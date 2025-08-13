
/// Facility의 정보를 나타내는 구조체입니다.
#[derive(Default, Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct FacilityInfo {
    #[serde(default)]
    pub id: u32,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub groups: Vec<u32>,
    #[serde(default)]
    pub protocol_type: String,
    #[serde(default)]
    pub facility_type: FacilityType,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub facility_sub_type: Option<String>,
    /// Facility의 운전 시간을 분 단위로 표현합니다.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub operation_minute: Option<u32>,
    /// Facility의 연속 운전 시간을 분 단위로 표현합니다.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub continuous_operation_minute: Option<u32>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub tags: Vec<String>,
    #[serde(default)]
    pub name: String,
    #[serde(default)]
    pub path: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub parent: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub parent_path: Option<String>,
    /// 시리얼 포트 인덱스 (1 ~ 4)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub serial_port: Option<u32>,
    #[serde(default)]
    #[serde(skip_serializing_if = "HashMap::is_empty")]
    pub cnis: HashMap<String, Option<String>>, // CNI Name, Value

    #[serde(default, skip_serializing_if = "is_false")]
    pub on_remote_sync: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub remote_sync: Option<FacilityRemoteSync>,

    /// [생성/수정 시]
    /// 신규 생성이 아니라, 업데이트하는 경우에는 아래 field를 true로 보낸다.
    /// 아래 field가 true면 이름 중복 체크를 하지 않는다.
    #[serde(default, skip_serializing_if = "is_false")]
    pub is_update: bool,

    /// Point의 확장정보
    /// - 첫 번째 Key: 확장 정보의 타입
    /// - 두 번째 key: 확장 정보의 키
    /// - value: 확장정보의 값
    #[serde(default, skip_serializing_if = "HashMap::is_empty")]
    pub extended_info: HashMap<String, Value>,

    // 설치시에는 사용하지 않는 필드
    #[serde(default)]
    pub status: FacilityStatus,
}

이런식으로 facilityinfo 가 정의되어있고, parent 가 지금 내가 확인하고자하는 odu address 일때만 idu를 count 하려고 하는데 이렇게 했는데 왜 안될까

     info!("*=====================unit_id: {}, current_page: {}=====================", self.unit_id, page);
        let pdi_enabled = config().read().pdi;
        //  실내기 개수를 카운트한다
        let facilities = data_manager::facility::get_list_by_type(
            &FacilityType::Physical("idu".to_string()),
        )
        .unwrap_or_default();
        // parent 가 self.address 와 일치하는 facility 만 센다.
        let facilities: Vec<_> = facilities
            .into_iter()
            .filter(|f| f.parent == Some(self.address() as u32))
            .collect();

        let idu_count = facilities.len() as u8;

        info!("PDI smart_flag: {}, IDU count: {}", pdi_enabled, idu_count);
