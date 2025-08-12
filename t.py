
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
                self.current_page = if self.unit_id == 1 { 0 } else { self.unit_id } + 0x40;
                self.weight = 9999; // 무조건 다음 page에 대한 정보를 받기 위해 weight를 최대로 설정
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
            _ => Err(anyhow!("Invalid super5 page: {}", page)),
        }
    }

사실 최초에 이런식으로 되어 있었는데, 내가 0X38 계열을 추가하면서 좀 수정을 한거거든? 괜찮아보여?
