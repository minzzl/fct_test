use warp::Filter;

use self::inner::types::HistoryOptions;
use super::ACP_HEADER_TOKEN;

/// 히스토리 조회
/// #[utoipa::path(
///     get,
///     path = "/api/v1/histories",
///     // params(ListQueryParams),
///     responses(
///         (status = 200, description = "List histories successfully", body = [HistoryRecord])
///         )
///     )]
pub(crate) fn get_histories(
) -> impl Filter<Extract = (impl warp::Reply,), Error = warp::Rejection> + Clone {
    warp::path!("histories")
        .and(warp::get())
        .and(warp::query::<HistoryOptions>())
        .and(warp::header::optional::<String>(ACP_HEADER_TOKEN))
        .and_then(inner::get_histories)
}

pub(crate) fn post_histories(
) -> impl Filter<Extract = (impl warp::Reply,), Error = warp::Rejection> + Clone {
    warp::path!("histories")
        .and(warp::post())
        .and(warp::header::optional::<String>(ACP_HEADER_TOKEN))
        .and(warp::body::json())
        .and_then(inner::post_histories)
}

pub(crate) fn get_histories_csv(
) -> impl Filter<Extract = (impl warp::Reply,), Error = warp::Rejection> + Clone {
    warp::path!("historiesCsv")
        .and(warp::get())
        .and(warp::query::<HistoryOptions>())
        .and(warp::header::optional::<String>(ACP_HEADER_TOKEN))
        .and_then(inner::get_histories_csv)
}

pub(crate) fn clear_histories(
) -> impl Filter<Extract = (impl warp::Reply,), Error = warp::Rejection> + Clone {
    warp::path!("histories")
        .and(warp::delete())
        .and(warp::header::optional::<String>(ACP_HEADER_TOKEN))
        .and_then(inner::clear_histories)
}

pub(super) mod inner {
    use crate::{permission::access_control, response::Response};
    use csv::WriterBuilder;
    use log::*;
    use platform_common_types::iam::Permission;
    use platform_ipc_helper::sync::data_manager;
    use types::{HistoryMiscEvent, HistoryOptions};

    use chrono::{TimeZone, Utc}; // Make sure to include the chrono crate for date handling

    pub(crate) async fn get_histories(
        params: HistoryOptions,
        token: Option<String>,
    ) -> Result<impl warp::Reply, warp::Rejection> {
        if !access_control()
            .check_permission(token.as_deref(), Permission::GetHistory)
            .await
        {
            return Ok(Response::err("Permission denied".to_string()));
        }

        let histories = match data_manager::history::get(params.into()).await {
            Ok(histories) => histories,
            Err(e) => {
                error!("Failed to get histories: {e}");
                return Ok(Response::err(format!("Failed to get histories: {e}")));
            }
        };

        #[derive(serde::Serialize)]
        #[serde(rename_all = "camelCase")]
        struct HistoryInfo {
            count: u32,
            page: u32,
            page_total: u32,
            histories: Vec<platform_common_types::core::history::HistoryRecord>,
        }

        let history_info = HistoryInfo {
            count: histories.count,
            page: histories.page,
            page_total: histories.page_total,
            histories: histories
                .records
                .into_iter()
                .map(|record| {
                    // EXP io의 경우 state를 보정하여 저장한다.
                    let cni_value = if record.facility_type == Some("expio".to_string()) {
                        match record.cni_value {
                            Some(val) => {
                                if matches!(
                                    val.as_str(),
                                    "on" | "start"
                                        | "warning"
                                        | "close"
                                        | "occupied"
                                        | "1"
                                        | "short"
                                ) {
                                    Some("1".to_string())
                                } else if matches!(
                                    val.as_str(),
                                    "off" | "stop" | "normal" | "open" | "unoccupied" | "0"
                                ) {
                                    Some("0".to_string())
                                } else {
                                    Some(val)
                                }
                            }
                            None => None,
                        }
                    } else {
                        record.cni_value
                    };
                    platform_common_types::core::history::HistoryRecord {
                        timestamp: record.timestamp,
                        facility_id: record.facility_id,
                        facility_name: record.facility_name,
                        facility_type: record.facility_type,
                        facility_address: record.facility_address,
                        point_id: record.point_id,
                        cni: record.cni,
                        cni_value,
                        value: record.value,
                        state: record.state,
                        status_from: record.status_from,
                        status_to: record.status_to,
                        desc: record.desc,
                        event: record.event,
                        reason: record.reason,
                        group_id: record.group_id,
                        group_name: record.group_name,
                        affect: record.affect,
                    }
                })
                .collect(),
        };

        Ok(Response::ok_with_data(
            serde_json::to_value(history_info).unwrap(),
        ))
    }

