/// 저장된 History를 'count'만큼 불러옵니다. 가장 최신의 History부터 불러옵니다.
    pub fn get_record(&mut self, filter: &HistoryFilter) -> Result<HistoryInfo> {
        // count가 설정되지 않았을 때는 200개로 설정합니다.
        // 시스템에 과도한 부하를 방지하기 위함입니다.
        let mut count = filter.count.unwrap_or(1000);
        if count > 1000 {
            warn!("Count is over 1000. Set count to 1000.");
            count = 1000;
        }
        let page = filter.page.unwrap_or(0);

        let histories = mem::take(&mut self.histories);
        if !histories.is_empty() {
            let histories: Vec<HistoryRecord> = histories
                .into_iter()
                .filter_map(|h| match HistoryRecord::try_from(h) {
                    Ok(record) => Some(record),
                    Err(e) => {
                        error!("Failed to convert History to HistoryRecord: {e}");
                        None
                    }
                })
                .collect();

            if let Err(e) = db::save_histories(&histories) {
                error!("Failed to save histories: {e}");
            }
        }
        self.clear_cached();

        // NOTE: 직접 메모리 상에서 조회하는 것 없이 모두 DB에서 조회합니다.
        let mut complex_queries = ComplexQueries {
            query_type: QueryType::And,
            queries: vec![],
        };

        let mut queries = Queries {
            query_type: QueryType::And,
            queries: vec![],
        };

        if let Some(timestamp) = filter.timestamp {
            queries.queries.push(Query {
                prop: "timestamp".to_string(),
                op: ">=".parse().unwrap(),
                value: timestamp.time_from.unwrap_or(0).into(),
            });
            queries.queries.push(Query {
                prop: "timestamp".to_string(),
                op: "<=".parse().unwrap(),
                value: timestamp.time_to.unwrap_or(i64::MAX).into(),
            });
        }
        complex_queries.queries.push(queries);

        let mut queries = Queries {
            query_type: QueryType::Or,
            queries: vec![],
        };

        for event in &filter.event {
            let event = match serde_json::to_value(event) {
                Ok(event) => event,
                Err(e) => {
                    error!("Failed to serialize event: {e}");
                    continue;
                }
            };

            queries.queries.push(Query {
                prop: "event".to_string(),
                op: "=".parse().unwrap(),
                value: event,
            });
        }
        complex_queries.queries.push(queries);

        let mut queries = Queries {
            query_type: QueryType::Or,
            queries: vec![],
        };

        for id in &filter.facility_id {
            queries.queries.push(Query {
                prop: "facilityId".to_string(),
                op: "=".parse().unwrap(),
                value: id.facility.into(),
            });
        }
        complex_queries.queries.push(queries);

        let mut queries = Queries {
            query_type: QueryType::Or,
            queries: vec![],
        };

        for facility_type in &filter.facility_type {
            queries.queries.push(Query {
                prop: "facilityType".to_string(),
                op: "=".parse().unwrap(),
                value: facility_type.as_str().into(),
            });
        }
        complex_queries.queries.push(queries);

        let mut queries = Queries {
            query_type: QueryType::Or,
            queries: vec![],
        };

        for facility_name in &filter.facility_name {
            queries.queries.push(Query {
                prop: "facilityName".to_string(),
                op: "=".parse().unwrap(),
                value: facility_name.as_str().into(),
            });
        }
        complex_queries.queries.push(queries);

        let mut queries = Queries {
            query_type: QueryType::Or,
            queries: vec![],
        };

        for cni in &filter.cni {
            queries.queries.push(Query {
                prop: "cni".to_string(),
                op: "=".parse().unwrap(),
                value: cni.as_str().into(),
            });
        }
        complex_queries.queries.push(queries);

        let mut queries = Queries {
            query_type: QueryType::Or,
            queries: vec![],
        };

        for id in &filter.point_id {
            queries.queries.push(Query {
                prop: "pointId".to_string(),
                op: "=".parse().unwrap(),
                value: id.point.into(),
            });
        }
        complex_queries.queries.push(queries);

        let mut queries = Queries {
            query_type: QueryType::Or,
            queries: vec![],
        };

        if let Some(value) = &filter.value {
            if let Some(from) = value.value_from {
                queries.queries.push(Query {
                    prop: "value".to_string(),
                    op: ">=".parse().unwrap(),
                    value: from.into(),
                });
            }
            if let Some(to) = value.value_to {
                queries.queries.push(Query {
                    prop: "value".to_string(),
                    op: "<=".parse().unwrap(),
                    value: to.into(),
                });
            }
        }
        complex_queries.queries.push(queries);

        let mut queries = Queries {
            query_type: QueryType::Or,
            queries: vec![],
        };
        for reason in &filter.reason {
            let reason = match serde_json::to_value(reason) {
                Ok(reason) => reason,
                Err(e) => {
                    error!("Failed to serialize reason: {e}");
                    continue;
                }
            };

            queries.queries.push(Query {
                prop: "reason".to_string(),
                op: "=".parse().unwrap(),
                value: reason,
            });
        }
        complex_queries.queries.push(queries);

        let mut queries = Queries {
            query_type: QueryType::Or,
            queries: vec![],
        };

        for affect in &filter.affect {
            queries.queries.push(Query {
                prop: "affect".to_string(),
                op: "=".parse().unwrap(),
                value: affect.as_str().into(),
            });
        }
        complex_queries.queries.push(queries);

        let pagination = Pagination {
            limit: count,
            page,
            reverse: true,
            sort_key: Some("timestamp".to_string()),
        };

        match db::load_histories(complex_queries, pagination) {
            Ok(info) => Ok(info),
            Err(e) => {
                error!("Failed to load histories: {e}");
                Err(e)
            }
        }
    }
}



내부적으로는 해당 함수를 써.
