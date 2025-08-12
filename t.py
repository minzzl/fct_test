use anyhow::{anyhow, Result};
use bytes::{Buf, BufMut, Bytes, BytesMut};
use log::*;
use platform_common_types::core::{FacilityType, Status};
use platform_ipc_helper::blocking::data_manager;

use crate::{
    ad_table::{
        get_airtemp, get_dischargetemp, get_high_pressure_r410a, get_pipetemp, get_suctiontemp,
    },
    config::config,
    connection_checker::ConnectionChecker,
    data::{data_table, DataSets},
    device::{DeviceInfo, DeviceType, LgapCodec, LgapDevice, NeedSchedule, SubOduType},
    fota::Fotable,
};

#[derive(Debug, Clone)]
pub struct Super5 {
    /// 연결된 serial port
    /// 만약 serial port가 0이면 검색 모드로 동작함
    /// 매 턴마다 시리얼 포트가 설정되었는지를 확인하고, 설정되었으면 weight를 0으로 설정하여
    /// 동작하지 않도록 한다.
    port: u8,

    /// searching이 진행되는 포트 설정
    searching_port: u8,

    /// product code
    product_code: u8,

    /// odu_addr
    odu_addr: u8,

    /// 부모 odu id
    odu_id: u32,

    /// 1, 2, 3, 4
    unit_id: u8,

    /// current page
    current_page: u8,

    /// Version
    major: u8,
    minor: u8,
    patch: u8,

    /// default weight은 기본 weight이고,
    /// weight은 cycle데이터 수신 시 여러 page에서 데이터를 받을 때 사용하는 weight이다.
    weight: u32,
    default_weight: u32,

    /// 장치가 다른 포트에 설정되었으면, 본 객체를 unused 처리한다.
    is_unused: bool,

    // 연결 끊김 여부를 체크하는 객체
    connection_checker: ConnectionChecker,

    // 마지막 에러 상태
    // 장치의 상태를 업데이트 하기 위해서 기억
    last_error: u8,
}

impl Super5 {
    pub fn new(facility_id: u32, odu_id: u32, addr: u32, unit_id: u32) -> Result<Self> {
        data_table().write().register_unit(
            DeviceType::OduUnit,
            addr as u8,
            unit_id as u8,
            facility_id,
        )?;

        let connection_checker = ConnectionChecker::new(odu_id);

        let page = if unit_id == 1 { 0 } else { unit_id };

        Ok(Self {
            port: 0,
            searching_port: 0,
            product_code: 0xC0,
            odu_addr: addr as u8,
            odu_id,
            unit_id: unit_id as u8,
            current_page: page as u8,
            major: 0,
            minor: 0,
            patch: 0,
            weight: 10,
            default_weight: 10,
            is_unused: false,
            connection_checker,
            last_error: 0,
        })
    }

    /// 포트가 0번이면, 포트를 찾기 위한 검색 모드로 동작함
    fn is_searching_mode(&self) -> bool {
        self.port == 0
    }

    /// 시리얼 포트가 설정되었는지 확인
    /// 다른 포트에서 설정된 포트가 있는지 확인하고, 설정된 포트가 있으면 true를 반환
    fn set_searching_mode_done(&mut self) -> bool {
        if !self.is_searching_mode() {
            return true;
        }

        let port = match data_manager::facility::get_serial_port(self.odu_id) {
            Ok(port) => port,
            Err(e) => {
                error!("Failed to get serial port: {e}");
                return false;
            }
        };

        if let Some(port) = port {
            // 포트가 설정되었으면, 검색 모드 종료
            if self.searching_port != port as u8 {
                // 내 포트와 설정된 포트가 다르면 weight를 0으로 설정해서 통신이 안되도록 함
                self.weight = 0;
                // 스케쥴링에서 제외
                self.is_unused = true;
            } else {
                // 포트가 설정되었으면, 기본 포트를 설정
                self.port = port as u8;
            }
            true
        } else {
            // 포트가 설정되지 않았으면, 검색 모드 유지
            false
        }
    }

    fn encode_cmde(&mut self) -> Bytes {
        let mut bytes = BytesMut::new();

        // 연결 끊김 체크
        if !self.connection_checker.check_connection() {
            if let Err(e) = data_table()
                .write()
                .set(DeviceType::Odu, self.address(), "err", 242.0)
            {
                error!("Failed to set err: {e}");
            }
            data_table()
                .write()
                .flush(DeviceType::Odu, self.address(), None);
            self.last_error = 242;
        }

        // 부모 ODU의 데이터를 가져온다.
        let data_sets = data_table()
            .read()
            .gets(DeviceType::Odu, self.address())
            .unwrap_or_default();

        info!("Super5 encode_cmde: odu_id: {}, addr: {}, unit_id: {}, current_page: {}, port: {}",
        self.odu_id, self.address(), self.unit_id, self.current_page, self.port);

        // byte 0
        let is_master = 1;
        let cmdcode = 0xe;
        let protocol_version = 0;
        let byte0 = is_master << 7 | cmdcode << 3 | protocol_version;
        bytes.put_u8(byte0);

        // byte 1
        let byte1 = self.product_code;
        bytes.put_u8(byte1);

        // byte 2
        let byte2 = 0xA0;
        bytes.put_u8(byte2);

        // byte 3
        let byte3 = self.odu_addr;
        bytes.put_u8(byte3);

        // byte 4
        let page = self.current_page;
        
        info!("*=====================unit_id: {}, current_page: {}=====================", self.unit_id, page);
        let smart_flag = data_sets.get("smart_plug_enable") as f32;
        //  실내기 개수를 카운트한다
        let facilities = data_manager::facility::get_list_by_type(
            &FacilityType::Physical("idu".to_string()),
        )
        .unwrap_or_default();
        let idu_count = facilities.len() as u8;

        info!("PDI smart_flag: {}, IDU count: {}", smart_flag, idu_count);

        match page {
            0 | 2 | 3 | 4 => {
                // 0x0, 0x2, 0x3, 0x4
                self.current_page = if self.unit_id == 1 { 0 } else { self.unit_id } + 10;
                self.weight = 9999; // 무조건 다음 page에 대한 정보를 받기 위해 weight를 최대로 설정
            }
            10 | 12 | 13 | 14 => {
                self.current_page = if self.unit_id == 1 { 0 } else { self.unit_id } + 0x20;
                self.weight = 9999; // 무조건 다음 page에 대한 정보를 받기 위해 weight를 최대로 설정
            }
            0x20 | 0x22 | 0x23 | 0x24 => {
                // smart flag 가 켜져 있으면 0x38대로 진입하여 IDU 목록 페이지들을 순회
                if smart_flag == 1.0 && idu_count > 0 {
                    self.current_page = 0x38;              // 첫 PDI 페이지로
                    self.weight = 9999;
                } else {
                    //smart flag  끔 or IDU 없음 → 기존대로 0x40
                    self.current_page = if self.unit_id == 1 { 0 } else { self.unit_id } + 0x40;
                    self.weight = 9999;
                }
            }
            // ★ 추가: 0x38~0x3C 순회
            0x38 | 0x39 | 0x3A | 0x3B | 0x3C => {
                if smart_flag == 1.0 && idu_count > 0 {
                    // 페이지별 수용량 (누적 상한)
                    // 0x38: 13, 0x39: 26, 0x3A: 39, 0x3B: 52, 0x3C: 64(마지막은 12로 총 64)
                    let required_last_page = match idu_count {
                        0..=13   => 0x38,
                        14..=26  => 0x39,
                        27..=39  => 0x3A,
                        40..=52  => 0x3B,
                        _        => 0x3C,
                    };
                    if page < required_last_page {
                        self.current_page = page + 1;      // 다음 페이지 계속
                        self.weight = 9999;
                    } else {
                        // 필요한 페이지 다 보냈음 → 0x40대로 이동
                        self.current_page = if self.unit_id == 1 { 0 } else { self.unit_id } + 0x40;
                        self.weight = 9999;
                    }
                } else {
                    // smart flag  꺼짐/IDU 0 → 0x40대로
                    self.current_page = if self.unit_id == 1 { 0 } else { self.unit_id } + 0x40;
                    self.weight = 9999;
                }
            }
         
            0x40 | 0x42 | 0x43 | 0x44 => {
                self.current_page = if self.unit_id == 1 { 0 } else { self.unit_id };
            }
            _ => {
                self.current_page = if self.unit_id == 1 { 0 } else { self.unit_id };
            }
        };
        let byte4 = page;
        bytes.put_u8(byte4);

        // byte 5
        let index = 0x00;
        let byte5 = index;
        bytes.put_u8(byte5);

        // byte 6
        let (oil_return, oil_return_exe) = if self.unit_id == 1 && page == 0x0 {
            // unit_id가 1이고 page가 0x0인 경우에만 oil_return을 실행
            let oil_return = data_sets.get("oil_return");
            let oil_return_exe =
                data_table()
                    .read()
                    .is_field_dirty(DeviceType::Odu, self.address(), "oil_return")
                    as u8;
            (oil_return as u8, oil_return_exe)
        } else {
            (0, 0)
        };
        let byte6 = oil_return << 1 | oil_return_exe;
        bytes.put_u8(byte6);

        // byte 7
        let checksum = bytes.iter().map(|x| *x as u32).sum::<u32>() ^ 0x55;
        let checksum = (checksum & 0xff) as u8;
        let byte6 = checksum;
        bytes.put_u8(byte6);

        bytes.freeze()
    }