    pub(crate) async fn post_histories(
        token: Option<String>,
        payload: HistoryMiscEvent,
    ) -> Result<impl warp::Reply, warp::Rejection> {
        if !access_control()
            .check_permission(token.as_deref(), Permission::GetHistory)
            .await
        {
            return Ok(Response::err("Permission denied".to_string()));
        }

        let affect = access_control().get_id(&token.unwrap_or_default()).await;
        match data_manager::history::set(
            payload.event.as_str(),
            payload.desc.unwrap_or_default().as_str(),
            payload.facility_id,
            payload.group_id,
            payload.affect.unwrap_or(affect).as_str(),
        )
        .await
        {
            Ok(_) => Ok(Response::ok()),
            Err(e) => {
                error!("Failed to set history: {}", e);
                Ok(Response::err(e.to_string()))
            }
        }
    }

    pub(crate) async fn clear_histories(
        token: Option<String>,
    ) -> Result<impl warp::Reply, warp::Rejection> {
        if !access_control()
            .check_permission(token.as_deref(), Permission::GetHistory)
            .await
        {
            return Ok(Response::err("Permission denied".to_string()));
        }

        let url = "luna://com.b2b.dataManager.service/clear";

        match moonlight::sync::call(url, "{}").await {
            Ok(_) => Ok(Response::ok()),
            Err(e) => {
                error!("Failed to clear histories: {}", e);
                Ok(Response::err(e.to_string()))
            }
        }
    }

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

        // Fetch the total count of records first (count는 filename/로그 등에 필요할 수 있어 유지)
        let initial_histories = match data_manager::history::get(params.clone().into()).await {
            Ok(histories) => histories,
            Err(e) => {
                error!("Failed to get histories: {e}");
                return Ok(Response::err(format!("Failed to get histories: {e}")));
            }
        };

        let total_count = initial_histories.count;
        // 출력 상한 (요구사항: 2만개 초과 시 최신 기준 2만개만)
        let output_limit: usize = 20_000;

