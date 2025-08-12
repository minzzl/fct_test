

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
        
        info!("=====================unit_id: {}, current_page: {}=====================", self.unit_id, page);
        let pdi_enabled = config().read().pdi;
        //  실내기 개수를 카운트한다
        let facilities = data_manager::facility::get_list_by_type(
            &FacilityType::Physical("idu".to_string()),
        )
        .unwrap_or_default();
        let idu_count = facilities.len() as u8;

        info!("PDI enabled: {}, IDU count: {}", pdi_enabled, idu_count);

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
                self.current_page = if self.unit_id == 1 { 0 } else { self.unit_id } + 0x33;
                self.weight = 9999; // 무조건 다음 page에 대한 정보를 받기 위해 weight를 최대로 설정
            }
            0x38 | 0x39 | 0x3A | 0x3B | 0x3C => {
                // PDI 설정 여부에 따라 페이지를 다르게 설정
                info!("pdi: {}", config().read().pdi);
                if config().read().pdi {
                    // idu count 를 계산한다.
                    
                    self.current_page = if self.unit_id == 1 { 0 } else { self.unit_id } + 0x40;
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


여기서 

 0x38 | 0x39 | 0x3A | 0x3B | 0x3C => {
                // PDI 설정 여부에 따라 페이지를 다르게 설정
                info!("pdi: {}", config().read().pdi);
                if config().read().pdi {
                    // idu count 를 계산한다.
                    
                    self.current_page = if self.unit_id == 1 { 0 } else { self.unit_id } + 0x40;
                } 
            }

이 부분을 수정해야해. 

각 page별 송신할 실내기 대수 : 실내기page 0x38~0x3B: 13개 실내기 , page 0x3C: 12개 실내기

이렇게 인데 실내기 개수에 따라서 요청을 해야할 거 ㅅ같아ㅣ 지금이 요청하는 코드거든? 
얘를들어 총 idu 가 13대이면 0x38 까지만 요청하면되고 만약 17대면 0x38, 0x39 까지, 뭐 이런식으로 각 페이지별로 13대씩가지고 있을 수 있고 0x3c 페이지에서는 12대까지만이긴한데 아무튼 이런식으로 ..idu_count 카운트 값을 이용하면 될 것 같아. 이때 pdi_enabled 이 true로 되어있어야해 