    pub fn decode_super5(&mut self, bytes: Bytes) -> Result<()> {
        let page = match bytes.get(5) {
            Some(byte) => *byte,
            None => return Err(anyhow!("Invalid super5 page")),
        };

        // NOTE: 타입 체크는 프로토콜 상 모든 페이지에서 동일하게 제공하지만,
        // 실제 실외기에서는 page 0x0, 0x2, 0x3, 0x4에서만 제공된다.
        if page == 0x0 || page == 0x2 || page == 0x3 || page == 0x4 {
            let odu_type_upper = match bytes.get(6) {
                Some(byte) => *byte & 0x0f,
                None => return Err(anyhow!("Invalid super5 type")),
            };

            let odu_type_pre = match odu_type_upper {
                0 => "HP_".to_string(),
                1 => "CO_".to_string(),
                2 => "SYNC_".to_string(),
                _ => format!("NONE[{}]_", odu_type_upper),
            };

            let odu_type_lower = match bytes.get(7) {
                Some(byte) => *byte,
                None => return Err(anyhow!("Invalid super5 type")),
            };
            let odu_type = odu_type_lower;
            let odu_type: SubOduType = odu_type.try_into()?;
            // if odu_type != SubOduType::Super5 {
            //     return Err(anyhow!("Invalid super5 type"));
            // }

            let odu_type = format!("{}{}", odu_type_pre, odu_type);
            if let Err(e) = data_table().write().set_text_unit(
                DeviceType::OduUnit,
                self.address(),
                self.unit_id(),
                "type",
                &odu_type,
            ) {
                error!("Failed to set type: {e}");
            }
        }

        match page {
            0 | 2 | 3 | 4 => self.decode_super5_page0234(bytes),
            10 | 12 | 13 | 14 => self.decode_super5_page10to14(bytes),
            0x20 | 0x22 | 0x23 | 0x24 => self.decode_super5_page20to24(bytes),
            0x40 | 0x42 | 0x43 | 0x44 => self.decode_super5_page40to44(bytes),
            0x38 | 0x39 | 0x3A | 0x3B | 0x3C => self.decode_super5_page38to3c(bytes),
            _ => Err(anyhow!("Invalid super5 page: {}", page)),
        }
    }

