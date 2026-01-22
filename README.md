//! Point와 Facility에 대한 이력 정보를 나타내는 구조체입니다.
use std::str::FromStr;

use serde::{Deserialize, Serialize};

use crate::serde::DbusSerde;

use super::facility::FacilityStatus;

#[derive(Debug, Clone)]
pub struct HistoryParsingError(String);

impl std::fmt::Display for HistoryParsingError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Failed to parse history info: {}", self.0)
    }
}

impl std::error::Error for HistoryParsingError {}

/// 어떤 이벤트가 발생했는지를 나타냅니다.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub enum HistoryEvent {
    /// 제어기 장치의 생존 여부를 나타냅니다.
    /// 주기적으로 발생하는 이벤트로, 제어기 장치가 살아있음을 나타냅니다.
    /// 기본: 5분마다 발생
    Heartbeat,
    /// 장치의 설치가 완료되었을 때 발생합니다.
    Installed,
    /// 장치가 제거되었을 때 발생합니다.
    Removed,
    /// 실제 값이 변경되었을 때 발생합니다.
    /// ValueUpdated와는 다르게, 실제 Device에서 올려준 값을 그대로 기록합니다.
    RawValueChanged,
    /// 값이 제어되었을 때 발생합니다.
    ValueControlled,
    /// 값이 제어되었으나 실패했을 때 발생합니다.
    ValueControlFailed,
    /// 값이 업데이트되었을 때 발생합니다.
    ValueUpdated,
    /// 상태가 변경되었을 때 발생합니다.
    /// 정상 상태, 연결 에러 등의 상태 변경을 기록합니다.
    StatusChanged,
    /// 기타 이벤트가 발생했을 때 발생합니다.
    /// 예를 들어, 설정 정보가 변경되었을 때 발생합니다.
    /// 이 이벤트는 외부에서 정의될 수 있습니다. (e.g. 스케쥴 등록 등)
    #[serde(untagged)]
    Misc(String),
}

impl FromStr for HistoryEvent {
    type Err = HistoryParsingError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "heartbeat" => Ok(Self::Heartbeat),
            "installed" => Ok(Self::Installed),
            "removed" => Ok(Self::Removed),
            "raw_value_changed" | "rawvaluechanged" => Ok(Self::RawValueChanged),
            "value_controlled" | "valuecontrolled" => Ok(Self::ValueControlled),
            "value_control_failed" | "valuecontrolfailed" => Ok(Self::ValueControlFailed),
            "value_updated" | "valueupdated" => Ok(Self::ValueUpdated),
            "status_changed" | "statuschanged" => Ok(Self::StatusChanged),
            _ => {
                if s.is_empty() {
                    Err(HistoryParsingError(
                        "Event string cannot be empty".to_string(),
                    ))
                } else {
                    Ok(Self::Misc(s.to_string()))
                }
            }
        }
    }
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub enum HistoryEventFailedReason {
    Locked,
    OutOfRange,
    WriteRestricted,
    PriorityLow,
    Timeout,
    Unknown,
}

impl FromStr for HistoryEventFailedReason {
    type Err = HistoryParsingError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "locked" => Ok(Self::Locked),
            "out_of_range" | "outofrange" => Ok(Self::OutOfRange),
            "write_restricted" | "writerestricted" => Ok(Self::WriteRestricted),
            "priority_low" | "prioritylow" => Ok(Self::PriorityLow),
            "timeout" => Ok(Self::Timeout),
            _ => Err(HistoryParsingError(format!(
                "Invalid history event failed reason: {s}",
            ))),
        }
    }
}

/// 이력에 대한 기록의 집합입니다.
#[derive(Default, Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct HistoryInfo {
    /// 이력의 개수입니다.
    pub count: u32,
    /// 이력의 현재 Page입니다.
    pub page: u32,
    /// 이력의 전체 개수입니다.
    pub page_total: u32,
    /// 이력의 목록입니다.
    pub records: Vec<HistoryRecord>,
}

/// 각각 이력에 대한 기록을 나타냅니다.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct HistoryRecord {
    /// 이력이 발생한 시각입니다.
    /// Unix timestamp로 표현됩니다.
    pub timestamp: i64,
    /// 이력이 발생한 Point의 ID입니다.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub point_id: Option<u32>,
    /// 이력이 발생한 Facility의 ID입니다.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub facility_id: Option<u32>,
    /// 이력이 발생한 Facility Type입니다.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub facility_type: Option<String>,
    /// 이력이 발생한 Facility Name입니다.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub facility_name: Option<String>,
    /// 이력이 발생한 Facility의 주소입니다.
    /// LGAP, Modbus 장치에 한해서만 지원합니다.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub facility_address: Option<u32>,
    /// 소속 그룹
    /// NOTE: 하나의 장치는 복수개의 그룹에 속할 수 있습니다. 현재는 "ui" 그룹의 정보를 넘겨주도록
    /// 합니다. 추후 대표 그룹을 지정할 수 있는 기능이 추가될 필요가 있습니다.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub group_id: Option<u32>,
    /// 소속 그룹 이름
    /// NOTE: 하나의 장치는 복수개의 그룹에 속할 수 있습니다. 현재는 "ui" 그룹의 정보를 넘겨주도록
    /// 합니다. 추후 대표 그룹을 지정할 수 있는 기능이 추가될 필요가 있습니다.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub group_name: Option<String>,
    /// 이력이 발생한 이유가 되는 이벤트입니다.
    pub event: HistoryEvent,
    /// 제어/모니터링 관련 이벤트 발생시 기록되는 cni 항목입니다.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cni: Option<String>,
    /// 제어/모니터링 관련 이벤트 발생시 기록되는 cni_value 항목입니다.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cni_value: Option<String>,
    /// 제어/모니터링 관련 이벤트 발생시 기록되는 관제점의 value 입니다.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub value: Option<f32>,
    /// 제어/모니터링 관련 이벤트 발생시 기록되는 관제점의 state 입니다.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub state: Option<String>,
    /// 상태변경, 에러 등의 이벤트가 발생한 경우, 이전 상태를 기록합니다.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub status_from: Option<FacilityStatus>,
    /// 상태변경, 에러 등의 이벤트가 발생한 경우, 이전 상태를 기록합니다.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub status_to: Option<FacilityStatus>,
    /// 이력에 대한 상세 설명입니다.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub desc: Option<String>,
    /// 실패하는 경우에 실패 이유를 기록합니다.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub reason: Option<HistoryEventFailedReason>,
    /// 제어 주체가 있는 경우 기록합니다.
    pub affect: String,
}

