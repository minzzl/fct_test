pub(crate) async fn get_histories_csv(
        params: HistoryOptions,
        token: Option<String>,
    ) -> Result<impl warp::Reply, warp::Rejection> {
        if !access_control()
            .check_permission(token.as_deref(), Permission::GetHistory)
            .await
        {
            return Ok(Response::err("Permission denied".to_string()));
        }

        // Initialize variables for pagination
        let mut histories_records = vec![];

        // Fetch the total count of records first
        let initial_histories = match data_manager::history::get(params.clone().into()).await {
            Ok(histories) => histories,
            Err(e) => {
                error!("Failed to get histories: {e}");
                return Ok(Response::err(format!("Failed to get histories: {e}")));
            }
        };

        let total_count = initial_histories.count;

        // Check if total_count exceeds the limit
        if total_count > 20000 {
            return Ok(Response::err(
                "Cannot fetch more than 20000 records.".to_string(),
            ));
        }

        info!("Total count: {total_count}");

        // Calculate the number of pages needed based on params.count
        let count_per_page = params.count.unwrap_or(1000); // 기본값을 1000으로 설정
        let total_pages = total_count.div_ceil(count_per_page); // 올림 계산

        info!("Total pages: {total_pages}");

        // Loop to fetch records in batches
        for page in 0..total_pages {
            let mut paged_params = params.clone();
            paged_params.page = Some(page); // Set the current page

            let histories = match data_manager::history::get(paged_params.into()).await {
                Ok(histories) => histories,
                Err(e) => {
                    error!("Failed to get histories: {e}");
                    return Ok(Response::err(format!("Failed to get histories: {e}")));
                }
            };

            // If no more records are returned, break the loop
            if histories.records.is_empty() {
                break;
            }

            for record in histories.records {
                histories_records.push(record);
            }
        }

        // CSV 내보내기에만 사용할 struct와 impl
        #[derive(serde::Serialize)]
        struct CsvHistoryRecord {
            timestamp: i64,
            #[serde(rename = "facilityName")]
            facility_name: Option<String>,
            #[serde(rename = "facilityType")]
            facility_type: Option<String>,
            #[serde(rename = "facilityAddress")]
            facility_address: Option<u32>,
            #[serde(rename = "pointId")]
            point_id: Option<u32>,
            #[serde(rename = "facilityId")]
            facility_id: Option<u32>,
            #[serde(rename = "groupId")]
            group_id: Option<u32>,
            #[serde(rename = "groupName")]
            group_name: Option<String>,
            event: String,
            cni: Option<String>,
            #[serde(rename = "cniValue")]
            cni_value: Option<String>,
            value: Option<f32>,
            state: Option<String>,
            #[serde(rename = "statusFrom")]
            status_from: Option<String>,
            #[serde(rename = "statusTo")]
            status_to: Option<String>,
            desc: Option<String>,
            reason: Option<String>,
            affect: String,
        }
    
        impl From<&platform_common_types::core::history::HistoryRecord> for CsvHistoryRecord {
            fn from(hr: &platform_common_types::core::history::HistoryRecord) -> Self {
                // 소문자 시작 변환 함수
                fn first_lowercase(s: &str) -> String {
                    let mut c = s.chars();
                    match c.next() {
                        None => String::new(),
                        Some(f) => f.to_lowercase().collect::<String>() + c.as_str(),
                    }
                }
                // enum용 변환 함수 (Debug trait 이용)
                fn enum_to_lower_string<T: std::fmt::Debug>(e: &T) -> String {
                    first_lowercase(&format!("{:?}", e))
                }
    
                CsvHistoryRecord {
                    timestamp: hr.timestamp,
                    facility_name: hr.facility_name.clone(),
                    facility_type: hr.facility_type.clone(),
                    facility_address: hr.facility_address,
                    point_id: hr.point_id,
                    facility_id: hr.facility_id,
                    group_id: hr.group_id,
                    group_name: hr.group_name.clone(),
                    event: enum_to_lower_string(&hr.event),
                    cni: hr.cni.clone(),
                    cni_value: hr.cni_value.clone(),
                    value: hr.value,
                    state: hr.state.clone(),
                    status_from: hr.status_from.as_ref().map(enum_to_lower_string),
                    status_to: hr.status_to.as_ref().map(enum_to_lower_string),
                    desc: hr.desc.clone(),
                    reason: hr.reason.as_ref().map(|r| format!("{:?}", r)),
                    affect: hr.affect.clone(),
                }
            }
        }

        let mut wtr = WriterBuilder::new().from_writer(vec![]);
        for record in histories_records {
            if let Err(e) = wtr.serialize(CsvHistoryRecord::from(&record)) {
                error!("Failed to write record to CSV: {e}");
                return Ok(Response::err(format!("Failed to write record to CSV: {e}")));
            }
        }

        // CSV 데이터를 Vec<u8>로 가져오기
        let data = wtr.into_inner().map_err(|e| {
            error!("Failed to finalize CSV writer: {e}");
            warp::reject::not_found() // 적절한 오류 처리
        })?;

        // CSV 데이터를 String으로 변환
        let csv_data = String::from_utf8(data).map_err(|e| {
            error!("Failed to convert CSV data to String: {e}");
            warp::reject::not_found() // 적절한 오류 처리
        })?;

        // Create a filename based on the parameters
        let default_filename = "histories.csv".to_string();
        let filename = if let (Some(start_data), Some(end_data)) = (
            Utc.timestamp_opt(params.timestamp_from.unwrap_or(0), 0)
                .single(),
            Utc.timestamp_opt(params.timestamp_to.unwrap_or(0), 0)
                .single(),
        ) {
            let formatted_start_date = start_data.format("%Y-%m-%d").to_string();
            let formatted_end_date = end_data.format("%Y-%m-%d").to_string();
            format!(
                "histories_{}_{}.csv",
                formatted_start_date, formatted_end_date
            )
        } else {
            default_filename
        };

        // CSV 응답을 반환
        let response = Response::ok_with_csv(csv_data, filename);
        Ok(response)
    }