    fn decode_super5_page0234(&mut self, bytes: Bytes) -> Result<()> {
        let mut bytes = bytes;
        let check_bytes = bytes.clone();

        let byte0 = bytes.get_u8();
        let length = byte0 & 0x7F;
        if length != 0x40 {
            return Err(anyhow!(
                "ODU super5 page0234 decode: invalid length: {length}"
            ));
        }

        if bytes.remaining() < length as usize - 1 {
            return Err(anyhow!("ODU super5 page0234 decode: invalid length"));
        }

        let byte1 = bytes.get_u8();
        let cmd = (byte1 >> 3) & 0x0F;
        if cmd != 0xe {
            return Err(anyhow!("ODU super5 page0234 decode: invalid cmd: {cmd}"));
        }

        let byte2 = bytes.get_u8();
        let byte3 = bytes.get_u8();
        let byte4 = bytes.get_u8();
        let byte5 = bytes.get_u8();
        let byte6 = bytes.get_u8();
        let byte7 = bytes.get_u8();
        let byte8 = bytes.get_u8();
        let byte9 = bytes.get_u8();
        let byte10 = bytes.get_u8();
        let byte11 = bytes.get_u8();
        let byte12 = bytes.get_u8();
        let byte13 = bytes.get_u8();
        let byte14 = bytes.get_u8();
        let byte15 = bytes.get_u8();
        let byte16 = bytes.get_u8();
        let byte17 = bytes.get_u8();
        let byte18 = bytes.get_u8();
        let byte19 = bytes.get_u8();
        let byte20 = bytes.get_u8();
        let byte21 = bytes.get_u8();
        let byte22 = bytes.get_u8();
        let byte23 = bytes.get_u8();
        let byte24 = bytes.get_u8();
        let byte25 = bytes.get_u8();
        let byte26 = bytes.get_u8();
        let byte27 = bytes.get_u8();
        let byte28 = bytes.get_u8();
        let byte29 = bytes.get_u8();
        let byte30 = bytes.get_u8();
        let byte31 = bytes.get_u8();
        let byte32 = bytes.get_u8();
        let byte33 = bytes.get_u8();
        let byte34 = bytes.get_u8();
        let byte35 = bytes.get_u8();
        let byte36 = bytes.get_u8();
        let byte37 = bytes.get_u8();
        let byte38 = bytes.get_u8();
        let byte39 = bytes.get_u8();
        let byte40 = bytes.get_u8();
        let byte41 = bytes.get_u8();
        let byte42 = bytes.get_u8();
        let byte43 = bytes.get_u8();
        let byte44 = bytes.get_u8();
        let byte45 = bytes.get_u8();
        let byte46 = bytes.get_u8();
        let byte47 = bytes.get_u8();
        let byte48 = bytes.get_u8();
        let byte49 = bytes.get_u8();
        let byte50 = bytes.get_u8();
        let byte51 = bytes.get_u8();
        let byte52 = bytes.get_u8();
        let byte53 = bytes.get_u8();
        let byte54 = bytes.get_u8();
        let byte55 = bytes.get_u8();
        let byte56 = bytes.get_u8();
        let byte57 = bytes.get_u8();
        let byte58 = bytes.get_u8();
        let byte59 = bytes.get_u8();
        let byte60 = bytes.get_u8();
        let byte61 = bytes.get_u8();
        let byte62 = bytes.get_u8();
        let byte63 = bytes.get_u8();

        // byte 63
        let checksum = byte63;
        let expected_checksum = {
            let mut sum: u32 = 0;
            for byte in check_bytes[0..63].iter() {
                sum += *byte as u32;
            }
            ((sum ^ 0x55) & 0xff) as u8
        };

        self.connection_checker.reset_disconnect_count();
        let mut data_sets = DataSets::default();

        if checksum != expected_checksum {
            return Err(anyhow!(
                "ODU CmdE super5 checksum error: {checksum} != {expected_checksum}"
            ));
        }

        // byte 2
        let recv_product_code = byte2;
        if !(0xa0..=0xaf).contains(&recv_product_code) {
            return Err(anyhow!("This msg is not for ACP"));
        }

        // byte 3
        let product_code = byte3;
        if !(0xc0..=0xcf).contains(&product_code) {
            return Err(anyhow!(
                "ODU CmdE super5 product code error: {product_code}"
            ));
        }
        self.product_code = product_code;

        // byte 4
        let addr = byte4;
        if addr != self.odu_addr {
            return Err(anyhow!("ODU CmdE super5 addr error: {addr}"));
        }

        // byte 5
        let _page = byte5;

        // byte 6
        let ref_type = (byte6 >> 6) & 0x03;
        data_sets.set("refrigerant", ref_type as f32);
        let sync_status = (byte6 >> 4) & 0x03;
        let text = match sync_status {
            0b00 => "OFF",
            0b01 => "ON",
            0b10 => "SUCCESS",
            0b11 => "FAIL",
            _ => "UNKNOWN",
        };

        if let Err(e) = data_table().write().set_text_unit(
            DeviceType::OduUnit,
            self.address(),
            self.unit_id(),
            "sync_status",
            text,
        ) {
            error!("Failed to set sync_status: {e}");
        }

        // byte 7
        let _odu_type = byte7;

        // byte 8
        let micom_ver_major = byte8;
        self.major = micom_ver_major;

        // byte 9
        let micom_ver_minor = byte9;
        self.minor = micom_ver_minor;
        if let Err(e) = data_table().write().set_text_unit(
            DeviceType::OduUnit,
            self.address(),
            self.unit_id(),
            "micom_ver",
            &format!("{}.{}.{}", micom_ver_major, micom_ver_minor, self.patch),
        ) {
            error!("Failed to set micom_ver: {e}");
        }

        // byte 10
        let err = byte10;
        data_sets.set("error", err as f32);
        if self.last_error != err {
            #[allow(clippy::collapsible_else_if)]
            if err != 0 {
                if let Err(e) =
                    data_manager::facility::set_status(self.odu_id, Status::MiscError(err as i32))
                {
                    error!("Failed to set status: {e}");
                }
            } else {
                if let Err(e) = data_manager::facility::set_status(self.odu_id, Status::Normal) {
                    error!("Failed to set status: {e}");
                }
            }

            self.last_error = err;
        }

        // byte 11
        let target_high_pressure = byte11;
        let target_high_pressure = get_high_pressure_r410a(target_high_pressure)?;
        data_sets.set("target_high_pressure", target_high_pressure as f32);

        // byte 12
        let target_low_pressure = byte12;
        let target_low_pressure = get_high_pressure_r410a(target_low_pressure)?;
        data_sets.set("target_low_pressure", target_low_pressure as f32);

        // byte 13
        let target_super_heat = byte13 as f32 / 10.0;
        data_sets.set("target_super_heat", target_super_heat);

        // byte 14
        let target_sub_cool = byte14 as f32 / 10.0;
        data_sets.set("target_sub_cool", target_sub_cool);

        // byte 15
        let odu_mode = byte15 & 0x03;
        data_sets.set("opermode", odu_mode as f32);
        if self.unit_id() == 0 {
            // unit_id가 1인 경우에는 ODU의 opermode를 설정한다.
            data_table().write().set(
                DeviceType::Odu,
                self.address(),
                "opermode",
                odu_mode as f32,
            )?;
        }
        let error_unit = ((byte15 >> 2) & 0x03) + 1;
        data_sets.set("odu_error_unit", error_unit as f32);
        let onboarding = (byte15 >> 4) & 0x01;
        data_sets.set("onboarding", onboarding as f32);
        let slave_unit_cnt = (byte15 >> 5) & 0x07;
        data_sets.set("slave_unit", slave_unit_cnt as f32);

        // byte 16
        let inv1_comp_freq = byte16;
        data_sets.set("inv1_comp_target_freq", inv1_comp_freq as f32);

        // byte 17
        let inv1_comp_current_freq = byte17;
        data_sets.set("inv1_comp_current_freq", inv1_comp_current_freq as f32);

        // byte 18
        let inv2_comp_freq = byte18;
        data_sets.set("inv2_comp_target_freq", inv2_comp_freq as f32);

        // byte 19
        let inv2_comp_current_freq = byte19;
        data_sets.set("inv2_comp_current_freq", inv2_comp_current_freq as f32);

        // byte 20
        let fan1_freq = byte20 as f32 * 10.0;
        data_sets.set("fan_freq1", fan1_freq);

        // byte 21
        let fan2_freq = byte21 as f32 * 10.0;
        data_sets.set("fan_freq2", fan2_freq);

        // byte 22
        let air_temp = byte22;
        let air_temp = get_airtemp(air_temp)?;
        data_sets.set("air_temp", air_temp as f32);

        // byte 23
        let high_pressure = byte23;
        let high_pressure = get_high_pressure_r410a(high_pressure)?;
        data_sets.set("high_pressure", high_pressure as f32);

        // byte 24
        let low_pressure = byte24;
        let low_pressure = get_high_pressure_r410a(low_pressure)?;
        data_sets.set("low_pressure", low_pressure as f32);

        let condense_temp = high_pressure as f32 / 10.0;
        data_sets.set("condense_temp", condense_temp);

        let evapo_temp = low_pressure as f32 / 10.0;
        data_sets.set("evapo_temp", evapo_temp);

        let pressure_rate = (high_pressure as f32 + 101.0) / (low_pressure as f32 + 101.0);
        data_sets.set("pressure_rate", pressure_rate);

        // byte 25
        let suction_temp = byte25;
        let suction_temp = get_suctiontemp(suction_temp)? as f32 / 10.0;
        data_sets.set("suction_temp", suction_temp as f32);

        // byte 26
        let inv1_discharge_temp = byte26;
        let inv1_discharge_temp = get_dischargetemp(inv1_discharge_temp)?;
        data_sets.set("inv1_discharge_temp", inv1_discharge_temp as f32);

        // byte 27
        let inv2_discharge_temp = byte27;
        let inv2_discharge_temp = get_dischargetemp(inv2_discharge_temp)?;
        data_sets.set("inv2_discharge_temp", inv2_discharge_temp as f32);

        // byte 28
        let liq_pipe_temp = byte28;
        let liq_pipe_temp = get_pipetemp(liq_pipe_temp)?;
        data_sets.set("liq_pipe_temp", liq_pipe_temp as f32);

        // byte 29
        let heat_exchange_temp_sensor = byte29;
        let heat_exchange_temp_sensor = get_pipetemp(heat_exchange_temp_sensor)?;
        data_sets.set(
            "heat_exchange_temp_sensor",
            heat_exchange_temp_sensor as f32,
        );

        // byte 30
        let upper_heat_exchanger_temp = byte30;
        let upper_heat_exchanger_temp = get_pipetemp(upper_heat_exchanger_temp)?;
        data_sets.set(
            "upper_heat_exchanger_temp",
            upper_heat_exchanger_temp as f32,
        );

        // byte 31
        let lower_heat_exchanger_temp = byte31;
        let lower_heat_exchanger_temp = get_pipetemp(lower_heat_exchanger_temp)?;
        data_sets.set(
            "lower_heat_exchanger_temp",
            lower_heat_exchanger_temp as f32,
        );

        // byte 32
        let subcool_inlet_temp = byte32;
        let subcool_inlet_temp = get_pipetemp(subcool_inlet_temp)?;
        data_sets.set("sc_inlet_temp", subcool_inlet_temp as f32);

        // byte 33
        let subcool_outlet_temp = byte33;
        let subcool_outlet_temp = get_pipetemp(subcool_outlet_temp)?;
        data_sets.set("sc_outlet_temp", subcool_outlet_temp as f32);

        let sh = (suction_temp as f32 - low_pressure as f32) / 10.0;
        data_sets.set("sh", sh);

        let sc = (high_pressure as f32 - liq_pipe_temp as f32) / 10.0;
        data_sets.set("sc", sc);

        let scsh = (subcool_outlet_temp as f32 - low_pressure as f32) / 10.0;
        data_sets.set("scsh", scsh);

        // byte 34
        let main1_eev_pulse = byte34 as f32 * 8.0;
        data_sets.set("main1_eev_pulse", main1_eev_pulse);

        // byte 35
        let main2_eev_pulse = byte35 as f32 * 8.0;
        data_sets.set("main2_eev_pulse", main2_eev_pulse);

        // byte 36
        let subcool_eev_pulse = byte36 as f32 * 8.0;
        data_sets.set("sub_cool_eev_pulse", subcool_eev_pulse);

        // byte 37
        let oil_balancing_eev_pulse = byte37 as f32 * 8.0;
        data_sets.set("tvi_eev_pulse", oil_balancing_eev_pulse);

        // byte 38
        let vi_eev1_pulse = byte38 as f32 * 8.0;
        data_sets.set("vi_eev1", vi_eev1_pulse);

        // byte 39
        let vi_eev2_pulse = byte39 as f32 * 8.0;
        data_sets.set("vi_eev2", vi_eev2_pulse);

        // byte 40
        let inv1_input_current = byte40 as f32 / 5.0;
        data_sets.set("inv1_input_current", inv1_input_current);

        // byte 41
        let inv1_input_voltage = byte41 as f32 * 5.0;
        data_sets.set("inv1_input_voltage", inv1_input_voltage);

        // byte 42
        let inv2_input_current = byte42 as f32 / 5.0;
        data_sets.set("inv2_input_current", inv2_input_current);

        // byte 43
        let inv2_input_voltage = byte43 as f32 * 5.0;
        data_sets.set("inv2_input_voltage", inv2_input_voltage);

        // byte 44
        let inv1_dclink = byte44 as f32 * 5.0;
        data_sets.set("inv1_dc_link_voltage", inv1_dclink);

        // byte 45
        let inv2_dclink = byte45 as f32 * 5.0;
        data_sets.set("inv2_dc_link_voltage", inv2_dclink);

        // byte 46
        let fan1_phase_current = byte46;
        data_sets.set("fan1_phase_current", fan1_phase_current as f32);

        // byte 47
        let fan2_phase_current = byte47;
        data_sets.set("fan2_phase_current", fan2_phase_current as f32);

        // byte 48
        let inv1_phase_current = byte48;
        data_sets.set("inverter1_phase_current", inv1_phase_current as f32);

        // byte 49
        let pwr_consumption_upper = byte49 as u32;

        // byte 50
        let pwr_consumption_middle = byte50 as u32;

        // byte 51
        let pwr_consumption_lower = byte51 as u32;
        let pwr_consumption =
            (pwr_consumption_upper << 16) + (pwr_consumption_middle << 8) + pwr_consumption_lower;
        // 아래쪽에서 처리

        // byte 52
        let inv1_heatsink = byte52;
        data_sets.set("inverter1_heatsink", inv1_heatsink as f32);

        // byte 53
        let connected_idu_count = byte53;
        data_sets.set("connected_idu_cnt", connected_idu_count as f32);

        // byte 54
        let inv2_heatsink = byte54;
        data_sets.set("inverter2_heatsink", inv2_heatsink as f32);

        // byte 55
        let capa = byte55;
        data_sets.set("odu_capacity", capa as f32);

        // byte 56
        let smart_plug_enable = (byte56 >> 7) & 0x01;
        info!("smart_plug_enable: {}**************88", smart_plug_enable);
        data_sets.set("smart_plug_enable", smart_plug_enable as f32);

        if self.unit_id == 0 {
            info!("address: {}, smart_plug_enable: {}", self.address(), smart_plug_enable);
            if let Err(e) = data_table().write().set(
                DeviceType::Odu,
                self.address(),
                "smart_plug_enable",
                smart_plug_enable as f32,
            ) {
                error!("Failed to set Odu smart_plug_enable: {e}");
            }
         }


        if smart_plug_enable == 1 {
            let pwr_current = byte56 & 0x01;
            data_sets.set("pwr_type", pwr_current as f32);
            if pwr_current == 1 {
                // 순시전력
                data_sets.set("pwr_cur", pwr_consumption as f32);
                data_sets.set("pwr_accm", 0.0);
            } else {
                // 누적전력
                data_sets.set("pwr_accm", pwr_consumption as f32);
                data_sets.set("pwr_cur", 0.0);
            }
        } else {
            data_sets.set("pwr_cur", 0.0);
            data_sets.set("pwr_accm", 0.0);
        }

        let ability_enhance_step = (byte56 >> 1) & 0x3f;
        data_sets.set("ability_enhance_step", ability_enhance_step as f32);

        // byte 57
        let fan_rpm_step = byte57 & 0x0f;
        data_sets.set("fan_rpm_step", fan_rpm_step as f32);
        let drycontact = (byte57 >> 4) & 0x01;
        data_sets.set("drycontact", drycontact as f32);
        let add_defrost = (byte57 >> 6) & 0x01;
        data_sets.set("add_defrost", add_defrost as f32);
        let remove_snow = (byte57 >> 7) & 0x01;
        data_sets.set("remove_snow", remove_snow as f32);

        // byte 58
        let inv2_capa = byte58 & 0x0f;
        data_sets.set("inv2_capa", inv2_capa as f32);
        let defrost = (byte58 >> 4) & 0x01;
        data_sets.set("defrost", defrost as f32);
        let div_defrost = (byte58 >> 5) & 0x01;
        data_sets.set("div_defrost", div_defrost as f32);
        let oil_return = (byte58 >> 6) & 0x01;
        data_sets.set("oil_return", oil_return as f32);
        let expose_power = (byte58 >> 7) & 0x01;
        data_sets.set("pwr_avail", expose_power as f32);

        // byte 59
        let inv1_oil_sensor = byte59 & 0x01;
        data_sets.set("inverter1_oil_sensor", inv1_oil_sensor as f32);
        let inv2_oil_sensor = (byte59 >> 1) & 0x01;
        data_sets.set("inverter2_oil_sensor", inv2_oil_sensor as f32);
        let inv1_heater = (byte59 >> 2) & 0x01;
        data_sets.set("inv1_heater", inv1_heater as f32);
        let inv2_heater = (byte59 >> 3) & 0x01;
        data_sets.set("inv2_heater", inv2_heater as f32);
        let suction_injection_valve = (byte59 >> 4) & 0x01;
        data_sets.set("suction_injection", suction_injection_valve as f32);
        let accum_oil_return_valve = (byte59 >> 5) & 0x01;
        data_sets.set("oilret", accum_oil_return_valve as f32);
        let fourway_valve2 = (byte59 >> 6) & 0x01;
        data_sets.set("fourway2", fourway_valve2 as f32);
        let fourway_valve1 = (byte59 >> 7) & 0x01;
        data_sets.set("fourway1", fourway_valve1 as f32);

        // byte 60
        let comp_count = byte60 & 0x03;
        data_sets.set("comp_count", comp_count as f32);
        let active_oil_valve1 = (byte60 >> 2) & 0x01;
        data_sets.set("active_oil_valve1", active_oil_valve1 as f32);
        let active_oil_valve2 = (byte60 >> 3) & 0x01;
        data_sets.set("active_oil_valve2", active_oil_valve2 as f32);
        let upper_heat_exchanger_valve = (byte60 >> 4) & 0x01;
        data_sets.set(
            "upper_heat_exchanger_valve",
            upper_heat_exchanger_valve as f32,
        );
        let lower_heat_exchanger_valve = (byte60 >> 5) & 0x01;
        data_sets.set(
            "lower_heat_exchanger_valve",
            lower_heat_exchanger_valve as f32,
        );
        let variable_path = (byte60 >> 6) & 0x01;
        data_sets.set("variable_path", variable_path as f32);
        let oil_equalizing_valve = (byte60 >> 7) & 0x01;
        data_sets.set("oil_equalizing_valve", oil_equalizing_valve as f32);

        // byte 61
        let receiver_in = byte61 & 0x01;
        data_sets.set("receiver_in", receiver_in as f32);
        let receiver_out = (byte61 >> 1) & 0x01;
        data_sets.set("receiver_out", receiver_out as f32);
        let inv1_capa = (byte61 >> 2) & 0x0f;
        data_sets.set("inv1_capa", inv1_capa as f32);
        let inv1_backup = (byte61 >> 6) & 0x01;
        data_sets.set("inv1_backup", inv1_backup as f32);
        let inv2_backup = (byte61 >> 7) & 0x01;
        data_sets.set("inv2_backup", inv2_backup as f32);

        // byte 62
        let inv2_phase_current = byte62;
        data_sets.set("inverter2_phase_current", inv2_phase_current as f32);

        if self.unit_id == 1 && oil_return == 1 {
            // yyyy-mm-ddThh:mm:ss
            let current_time = chrono::Local::now();
            let current_time = current_time.format("%Y-%m-%dT%H:%M:%S").to_string();
            data_sets.set_text("last_oilreturn_time", &current_time);
        } else if self.unit_id != 1 {
            // slave unit에서는 last_oilreturn_time을 계산하지 않는다.
            data_sets.set_text("last_oilreturn_time", "N/A");
        } else {
            // 만약 last_oilreturn_time이 설정된 적이 없다면 0으로 초기화
            if data_sets.get_text("last_oilreturn_time").is_empty() {
                data_sets.set_text("last_oilreturn_time", "N/A");
            }
        }

        data_table().write().set_units(
            DeviceType::OduUnit,
            self.address(),
            self.unit_id(),
            data_sets,
        )?;

        Ok(())
    }