impl DbusSerde for HistoryRecord {
    fn to_dbus_string(&self) -> crate::DbusJsonString {
        serde_json::to_string(self).unwrap_or_default()
    }

    fn from_dbus_string(
        json: crate::DbusJsonString,
    ) -> Result<Self, crate::serde::DeserializeError> {
        match serde_json::from_str(&json) {
            Ok(record) => Ok(record),
            Err(e) => Err(crate::serde::DeserializeError::new(e.to_string())),
        }
    }
}

/// 히스토리 결과를 제한하기 위해 사용되는 필터입니다.
#[derive(Default, Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct HistoryRecordFilter {
    /// 이력이 발생한 Point의 ID입니다.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub point_id: Vec<u32>,
    /// 이력이 발생한 Facility의 ID입니다.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub facility_id: Vec<u32>,
    /// 이력이 발생한 Facility Type입니다.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub facility_type: Vec<String>,
    /// 이력이 발생한 Facility Name입니다.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub facility_name: Vec<String>,
    /// cni 필드가 있는 경우 해당 값의 필터입니다..
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub cni: Vec<String>,
    /// Value 필드가 있는 경우 해당 값의 최소값입니다.
    pub value_min: Option<f32>,
    /// Value 필드가 있는 경우 해당 값의 최대값입니다.
    pub value_max: Option<f32>,
    /// 이력이 발생한 이벤트입니다.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub event: Vec<HistoryEvent>,
    /// 이벤트가 실패한 경우의 이유입니다.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub reason: Vec<HistoryEventFailedReason>,
    /// 이력의 개수를 제한합니다.
    pub count: Option<u32>,
    /// 이력의 Page 입니다.
    /// 0부터 시작하며, 한 페이지에는 count만큼의 이력이 포함됩니다.
    pub page: Option<u32>,
    /// 이력의 시작 시각입니다.
    pub timestamp_from: Option<i64>,
    /// 이력의 종료 시각입니다.
    pub timestamp_to: Option<i64>,
    /// 제어 주체가 있는 경우 기록합니다.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub affect: Vec<String>,
}

impl DbusSerde for HistoryRecordFilter {
    fn to_dbus_string(&self) -> crate::DbusJsonString {
        serde_json::to_string(self).unwrap_or_default()
    }

    fn from_dbus_string(
        json: crate::DbusJsonString,
    ) -> Result<Self, crate::serde::DeserializeError> {
        match serde_json::from_str(&json) {
            Ok(filter) => Ok(filter),
            Err(e) => Err(crate::serde::DeserializeError::new(e.to_string())),
        }
    }
}

/// 히스토리 결과의 메타 정보를 나타냅니다.
#[derive(Default, Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct HistoryRecordInfo {
    /// 이력의 개수입니다.
    pub count: u32,
    /// 이력의 현재 Page입니다.
    pub page: u32,
    /// 이력의 전체 개수입니다.
    pub page_total: u32,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_history_event_from_str() {
        assert_eq!(
            HistoryEvent::from_str("heartbeat").unwrap(),
            HistoryEvent::Heartbeat
        );
        assert_eq!(
            HistoryEvent::from_str("installed").unwrap(),
            HistoryEvent::Installed
        );
        assert_eq!(
            HistoryEvent::from_str("invalid").unwrap(),
            HistoryEvent::Misc("invalid".to_string())
        );
    }

    #[test]
    fn test_history_event_from_json() {
        let json = r#"{
            "timestamp": 1633072800,
            "point_id": 1,
            "facility_id": 2,
            "facility_type": "sensor",
            "facility_name": "Temperature Sensor",
            "facility_address": 100,
            "group_id": 10,
            "group_name": "Living Room",
            "event": "valueUpdated",
            "cni": "temperature",
            "cni_value": "25.5",
            "value": 25.5,
            "state": "normal",
            "status_from": null,
            "status_to": null,
            "desc": "Temperature updated",
            "reason": null,
            "affect": "user"
        }"#;

        let record: HistoryRecord = serde_json::from_str(json).unwrap();
        assert_eq!(record.event, HistoryEvent::ValueUpdated);

        let json = r#"{
            "timestamp": 1633072800,
            "point_id": 1,
            "facility_id": 2,
            "facility_type": "sensor",
            "facility_name": "Temperature Sensor",
            "facility_address": 100,
            "group_id": 10,
            "group_name": "Living Room",
            "event": "miscEvent",
            "cni": null,
            "cni_value": null,
            "value": null,
            "state": null,
            "status_from": null,
            "status_to": null,
            "desc": null,
            "reason": null,
            "affect": ""
        }"#;

        let record: HistoryRecord = serde_json::from_str(json).unwrap();
        assert_eq!(record.event, HistoryEvent::Misc("miscEvent".to_string()));
    }
}