        // count_per_page: 내부 get_record에서 1000 초과는 1000으로 강제되므로 여기서도 clamp
        let mut count_per_page = params.count.unwrap_or(1000);
        if count_per_page > 1000 {
            count_per_page = 1000;
        }
        if count_per_page == 0 {
            count_per_page = 1000;
        }
        // 최신 기준 2만개면 page 0부터 최대 output_limit까지만 가져오면 됨
        // total_count 기반 total_pages 계산 대신, output_limit 기준으로 최대 요청 페이지 수를 계산해 offset 폭주 방지
        let max_pages = (output_limit as u32).div_ceil(count_per_page);
        // Loop to fetch records in batches (always from page 0)
        let mut exported: usize = 0;
        for page in 0..max_pages {
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

    pub(super) mod types {
        use std::str::FromStr;

        use log::*;
        use platform_common_types::core::history::{
            HistoryEvent, HistoryEventFailedReason, HistoryRecordFilter,
        };
        use serde::Deserialize;

        #[derive(Default, Debug, Deserialize, Clone)]
        #[serde(rename_all = "camelCase")]
        pub struct HistoryOptions {
            #[serde(default)]
            pub cni: String,
            #[serde(default)]
            pub point_id: String,
            #[serde(default)]
            pub facility_id: String,
            #[serde(default)]
            pub facility_type: String,
            #[serde(default)]
            pub facility_name: String,
            #[serde(default)]
            pub event: String,
            #[serde(default)]
            pub reason: String,
            pub count: Option<u32>,
            pub page: Option<u32>,
            pub timestamp_from: Option<i64>,
            pub timestamp_to: Option<i64>,
            pub today: Option<bool>,
            #[serde(default)]
            pub affect: String,
        }

        impl From<HistoryOptions> for HistoryRecordFilter {
            fn from(options: HistoryOptions) -> Self {
                let facility_id = options
                    .facility_id
                    .split(',')
                    .filter_map(|s| s.parse().ok())
                    .collect();
                let point_id = options
                    .point_id
                    .split(',')
                    .filter_map(|s| s.parse().ok())
                    .collect();
                let facility_type = options
                    .facility_type
                    .split(',')
                    .filter_map(|s| {
                        if s.is_empty() {
                            None
                        } else {
                            Some(s.to_string())
                        }
                    })
                    .collect();
                let facility_name = options
                    .facility_name
                    .split(',')
                    .filter_map(|s| {
                        if s.is_empty() {
                            None
                        } else {
                            Some(s.to_string())
                        }
                    })
                    .collect();
                let cni = options
                    .cni
                    .split(',')
                    .filter_map(|s| {
                        if s.is_empty() {
                            None
                        } else {
                            Some(s.to_string())
                        }
                    })
                    .collect();
                let event = if options.event.is_empty() {
                    // 이벤트를 설정 안했다면, 아래 이벤트들을 기본으로 필터링한다.
                    vec![
                        HistoryEvent::ValueControlled,
                        HistoryEvent::ValueUpdated,
                        HistoryEvent::ValueControlFailed,
                        HistoryEvent::StatusChanged,
                        HistoryEvent::Misc("setting".to_string()),
                    ]
                } else {
                    options
                        .event
                        .split(',')
                        .filter_map(|event| match HistoryEvent::from_str(event) {
                            Ok(event) => Some(event),
                            Err(_) => {
                                warn!("Invalid event filter");
                                None
                            }
                        })
                        .collect()
                };
                let reason = options
                    .reason
                    .split(',')
                    .filter_map(|reason| match HistoryEventFailedReason::from_str(reason) {
                        Ok(reason) => Some(reason),
                        Err(_) => {
                            warn!("Invalid reason filter");
                            None
                        }
                    })
                    .collect();
                let count = options.count;
                let page = options.page;

                let mut timestamp_from = options.timestamp_from;
                let mut timestamp_to = options.timestamp_to;

                if let Some(today) = options.today {
                    if timestamp_from.is_some() || timestamp_to.is_some() {
                        warn!("Both 'today' and 'timestampFrom'/'timestampTo' are set. 'today' will be ignored.");
                    } else if today {
                        let now = chrono::Local::now();
                        let start_of_day = now
                            .date_naive()
                            .and_hms_opt(0, 0, 0)
                            .unwrap()
                            .and_local_timezone(chrono::Local)
                            .unwrap()
                            .timestamp();
                        let end_of_day = now
                            .date_naive()
                            .and_hms_opt(23, 59, 59)
                            .unwrap()
                            .and_local_timezone(chrono::Local)
                            .unwrap()
                            .timestamp();
                        timestamp_from = Some(start_of_day);
                        timestamp_to = Some(end_of_day);
                    }
                }

                let affect = options
                    .affect
                    .split(',')
                    .filter_map(|s| {
                        if s.is_empty() {
                            None
                        } else {
                            Some(s.to_string())
                        }
                    })
                    .collect();

                Self {
                    point_id,
                    facility_id,
                    facility_type,
                    facility_name,
                    cni,
                    value_min: None,
                    value_max: None,
                    event,
                    reason,
                    count,
                    page,
                    timestamp_from,
                    timestamp_to,
                    affect,
                }
            }
        }

        #[derive(Debug, Deserialize)]
        #[serde(rename_all = "camelCase")]
        pub struct HistoryMiscEvent {
            pub facility_id: Option<u32>,
            pub group_id: Option<u32>,
            pub event: String,
            pub desc: Option<String>,
            pub affect: Option<String>,
        }
    }
}

이렇게 되어있는데 ... 아래와 같이 요청이 왔어 


historiesCsv API 수정 요청드립니다.
event: "setting"일 때 histories API와 historiesCsv API에서 전달주는 값이 서로 다릅니다
histories API와 동일하게 설정 부탁드립니다!
 
현재 들어오는 값 첨부 드립니다
Plain Text
histories API
{"affect":"ACPi","desc":"facility","event":"setting","timestamp":1781327899}
historiesCsv API
1781327899,,,,,,,,"misc(""setting"")",,,,,,,facility,,ACPi

get_histories_csv 에서

왜 setting관련한 내용만 이런식으로 될까
get_histories 동일한 방식으로 모든 값들을 처리하되, csv 로 추출할 수 있도록 코드 짰다고 생각했는데 보완해야할 부분이 있을까 그리고 사실 setting만 이런건지 또 다른경우에 문제가 생길수 있는건지 가늠이 안돼

추가: 또 다른 경우에도 유사 문제 발생을 고려하는 경우를 위해서 어떻게 코드를 짜는게 좋을까 