    fn decode_super5_page10to14(&mut self, bytes: Bytes) -> Result<()> {
        let mut bytes = bytes;
        let check_bytes = bytes.clone();

        let byte0 = bytes.get_u8();
        let length = byte0 & 0x7F;
        if length != 0x40 {
            return Err(anyhow!(
                "ODU super5 page10to14 decode: invalid length: {length}"
            ));
        }

        if bytes.remaining() < length as usize - 1 {
            return Err(anyhow!("ODU super5 page10to14 decode: invalid length"));
        }

        let byte1 = bytes.get_u8();
        let cmd = (byte1 >> 3) & 0x0F;
        if cmd != 0xe {
            return Err(anyhow!("ODU super5 page10to14 decode: invalid cmd: {cmd}"));
        }

        let byte2 = bytes.get_u8();
        let byte3 = bytes.get_u8();
        let byte4 = bytes.get_u8();
        let byte5 = bytes.get_u8();
        let _byte6 = bytes.get_u8();
        let _byte7 = bytes.get_u8();
        let byte8 = bytes.get_u8();
        let byte9 = bytes.get_u8();
        let byte10 = bytes.get_u8();
        let byte11 = bytes.get_u8();
        let byte12 = bytes.get_u8();
        let byte13 = bytes.get_u8();
        let byte14 = bytes.get_u8();
        let byte15 = bytes.get_u8();
        let byte16 = bytes.get_u8();
        let byte17 = bytes.get_u8();
        let byte18 = bytes.get_u8();
        let byte19 = bytes.get_u8();
        let byte20 = bytes.get_u8();
        let byte21 = bytes.get_u8();
        let byte22 = bytes.get_u8();
        let byte23 = bytes.get_u8();
        let byte24 = bytes.get_u8();
        let byte25 = bytes.get_u8();
        let _byte26 = bytes.get_u8();
        let _byte27 = bytes.get_u8();
        let _byte28 = bytes.get_u8();
        let _byte29 = bytes.get_u8();
        let byte30 = bytes.get_u8();
        let byte31 = bytes.get_u8();
        let byte32 = bytes.get_u8();
        let _byte33 = bytes.get_u8();
        let byte34 = bytes.get_u8();
        let _byte35 = bytes.get_u8();
        let _byte36 = bytes.get_u8();
        let _byte37 = bytes.get_u8();
        let _byte38 = bytes.get_u8();
        let _byte39 = bytes.get_u8();
        let byte40 = bytes.get_u8();
        let byte41 = bytes.get_u8();
        let byte42 = bytes.get_u8();
        let byte43 = bytes.get_u8();
        let _byte44 = bytes.get_u8();
        let _byte45 = bytes.get_u8();
        let _byte46 = bytes.get_u8();
        let _byte47 = bytes.get_u8();
        let _byte48 = bytes.get_u8();
        let _byte49 = bytes.get_u8();
        let _byte50 = bytes.get_u8();
        let _byte51 = bytes.get_u8();
        let byte52 = bytes.get_u8();
        let _byte53 = bytes.get_u8();
        let byte54 = bytes.get_u8();
        let _byte55 = bytes.get_u8();
        let _byte56 = bytes.get_u8();
        let _byte57 = bytes.get_u8();
        let _byte58 = bytes.get_u8();
        let _byte59 = bytes.get_u8();
        let _byte60 = bytes.get_u8();
        let _byte61 = bytes.get_u8();
        let _byte62 = bytes.get_u8();
        let byte63 = bytes.get_u8();

        // byte 63
        let checksum = byte63;
        let expected_checksum = {
            let mut sum: u32 = 0;
            for byte in check_bytes[0..63].iter() {
                sum += *byte as u32;
            }
            ((sum ^ 0x55) & 0xff) as u8
        };

        self.connection_checker.reset_disconnect_count();
        let mut data_sets = DataSets::default();

        if checksum != expected_checksum {
            return Err(anyhow!(
                "ODU CmdE super5 checksum error: {checksum} != {expected_checksum}"
            ));
        }

        // byte 2
        let recv_product_code = byte2;
        if !(0xa0..=0xaf).contains(&recv_product_code) {
            return Err(anyhow!("This msg is not for ACP"));
        }

        // byte 3
        let product_code = byte3;
        if !(0xc0..=0xcf).contains(&product_code) {
            return Err(anyhow!(
                "ODU CmdE super5 product code error: {product_code}"
            ));
        }
        self.product_code = product_code;

        // byte 4
        let addr = byte4;
        if addr != self.odu_addr {
            return Err(anyhow!("ODU CmdE super5 addr error: {addr}"));
        }

        // byte 5
        let _page = byte5;

        // byte 6
        // byte 7
        // 중복으로 skip

        // byte 8
        let micom_svc_version = byte8;
        self.patch = micom_svc_version;

        // byte 9
        let inv1_comp_micom_version = byte9;
        data_sets.set("inv1_comp_micom_version", inv1_comp_micom_version as f32);

        // byte 10
        let inv2_comp_micom_version = byte10;
        data_sets.set("inv2_comp_micom_version", inv2_comp_micom_version as f32);

        // byte 11
        let fan1_micom_version = byte11;
        data_sets.set("fan1_micom_version", fan1_micom_version as f32);

        // byte 12
        let fan2_micom_version = byte12;
        data_sets.set("fan2_micom_version", fan2_micom_version as f32);

        // byte 13
        let eep_version_upper = byte13 as u32;

        // byte 14
        let eep_version_middle = byte14 as u32;

        // byte 15
        let eep_version_lower = byte15 as u32;
        let eep_version = format!(
            "{}.{}.{}",
            eep_version_upper, eep_version_middle, eep_version_lower
        );
        data_sets.set_text("eeprom_version", &eep_version);

        // byte 16
        let external_version = byte16;
        data_sets.set("externel_version", external_version as f32);

        // byte 17
        let cycle_overshoot_limit = byte17 & 0x01;
        data_sets.set("cycle_overshoot_limit", cycle_overshoot_limit as f32);
        let cycle_invup_limit = (byte17 >> 1) & 0x01;
        data_sets.set("cycle_invup_limit", cycle_invup_limit as f32);
        let cycle_lowtempcool_limit = (byte17 >> 2) & 0x01;
        data_sets.set("cycle_lowtempcool_limit", cycle_lowtempcool_limit as f32);
        let cycle_ipmtemp_limit = (byte17 >> 3) & 0x01;
        data_sets.set("cycle_ipmtemp_limit", cycle_ipmtemp_limit as f32);
        let cycle_dometemp_limit = (byte17 >> 4) & 0x01;
        data_sets.set("cycle_dometemp_limit", cycle_dometemp_limit as f32);
        let cycle_pressure_limit = (byte17 >> 5) & 0x01;
        data_sets.set("cycle_pressure_limit", cycle_pressure_limit as f32);
        let cycle_pressureratio_limit = (byte17 >> 6) & 0x01;
        data_sets.set(
            "cycle_pressureratio_limit",
            cycle_pressureratio_limit as f32,
        );
        let cycle_liquidbackheat_limit = (byte17 >> 7) & 0x01;
        data_sets.set(
            "cycle_liquidbackheat_limit",
            cycle_liquidbackheat_limit as f32,
        );

        // byte 18
        let _cycle_emergency_control = byte18;

        // byte 19
        let odu_error_num = byte19;
        data_sets.set("odu_error_num", odu_error_num as f32);

        // byte 20
        let odu_error_level = byte20 & 0x07;
        data_sets.set("odu_error_level", odu_error_level as f32);
        let odu_error_unit = (byte20 >> 3) & 0x07;
        data_sets.set("odu_error_unit_info", odu_error_unit as f32);
        let odu_error_inv = (byte20 >> 6) & 0x03;
        data_sets.set("odu_error_inv", odu_error_inv as f32);

        // byte 21
        let odu_idu_comm_type = byte21;
        data_sets.set("odu_idu_comm_type", odu_idu_comm_type as f32);

        // byte 22
        let tvi_inlet_temp = byte22;
        data_sets.set("tvi_inlet_temp", tvi_inlet_temp as f32);

        // byte 23
        let tvi_outlet_temp = byte23;
        data_sets.set("tvi_outlet_temp", tvi_outlet_temp as f32);

        // byte 24
        let lb_inlet_temp = byte24;
        data_sets.set("lb_inlet_temp", lb_inlet_temp as f32);

        // byte 25
        let lb_outlet_temp = byte25;
        data_sets.set("lb_outlet_temp", lb_outlet_temp as f32);

        // byte 26
        // byte 27
        // byte 28
        // byte 29

        // byte 30
        let noise_level = byte30;
        data_sets.set("noise_level", noise_level as f32);

        // byte 31
        let humidity_value = byte31;
        data_sets.set("humidity_value", humidity_value as f32);

        // byte 32
        let accumulated_snow = byte32;
        data_sets.set("accumulated_snow", accumulated_snow as f32);

        // byte 33

        // byte 34
        let lb_eev_pulse = byte34 as u16 * 8;
        data_sets.set("lb_eev_pulse", lb_eev_pulse as f32);

        // byte 35
        // byte 36
        // byte 37
        // byte 38
        // byte 39

        // byte 40
        let inv1_overload = byte40 & 0x01;
        data_sets.set("inv1_overload", inv1_overload as f32);
        let inv1_input_current_limit = (byte40 >> 1) & 0x01;
        data_sets.set("inv1_input_current_limit", inv1_input_current_limit as f32);
        let inv1_heatsink_limit = (byte40 >> 2) & 0x01;
        data_sets.set("inv1_heatsink_limit", inv1_heatsink_limit as f32);
        let inv1_voltage_limit = (byte40 >> 3) & 0x01;
        data_sets.set("inv1_voltage_limit", inv1_voltage_limit as f32);

        // byte 41
        let inv2_overload = byte41 & 0x01;
        data_sets.set("inv2_overload", inv2_overload as f32);
        let inv2_input_current_limit = (byte41 >> 1) & 0x01;
        data_sets.set("inv2_input_current_limit", inv2_input_current_limit as f32);
        let inv2_heatsink_limit = (byte41 >> 2) & 0x01;
        data_sets.set("inv2_heatsink_limit", inv2_heatsink_limit as f32);
        let inv2_voltage_limit = (byte41 >> 3) & 0x01;
        data_sets.set("inv2_voltage_limit", inv2_voltage_limit as f32);

        // byte 42
        let fan1_overload = byte42 & 0x01;
        data_sets.set("fan1_overload", fan1_overload as f32);
        let fan1_input_current_limit = (byte42 >> 1) & 0x01;
        data_sets.set("fan1_input_current_limit", fan1_input_current_limit as f32);
        let fan1_heatsink_limit = (byte42 >> 2) & 0x01;
        data_sets.set("fan1_heatsink_limit", fan1_heatsink_limit as f32);
        let fan1_voltage_limit = (byte42 >> 3) & 0x01;
        data_sets.set("fan1_voltage_limit", fan1_voltage_limit as f32);

        // byte 43
        let fan2_overload = byte43 & 0x01;
        data_sets.set("fan2_overload", fan2_overload as f32);
        let fan2_input_current_limit = (byte43 >> 1) & 0x01;
        data_sets.set("fan2_input_current_limit", fan2_input_current_limit as f32);
        let fan2_heatsink_limit = (byte43 >> 2) & 0x01;
        data_sets.set("fan2_heatsink_limit", fan2_heatsink_limit as f32);
        let fan2_voltage_limit = (byte43 >> 3) & 0x01;
        data_sets.set("fan2_voltage_limit", fan2_voltage_limit as f32);

        // byte 44
        // byte 45
        // byte 46
        // byte 47
        // byte 48
        // byte 49
        // byte 50
        // byte 51

        // byte 52
        let fan1_heatsink = byte52;
        data_sets.set("fan1_heatsink", fan1_heatsink as f32);

        // byte 53

        // byte 54
        let fan2_heatsink = byte54;
        data_sets.set("fan2_heatsink", fan2_heatsink as f32);

        data_table().write().set_units(
            DeviceType::OduUnit,
            self.address(),
            self.unit_id(),
            data_sets,
        )?;

        Ok(())
    }

