fn get_config_impl() -> Result<Value> {
    let config = crate::config::config().read();
    let config = serde_json::to_value(&*config)?;

    Ok(config)
}

fn set_config_impl(payload: &str) -> Result<()> {
    #[derive(Debug, Deserialize)]
    #[serde(rename_all = "camelCase")]
    struct Payload {
        pdi: Option<bool>,
        gdi: Option<bool>,
        slave: Option<bool>,
        slave_lock: Option<bool>,
        cycle_monitor: Option<bool>,
        cycle_control: Option<bool>,
        aco_enable: Option<bool>,
        tempdiff: Option<f32>,
    }
    let payload = serde_json::from_str::<Payload>(payload)?;

    if let Some(pdi) = payload.pdi {
        crate::config::config().write().pdi = pdi;
    }

    if let Some(gdi) = payload.gdi {
        crate::config::config().write().gdi = gdi;
    }

    if let Some(slave) = payload.slave {
        crate::config::config().write().slave = slave;
    }

    if let Some(slave_lock) = payload.slave_lock {
        crate::config::config().write().slave_lock = slave_lock;
    }

    if let Some(cycle_monitor) = payload.cycle_monitor {
        crate::config::config().write().cycle_monitor = cycle_monitor;
    }

    if let Some(cycle_control) = payload.cycle_control {
        crate::config::config().write().cycle_control = cycle_control;
    }

    if let Some(aco_enable) = payload.aco_enable {
        crate::config::config().write().aco_enable = aco_enable;
    }

    if let Some(tempdiff) = payload.tempdiff {
        crate::config::config().write().tempdiff = tempdiff;
    }

    save_config()?;

    Ok(())
}

pub fn save_config() -> Result<()> {
    let config = config().write();

    let yaml = serde_yaml::to_string(&*config)?;
    std::fs::write("config.yaml", yaml)?;

    Ok(())
}


이런식으로 CONFIG 에 저장이 되고 있는데, 내가 지금 확인하고 싶은거는 PDI 가 TRUE 이냐, FALSE 냐 이야ㅣ 

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

여기서 PDI가 FALSE 일 때만 0x38 | 0x39 | 0x3A | 0x3B | 0x3C = 부분을 파싱하면 되는거거든 어떻게 decode_super5 부분에 코드를 추가해야할까?? 