기존에 코드에서.. 2만 개 초과 시 최신 기준 2만 개만 추출하도록 수정하도록 요구를 받아서 그렇게 수정을 했어. 근데 ... 뭔가 바꾼코드의 부하가 큰 것 같아. 
이 코드에서는 2만개의 데이터 조회시에, 1000개씩 20회 조회해도 문제가 되지 않았는데 .. 왜지금 코드는 문제가 되는거지? 효율을 높일 수 있을까? 
아니면 기존 코드에서 gui 개발자한테 적절하게 api 요청시에 필터링을 걸어서 요청하라하고 기존의 코드를 유지행할까

pub(crate) async fn get_histories_csv(
        params: HistoryOptions,
        token: Option<String>,
    ) -> Result<impl warp::Reply, warp::Rejection> {
        if !access_control()
            .check_permission(token.as_deref(), Permission::GetHistory)
            .await
        {
            return Ok(Response::err("Permission denied".to_string()));
        }

        // 전체 레코드 개수 확인
        let initial_histories = match data_manager::history::get(params.clone().into()).await {
            Ok(histories) => histories,
            Err(e) => {
                error!("Failed to get histories: {e}");
                return Ok(Response::err(format!("Failed to get histories: {e}")));
            }
        };
        let total_count = initial_histories.count;

        let output_limit = 20_000;
        let count_per_page = params.count.unwrap_or(1000);

        // 최신 기준 2만개 페이징 계산
        let total_pages = total_count.div_ceil(count_per_page);
        let fetch_pages;
        let start_page;

        if total_count > output_limit {
            fetch_pages = output_limit.div_ceil(count_per_page);
            start_page = if total_pages > fetch_pages { total_pages - fetch_pages } else { 0 };
        } else {
            fetch_pages = total_pages;
            start_page = 0;
        }

        let mut histories_records = Vec::with_capacity(output_limit as usize);
        let mut exported = 0;
        for page in start_page..(start_page + fetch_pages) {
            let mut paged_params = params.clone();
            paged_params.page = Some(page);
            paged_params.count = Some(count_per_page);

            let histories = match data_manager::history::get(paged_params.into()).await {
                Ok(histories) => histories,
                Err(e) => {
                    error!("Failed to get histories: {e}");
                    return Ok(Response::err(format!("Failed to get histories: {e}")));
                }
            };

            // If no more records are returned, break the loop
            if histories.records.is_empty() {
                break;
            }

            for record in histories.records {
                histories_records.push(record);
                exported += 1;
                if exported >= output_limit {
                    break;
                }
            }
            if exported >= output_limit {
                break;
            }
        }

        // CSV 내보내기에만 사용할 struct와 impl
        #[derive(serde::Serialize)]
        struct CsvHistoryRecord {
            timestamp: i64,
            #[serde(rename = "facilityName")]
            facility_name: Option<String>,
            #[serde(rename = "facilityType")]
            facility_type: Option<String>,
            #[serde(rename = "facilityAddress")]
            facility_address: Option<u32>,
            #[serde(rename = "pointId")]
            point_id: Option<u32>,
            #[serde(rename = "facilityId")]
            facility_id: Option<u32>,
            #[serde(rename = "groupId")]
            group_id: Option<u32>,
            #[serde(rename = "groupName")]
            group_name: Option<String>,
            event: String,
            cni: Option<String>,
            #[serde(rename = "cniValue")]
            cni_value: Option<String>,
            value: Option<f32>,
            state: Option<String>,
            #[serde(rename = "statusFrom")]
            status_from: Option<String>,
            #[serde(rename = "statusTo")]
            status_to: Option<String>,
            desc: Option<String>,
            reason: Option<String>,
            affect: String,
        }
    
        impl From<&platform_common_types::core::history::HistoryRecord> for CsvHistoryRecord {
            fn from(hr: &platform_common_types::core::history::HistoryRecord) -> Self {
                // 소문자 시작 변환 함수
                fn first_lowercase(s: &str) -> String {
                    let mut c = s.chars();
                    match c.next() {
                        None => String::new(),
                        Some(f) => f.to_lowercase().collect::<String>() + c.as_str(),
                    }
                }
                // enum용 변환 함수 (Debug trait 이용)
                fn enum_to_lower_string<T: std::fmt::Debug>(e: &T) -> String {
                    first_lowercase(&format!("{:?}", e))
                }
    
                CsvHistoryRecord {
                    timestamp: hr.timestamp,
                    facility_name: hr.facility_name.clone(),
                    facility_type: hr.facility_type.clone(),
                    facility_address: hr.facility_address,
                    point_id: hr.point_id,
                    facility_id: hr.facility_id,
                    group_id: hr.group_id,
                    group_name: hr.group_name.clone(),
                    event: enum_to_lower_string(&hr.event),
                    cni: hr.cni.clone(),
                    cni_value: hr.cni_value.clone(),
                    value: hr.value,
                    state: hr.state.clone(),
                    status_from: hr.status_from.as_ref().map(enum_to_lower_string),
                    status_to: hr.status_to.as_ref().map(enum_to_lower_string),
                    desc: hr.desc.clone(),
                    reason: hr.reason.as_ref().map(|r| format!("{:?}", r)),
                    affect: hr.affect.clone(),
                }
            }
        }

        let mut wtr = WriterBuilder::new().from_writer(vec![]);
        for record in histories_records {
            if let Err(e) = wtr.serialize(CsvHistoryRecord::from(&record)) {
                error!("Failed to write record to CSV: {e}");
                return Ok(Response::err(format!("Failed to write record to CSV: {e}")));
            }
        }

        // CSV 데이터를 Vec<u8>로 가져오기
        let data = wtr.into_inner().map_err(|e| {
            error!("Failed to finalize CSV writer: {e}");
            warp::reject::not_found() // 적절한 오류 처리
        })?;

        // CSV 데이터를 String으로 변환
        let csv_data = String::from_utf8(data).map_err(|e| {
            error!("Failed to convert CSV data to String: {e}");
            warp::reject::not_found() // 적절한 오류 처리
        })?;

        // Create a filename based on the parameters
        let default_filename = "histories.csv".to_string();
        let filename = if let (Some(start_data), Some(end_data)) = (
            Utc.timestamp_opt(params.timestamp_from.unwrap_or(0), 0)
                .single(),
            Utc.timestamp_opt(params.timestamp_to.unwrap_or(0), 0)
                .single(),
        ) {
            let formatted_start_date = start_data.format("%Y-%m-%d").to_string();
            let formatted_end_date = end_data.format("%Y-%m-%d").to_string();
            format!(
                "histories_{}_{}.csv",
                formatted_start_date, formatted_end_date
            )
        } else {
            default_filename
        };

        // CSV 응답을 반환
        let response = Response::ok_with_csv(csv_data, filename);
        Ok(response)
    }