    fn decode_super5_page20to24(&mut self, bytes: Bytes) -> Result<()> {
        let mut bytes = bytes;
        let check_bytes = bytes.clone();

        let byte0 = bytes.get_u8();
        let length = byte0 & 0x7F;
        if length != 0x40 {
            return Err(anyhow!(
                "ODU super5 page10to14 decode: invalid length: {length}"
            ));
        }

        if bytes.remaining() < length as usize - 1 {
            return Err(anyhow!("ODU super5 page10to14 decode: invalid length"));
        }

        let byte1 = bytes.get_u8();
        let cmd = (byte1 >> 3) & 0x0F;
        if cmd != 0xe {
            return Err(anyhow!("ODU super5 page10to14 decode: invalid cmd: {cmd}"));
        }

        let byte2 = bytes.get_u8();
        let byte3 = bytes.get_u8();
        let byte4 = bytes.get_u8();
        let byte5 = bytes.get_u8();
        let byte6 = bytes.get_u8();
        let byte7 = bytes.get_u8();
        let byte8 = bytes.get_u8();
        let byte9 = bytes.get_u8();
        let byte10 = bytes.get_u8();
        let byte11 = bytes.get_u8();
        let byte12 = bytes.get_u8();
        let byte13 = bytes.get_u8();
        let byte14 = bytes.get_u8();
        let byte15 = bytes.get_u8();
        let byte16 = bytes.get_u8();
        let byte17 = bytes.get_u8();
        let byte18 = bytes.get_u8();
        let byte19 = bytes.get_u8();
        let byte20 = bytes.get_u8();
        let byte21 = bytes.get_u8();
        let byte22 = bytes.get_u8();
        let byte23 = bytes.get_u8();
        let byte24 = bytes.get_u8();
        let byte25 = bytes.get_u8();
        let byte26 = bytes.get_u8();
        let byte27 = bytes.get_u8();
        let byte28 = bytes.get_u8();
        let byte29 = bytes.get_u8();
        let byte30 = bytes.get_u8();
        let byte31 = bytes.get_u8();
        let byte32 = bytes.get_u8();
        let byte33 = bytes.get_u8();
        let byte34 = bytes.get_u8();
        let byte35 = bytes.get_u8();
        let byte36 = bytes.get_u8();
        let byte37 = bytes.get_u8();
        let byte38 = bytes.get_u8();
        let byte39 = bytes.get_u8();
        let byte40 = bytes.get_u8();
        let byte41 = bytes.get_u8();
        let byte42 = bytes.get_u8();
        let byte43 = bytes.get_u8();
        let byte44 = bytes.get_u8();
        let byte45 = bytes.get_u8();
        let byte46 = bytes.get_u8();
        let byte47 = bytes.get_u8();
        let byte48 = bytes.get_u8();
        let byte49 = bytes.get_u8();
        let byte50 = bytes.get_u8();
        let _byte51 = bytes.get_u8();
        let _byte52 = bytes.get_u8();
        let _byte53 = bytes.get_u8();
        let _byte54 = bytes.get_u8();
        let _byte55 = bytes.get_u8();
        let _byte56 = bytes.get_u8();
        let _byte57 = bytes.get_u8();
        let _byte58 = bytes.get_u8();
        let _byte59 = bytes.get_u8();
        let _byte60 = bytes.get_u8();
        let _byte61 = bytes.get_u8();
        let _byte62 = bytes.get_u8();
        let byte63 = bytes.get_u8();

        // byte 63
        let checksum = byte63;
        let expected_checksum = {
            let mut sum: u32 = 0;
            for byte in check_bytes[0..63].iter() {
                sum += *byte as u32;
            }
            ((sum ^ 0x55) & 0xff) as u8
        };

        self.connection_checker.reset_disconnect_count();
        let mut data_sets = DataSets::default();

        if checksum != expected_checksum {
            return Err(anyhow!(
                "ODU CmdE super5 checksum error: {checksum} != {expected_checksum}"
            ));
        }

        // byte 2
        let recv_product_code = byte2;
        if !(0xa0..=0xaf).contains(&recv_product_code) {
            return Err(anyhow!("This msg is not for ACP"));
        }

        // byte 3
        let product_code = byte3;
        if !(0xc0..=0xcf).contains(&product_code) {
            return Err(anyhow!(
                "ODU CmdE super5 product code error: {product_code}"
            ));
        }
        self.product_code = product_code;

        // byte 4
        let addr = byte4;
        if addr != self.odu_addr {
            return Err(anyhow!("ODU CmdE super5 addr error: {addr}"));
        }

        // byte 5
        let _page = byte5;

        // byte 6
        let unit_power_connect_time_upper = byte6 as u32;

        // byte 7
        let unit_power_connect_time_middle = byte7 as u32;

        // byte 8
        let unit_power_connect_time_lower = byte8 as u32;
        let unit_power_connect_time = (unit_power_connect_time_upper << 16)
            + (unit_power_connect_time_middle << 8)
            + unit_power_connect_time_lower;
        data_sets.set("unit_power_connect_time", unit_power_connect_time as f32);

        // byte 9
        let unit_comp1_running_time_upper = byte9 as u32;

        // byte 10
        let unit_comp1_running_time_middle = byte10 as u32;

        // byte 11
        let unit_comp1_running_time_lower = byte11 as u32;
        let unit_comp1_running_time = (unit_comp1_running_time_upper << 16)
            + (unit_comp1_running_time_middle << 8)
            + unit_comp1_running_time_lower;
        data_sets.set("unit_comp1_running_time", unit_comp1_running_time as f32);

        // byte 12
        let unit_comp2_running_time_upper = byte12 as u32;

        // byte 13
        let unit_comp2_running_time_middle = byte13 as u32;

        // byte 14
        let unit_comp2_running_time_lower = byte14 as u32;
        let unit_comp2_running_time = (unit_comp2_running_time_upper << 16)
            + (unit_comp2_running_time_middle << 8)
            + unit_comp2_running_time_lower;
        data_sets.set("unit_comp2_running_time", unit_comp2_running_time as f32);

        // byte 15
        let unit_fanmotor1_running_time_upper = byte15 as u32;

        // byte 16
        let unit_fanmotor1_running_time_middle = byte16 as u32;

        // byte 17
        let unit_fanmotor1_running_time_lower = byte17 as u32;
        let unit_fanmotor1_running_time = (unit_fanmotor1_running_time_upper << 16)
            + (unit_fanmotor1_running_time_middle << 8)
            + unit_fanmotor1_running_time_lower;
        data_sets.set(
            "unit_fanmotor1_running_time",
            unit_fanmotor1_running_time as f32,
        );

        // byte 18
        let unit_fanmotor2_running_time_upper = byte18 as u32;

        // byte 19
        let unit_fanmotor2_running_time_middle = byte19 as u32;

        // byte 20
        let unit_fanmotor2_running_time_lower = byte20 as u32;
        let unit_fanmotor2_running_time = (unit_fanmotor2_running_time_upper << 16)
            + (unit_fanmotor2_running_time_middle << 8)
            + unit_fanmotor2_running_time_lower;
        data_sets.set(
            "unit_fanmotor2_running_time",
            unit_fanmotor2_running_time as f32,
        );

        // byte 21 - byte 35: unit_model_name
        let unit_model_name = vec![
            byte21, byte22, byte23, byte24, byte25, byte26, byte27, byte28, byte29, byte30, byte31,
            byte32, byte33, byte34, byte35,
        ];
        let unit_model_name = if byte21 == 0 {
            // 첫 byte가 0이면 unit_model_name이 없는 것으로 판단
            "N/A".to_string()
        } else {
            match String::from_utf8(unit_model_name) {
                Ok(s) => s,
                Err(_) => "N/A".to_string(),
            }
        };
        data_sets.set_text("unit_model_name", &unit_model_name);

        // byte 36 - byte 50: unit_product_no
        let unit_product_no = vec![
            byte36, byte37, byte38, byte39, byte40, byte41, byte42, byte43, byte44, byte45, byte46,
            byte47, byte48, byte49, byte50,
        ];
        let unit_product_no = if byte36 == 0 {
            // 첫 byte가 0이면 unit_product_no가 없는 것으로 판단
            "N/A".to_string()
        } else {
            match String::from_utf8(unit_product_no) {
                Ok(s) => s,
                Err(_) => "N/A".to_string(),
            }
        };
        data_sets.set_text("unit_product_no", &unit_product_no);

        data_table().write().set_units(
            DeviceType::OduUnit,
            self.address(),
            self.unit_id(),
            data_sets,
        )?;

        Ok(())
    }

    fn decode_super5_page40to44(&mut self, bytes: Bytes) -> Result<()> {
        let mut bytes = bytes;
        let check_bytes = bytes.clone();

        let byte0 = bytes.get_u8();
        let length = byte0 & 0x7F;
        if length != 0x40 {
            return Err(anyhow!(
                "ODU super5 page10to14 decode: invalid length: {length}"
            ));
        }

        if bytes.remaining() < length as usize - 1 {
            return Err(anyhow!("ODU super5 page10to14 decode: invalid length"));
        }

        let byte1 = bytes.get_u8();
        let cmd = (byte1 >> 3) & 0x0F;
        if cmd != 0xe {
            return Err(anyhow!("ODU super5 page10to14 decode: invalid cmd: {cmd}"));
        }

        let byte2 = bytes.get_u8();
        let byte3 = bytes.get_u8();
        let byte4 = bytes.get_u8();
        let byte5 = bytes.get_u8();
        let byte6 = bytes.get_u8();
        let byte7 = bytes.get_u8();
        let byte8 = bytes.get_u8();
        let byte9 = bytes.get_u8();
        let byte10 = bytes.get_u8();
        let byte11 = bytes.get_u8();
        let byte12 = bytes.get_u8();
        let byte13 = bytes.get_u8();
        let byte14 = bytes.get_u8();
        let byte15 = bytes.get_u8();
        let byte16 = bytes.get_u8();
        let byte17 = bytes.get_u8();
        let byte18 = bytes.get_u8();
        let byte19 = bytes.get_u8();
        let byte20 = bytes.get_u8();
        let byte21 = bytes.get_u8();
        let byte22 = bytes.get_u8();
        let byte23 = bytes.get_u8();
        let byte24 = bytes.get_u8();
        let byte25 = bytes.get_u8();
        let _byte26 = bytes.get_u8();
        let byte27 = bytes.get_u8();
        let byte28 = bytes.get_u8();
        let byte29 = bytes.get_u8();
        let byte30 = bytes.get_u8();
        let byte31 = bytes.get_u8();
        let byte32 = bytes.get_u8();
        let byte33 = bytes.get_u8();
        let byte34 = bytes.get_u8();
        let byte35 = bytes.get_u8();
        let byte36 = bytes.get_u8();
        let byte37 = bytes.get_u8();
        let byte38 = bytes.get_u8();
        let byte39 = bytes.get_u8();
        let byte40 = bytes.get_u8();
        let byte41 = bytes.get_u8();
        let byte42 = bytes.get_u8();
        let byte43 = bytes.get_u8();
        let byte44 = bytes.get_u8();
        let byte45 = bytes.get_u8();
        let byte46 = bytes.get_u8();
        let _byte47 = bytes.get_u8();
        let _byte48 = bytes.get_u8();
        let _byte49 = bytes.get_u8();
        let _byte50 = bytes.get_u8();
        let _byte51 = bytes.get_u8();
        let _byte52 = bytes.get_u8();
        let _byte53 = bytes.get_u8();
        let _byte54 = bytes.get_u8();
        let _byte55 = bytes.get_u8();
        let _byte56 = bytes.get_u8();
        let _byte57 = bytes.get_u8();
        let _byte58 = bytes.get_u8();
        let _byte59 = bytes.get_u8();
        let _byte60 = bytes.get_u8();
        let _byte61 = bytes.get_u8();
        let _byte62 = bytes.get_u8();
        let byte63 = bytes.get_u8();

        // byte 63
        let checksum = byte63;
        let expected_checksum = {
            let mut sum: u32 = 0;
            for byte in check_bytes[0..63].iter() {
                sum += *byte as u32;
            }
            ((sum ^ 0x55) & 0xff) as u8
        };

        self.connection_checker.reset_disconnect_count();
        let mut data_sets = DataSets::default();

        if checksum != expected_checksum {
            return Err(anyhow!(
                "ODU CmdE super5 checksum error: {checksum} != {expected_checksum}"
            ));
        }

        // byte 2
        let recv_product_code = byte2;
        if !(0xa0..=0xaf).contains(&recv_product_code) {
            return Err(anyhow!("This msg is not for ACP"));
        }

        // byte 3
        let product_code = byte3;
        if !(0xc0..=0xcf).contains(&product_code) {
            return Err(anyhow!(
                "ODU CmdE super5 product code error: {product_code}"
            ));
        }
        self.product_code = product_code;

        // byte 4
        let addr = byte4;
        if addr != self.odu_addr {
            return Err(anyhow!("ODU CmdE super5 addr error: {addr}"));
        }

        // byte 5
        let _page = byte5;

        // byte 6
        let comp1_no_entry = (byte6 >> 1) & 0x01;
        data_sets.set("comp1_no_entry", comp1_no_entry as f32);
        let comp1_stop = (byte6 >> 2) & 0x01;
        data_sets.set("comp1_stop", comp1_stop as f32);
        let comp1_ng = (byte6 >> 3) & 0x01;
        data_sets.set("comp1_ng", comp1_ng as f32);
        let comp1_ok = (byte6 >> 4) & 0x01;
        data_sets.set("comp1_ok", comp1_ok as f32);
        let comp1_pcb_ng = (byte6 >> 5) & 0x01;
        data_sets.set("comp1_pcb_ng", comp1_pcb_ng as f32);
        let comp1_pcb_ok = (byte6 >> 6) & 0x01;
        data_sets.set("comp1_pcb_ok", comp1_pcb_ok as f32);
        let comp1_complete = (byte6 >> 7) & 0x01;
        data_sets.set("comp1_complete", comp1_complete as f32);

        // byte 7
        let comp1_resist_upper = byte7 as u16;

        // byte 8
        let comp1_resist_lower = byte8 as u16;
        let comp1_resist = (comp1_resist_upper << 8) + comp1_resist_lower;
        data_sets.set("comp1_resist_value", comp1_resist as f32);

        // byte 9
        let comp1_ld_upper = byte9 as u16;

        // byte 10
        let comp1_ld_lower = byte10 as u16;
        let comp1_ld = (comp1_ld_upper << 8) + comp1_ld_lower;
        data_sets.set("comp1_ld_value", comp1_ld as f32);

        // byte 11
        let comp1_lq_upper = byte11 as u16;

        // byte 12
        let comp1_lq_lower = byte12 as u16;
        let comp1_lq = (comp1_lq_upper << 8) + comp1_lq_lower;
        data_sets.set("comp1_lq_value", comp1_lq as f32);

        // byte 13
        let comp1_back_elec_force_upper = byte13 as u16;

        // byte 14
        let comp1_back_elec_force_lower = byte14 as u16;
        let comp1_back_elec_force =
            (comp1_back_elec_force_upper << 8) + comp1_back_elec_force_lower;
        data_sets.set("comp1_back_elec_force", comp1_back_elec_force as f32);

        // byte 15
        let comp1_autotuning_apply_status = (byte15 >> 4) & 0x01;
        data_sets.set(
            "comp1_autotuning_apply_status",
            comp1_autotuning_apply_status as f32,
        );
        let comp1_autotuning_fail = (byte15 >> 5) & 0x01;
        data_sets.set("comp1_autotuning_fail", comp1_autotuning_fail as f32);
        let comp1_autotuning_success = (byte15 >> 6) & 0x01;
        data_sets.set("comp1_autotuning_success", comp1_autotuning_success as f32);
        let comp1_autotuning_logic_status = (byte15 >> 7) & 0x01;
        data_sets.set(
            "comp1_autotuning_logic_status",
            comp1_autotuning_logic_status as f32,
        );

        // byte 16
        let comp2_no_entry = (byte16 >> 1) & 0x01;
        data_sets.set("comp2_no_entry", comp2_no_entry as f32);
        let comp2_stop = (byte16 >> 2) & 0x01;
        data_sets.set("comp2_stop", comp2_stop as f32);
        let comp2_ng = (byte16 >> 3) & 0x01;
        data_sets.set("comp2_ng", comp2_ng as f32);
        let comp2_ok = (byte16 >> 4) & 0x01;
        data_sets.set("comp2_ok", comp2_ok as f32);
        let comp2_pcb_ng = (byte16 >> 5) & 0x01;
        data_sets.set("comp2_pcb_ng", comp2_pcb_ng as f32);
        let comp2_pcb_ok = (byte16 >> 6) & 0x01;
        data_sets.set("comp2_pcb_ok", comp2_pcb_ok as f32);
        let comp2_complete = (byte16 >> 7) & 0x01;
        data_sets.set("comp2_complete", comp2_complete as f32);

        // byte 17
        let comp2_resist_upper = byte17 as u16;

        // byte 18
        let comp2_resist_lower = byte18 as u16;
        let comp2_resist = (comp2_resist_upper << 8) + comp2_resist_lower;
        data_sets.set("comp2_resist_value", comp2_resist as f32);

        // byte 19
        let comp2_ld_upper = byte19 as u16;

        // byte 20
        let comp2_ld_lower = byte20 as u16;
        let comp2_ld = (comp2_ld_upper << 8) + comp2_ld_lower;
        data_sets.set("comp2_ld_value", comp2_ld as f32);

        // byte 21
        let comp2_lq_upper = byte21 as u16;

        // byte 22
        let comp2_lq_lower = byte22 as u16;
        let comp2_lq = (comp2_lq_upper << 8) + comp2_lq_lower;
        data_sets.set("comp2_lq_value", comp2_lq as f32);

        // byte 23
        let comp2_back_elec_force_upper = byte23 as u16;

        // byte 24
        let comp2_back_elec_force_lower = byte24 as u16;
        let comp2_back_elec_force =
            (comp2_back_elec_force_upper << 8) + comp2_back_elec_force_lower;
        data_sets.set("comp2_back_elec_force", comp2_back_elec_force as f32);

        // byte 25
        let comp2_autotuning_apply_status = (byte25 >> 4) & 0x01;
        data_sets.set(
            "comp2_autotuning_apply_status",
            comp2_autotuning_apply_status as f32,
        );
        let comp2_autotuning_fail = (byte25 >> 5) & 0x01;
        data_sets.set("comp2_autotuning_fail", comp2_autotuning_fail as f32);
        let comp2_autotuning_success = (byte25 >> 6) & 0x01;
        data_sets.set("comp2_autotuning_success", comp2_autotuning_success as f32);
        let comp2_autotuning_logic_status = (byte25 >> 7) & 0x01;
        data_sets.set(
            "comp2_autotuning_logic_status",
            comp2_autotuning_logic_status as f32,
        );

        // byte 46
        let fan1_no_entry = (byte46 >> 1) & 0x01;
        data_sets.set("fan1_no_entry", fan1_no_entry as f32);
        let fan1_stop = (byte46 >> 2) & 0x01;
        data_sets.set("fan1_stop", fan1_stop as f32);
        let fan1_ng = (byte46 >> 3) & 0x01;
        data_sets.set("fan1_ng", fan1_ng as f32);
        let fan1_ok = (byte46 >> 4) & 0x01;
        data_sets.set("fan1_ok", fan1_ok as f32);
        let fan1_pcb_ng = (byte46 >> 5) & 0x01;
        data_sets.set("fan1_pcb_ng", fan1_pcb_ng as f32);
        let fan1_pcb_ok = (byte46 >> 6) & 0x01;
        data_sets.set("fan1_pcb_ok", fan1_pcb_ok as f32);
        let fan1_complete = (byte46 >> 7) & 0x01;
        data_sets.set("fan1_complete", fan1_complete as f32);

        // byte 27
        let fan1_resist_upper = byte27 as u16;

        // byte 28
        let fan1_resist_lower = byte28 as u16;
        let fan1_resist = (fan1_resist_upper << 8) + fan1_resist_lower;
        data_sets.set("fan1_resist_value", fan1_resist as f32);

        // byte 29
        let fan1_ld_upper = byte29 as u16;

        // byte 30
        let fan1_ld_lower = byte30 as u16;
        let fan1_ld = (fan1_ld_upper << 8) + fan1_ld_lower;
        data_sets.set("fan1_ld_value", fan1_ld as f32);

        // byte 31
        let fan1_lq_upper = byte31 as u16;

        // byte 32
        let fan1_lq_lower = byte32 as u16;
        let fan1_lq = (fan1_lq_upper << 8) + fan1_lq_lower;
        data_sets.set("fan1_lq_value", fan1_lq as f32);

        // byte 33
        let fan1_back_elec_force_upper = byte33 as u16;

        // byte 34
        let fan1_back_elec_force_lower = byte34 as u16;
        let fan1_back_elec_force = (fan1_back_elec_force_upper << 8) + fan1_back_elec_force_lower;
        data_sets.set("fan1_back_elec_force", fan1_back_elec_force as f32);

        // byte 35
        let fan1_autotuning_apply_status = (byte35 >> 4) & 0x01;
        data_sets.set(
            "fan1_autotuning_apply_status",
            fan1_autotuning_apply_status as f32,
        );
        let fan1_autotuning_fail = (byte35 >> 5) & 0x01;
        data_sets.set("fan1_autotuning_fail", fan1_autotuning_fail as f32);
        let fan1_autotuning_success = (byte35 >> 6) & 0x01;
        data_sets.set("fan1_autotuning_success", fan1_autotuning_success as f32);
        let fan1_autotuning_logic_status = (byte35 >> 7) & 0x01;
        data_sets.set(
            "fan1_autotuning_logic_status",
            fan1_autotuning_logic_status as f32,
        );

        // byte 36
        let fan2_no_entry = (byte36 >> 1) & 0x01;
        data_sets.set("fan2_no_entry", fan2_no_entry as f32);
        let fan2_stop = (byte36 >> 2) & 0x01;
        data_sets.set("fan2_stop", fan2_stop as f32);
        let fan2_ng = (byte36 >> 3) & 0x01;
        data_sets.set("fan2_ng", fan2_ng as f32);
        let fan2_ok = (byte36 >> 4) & 0x01;
        data_sets.set("fan2_ok", fan2_ok as f32);
        let fan2_pcb_ng = (byte36 >> 5) & 0x01;
        data_sets.set("fan2_pcb_ng", fan2_pcb_ng as f32);
        let fan2_pcb_ok = (byte36 >> 6) & 0x01;
        data_sets.set("fan2_pcb_ok", fan2_pcb_ok as f32);
        let fan2_complete = (byte36 >> 7) & 0x01;
        data_sets.set("fan2_complete", fan2_complete as f32);

        // byte 37
        let fan2_resist_upper = byte37 as u16;

        // byte 38
        let fan2_resist_lower = byte38 as u16;
        let fan2_resist = (fan2_resist_upper << 8) + fan2_resist_lower;
        data_sets.set("fan2_resist_value", fan2_resist as f32);

        // byte 39
        let fan2_ld_upper = byte39 as u16;

        // byte 40
        let fan2_ld_lower = byte40 as u16;
        let fan2_ld = (fan2_ld_upper << 8) + fan2_ld_lower;
        data_sets.set("fan2_ld_value", fan2_ld as f32);

        // byte 41
        let fan2_lq_upper = byte41 as u16;

        // byte 42
        let fan2_lq_lower = byte42 as u16;
        let fan2_lq = (fan2_lq_upper << 8) + fan2_lq_lower;
        data_sets.set("fan2_lq_value", fan2_lq as f32);

        // byte 43
        let fan2_back_elec_force_upper = byte43 as u16;

        // byte 44
        let fan2_back_elec_force_lower = byte44 as u16;
        let fan2_back_elec_force = (fan2_back_elec_force_upper << 8) + fan2_back_elec_force_lower;
        data_sets.set("fan2_back_elec_force", fan2_back_elec_force as f32);

        // byte 45
        let fan2_autotuning_apply_status = (byte45 >> 4) & 0x01;
        data_sets.set(
            "fan2_autotuning_apply_status",
            fan2_autotuning_apply_status as f32,
        );
        let fan2_autotuning_fail = (byte45 >> 5) & 0x01;
        data_sets.set("fan2_autotuning_fail", fan2_autotuning_fail as f32);
        let fan2_autotuning_success = (byte45 >> 6) & 0x01;
        data_sets.set("fan2_autotuning_success", fan2_autotuning_success as f32);
        let fan2_autotuning_logic_status = (byte45 >> 7) & 0x01;
        data_sets.set(
            "fan2_autotuning_logic_status",
            fan2_autotuning_logic_status as f32,
        );

        data_table().write().set_units(
            DeviceType::OduUnit,
            self.address(),
            self.unit_id(),
            data_sets,
        )?;

        Ok(())
    }

    fn decode_super5_page38to3c(&mut self, bytes: Bytes) -> Result<()> {
        info!("ODU super5 page38to3c decode is not implemented yet");

        Ok(())
    }
      
}

impl LgapCodec for Super5 {
    fn encode(&mut self) -> Bytes {
        if self.is_searching_mode() {
            self.set_searching_mode_done();
        }

        // 만약 이전에 사이클 모니터링을 위해서 weight가 변경되었을 수 있기 때문에
        // 기본값으로 되돌린다.
        self.weight = self.default_weight;
        self.encode_cmde()
    }

    fn decode(&mut self, bytes: &Bytes) -> Result<()> {
        if self.is_searching_mode() {
            if let Err(e) = data_manager::facility::set_serial_port(
                self.odu_id,
                Some(self.searching_port as u32),
            ) {
                error!("Failed to set {}'s serial port: {e}", self.odu_id);
            }
            self.port = self.searching_port;
        }

        if let Some(byte3) = bytes.get(3) {
            if *byte3 < 0xC0 || *byte3 > 0xCF {
                return Err(anyhow!("ODU decode: Invalid product code: {byte3}"));
            }
        }

        if let Some(byte4) = bytes.get(4) {
            if *byte4 != self.odu_addr {
                return Err(anyhow!("IDU decode: Invalid addr: {byte4}"));
            }
        }

        self.decode_super5(bytes.clone())?;

        data_table()
            .write()
            .flush_unit(DeviceType::OduUnit, self.address(), self.unit_id(), None);

        Ok(())
    }
}

impl DeviceInfo for Super5 {
    fn device_type(&self) -> DeviceType {
        DeviceType::OduUnit
    }

    fn address(&self) -> u8 {
        self.odu_addr
    }

    fn unit_id(&self) -> u8 {
        self.unit_id
    }

    fn set_search_port(&mut self, search_port: u8) {
        self.searching_port = search_port;
    }

    fn is_unused(&self) -> bool {
        // cycle 모니터링이 비활성화된 경우에는
        // 이 장치가 사용되지 않는 것으로 간주한다.
        if !config().read().cycle_monitor {
            return true;
        }

        self.is_unused
    }
}

impl NeedSchedule for Super5 {
    fn is_dirty(&self) -> bool {
        false
    }

    fn weight(&self) -> u32 {
        if config().read().odu_cycle_boost {
            // 사이클 모니터링이 활성화된 경우에는
            // 실내기와 동일한 weight를 사용한다.
            80
        } else {
            self.weight
        }
    }
}

impl LgapDevice for Super5 {
    fn required_interval(&self) -> u32 {
        180
    }

    fn clone_box(&self) -> Box<dyn LgapDevice> {
        Box::new(self.clone())
    }
}

impl Fotable for Super5 {}



No aco_oper value
 ERROR lgap_comm::io_handler::serial > Time elapsed: 141ms
 WARN  lgap_comm                     > Failed to read: Read timeout: 140ms elapsed
 INFO  lgap_comm::device::odu::super5 > smart_plug_enable: 0**************88
 INFO  lgap_comm::device::odu::super5 > address: 0, smart_plug_enable: 0
 ERROR lgap_comm::data                > Cannot find data: "odu_type"
 ERROR lgap_comm                      > Failed to control value: Cannot find data: "odu_type"
 ERROR lgap_comm::io_handler::serial  > Time elapsed: 221ms
 WARN  lgap_comm                      > Failed to read: Read timeout: 220ms elapsed
 INFO  lgap_comm::device::odu::super5 > smart_plug_enable: 0**************88
 INFO  lgap_comm::device::odu::super5 > address: 6, smart_plug_enable: 0
 ERROR lgap_comm::data                > Cannot find data: "odu_type"
 ERROR lgap_comm                      > Failed to control value: Cannot find data: "odu_type"
 INFO  lgap_comm::device::odu::super5 > Super5 encode_cmde: odu_id: 21865, addr: 6, unit_id: 0, current_page: 0, port: 1
 INFO  lgap_comm::device::odu::super5 > *=====================unit_id: 0, current_page: 0=====================
 WARN  lgap_comm::data                > No smart_plug_enable value
 INFO  lgap_comm::device::odu::super5 > PDI smart_flag: 0, IDU count: 3
 ERROR lgap_comm::io_handler::serial  > Time elapsed: 221ms
 WARN  lgap_comm                      > Failed to read: Read timeout: 220ms elapsed
 INFO  lgap_comm::device::odu::super5 > Super5 encode_cmde: odu_id: 19478, addr: 0, unit_id: 0, current_page: 0, port: 0
 INFO  lgap_comm::device::odu::super5 > *=====================unit_id: 0, current_page: 0=====================
 WARN  lgap_comm::data                > No smart_plug_enable value
 INFO  lgap_comm::device::odu::super5 > PDI smart_flag: 0, IDU count: 3
 INFO  lgap_comm::device::odu::super5 > smart_plug_enable: 0**************88
 INFO  lgap_comm::device::odu::super5 > address: 6, smart_plug_enable: 0
 INFO  lgap_comm::device::odu::super5 > Super5 encode_cmde: odu_id: 19478, addr: 0, unit_id: 0, current_page: 0, port: 1
