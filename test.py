fn decode_cmd0(&mut self, bytes: Bytes) -> Result<()> {
        let mut bytes = bytes;
        let check_bytes = bytes.clone();

        let byte0 = bytes.get_u8();
        let length = byte0 & 0x7F;
        if length != 16 {
            return Err(anyhow!("IDU Cmd0 decode: invalid length: {length}"));
        }

        if bytes.remaining() < length as usize - 1 {
            return Err(anyhow!("IDU Cmd0 decode: invalid length"));
        }

        let byte1 = bytes.get_u8();
        let cmd = (byte1 >> 3) & 0x0F;
        if cmd != 0 {
            return Err(anyhow!("IDU Cmd0 decode: invalid cmd: {cmd}"));
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

        // byte 15
        let checksum = byte15;
        let expected_checksum = {
            let mut sum: u32 = 0;
            for byte in check_bytes[0..15].iter() {
                sum += *byte as u32;
            }
            ((sum ^ 0x55) & 0xff) as u8
        };

        if checksum != expected_checksum {
            return Err(anyhow!(
                "IDU Cmd0 decode: invalid checksum: {checksum} != {expected_checksum}"
            ));
        }

        self.connection_checker.reset_disconnect_count();
        let mut data_sets = DataSets::default();

        // byte 0
        let is_master = byte0 >> 7;
        if is_master != 0 {
            return Err(anyhow!("IDU Cmd0 decode: invalid is_master"));
        }

        // byte 1
        let oper = byte1 & 0x01;
        data_sets.set("oper", oper as f32);
        let lock = (byte1 >> 2) & 0x01;
        // TODO: if !self.hardlock 일 때만 값 업데이트
        data_sets.set("lock", lock as f32);
        let dot5 = (byte1 >> 7) & 0x01;

        // byte 2
        let product_code = byte2;
        if product_code != 0xA0 && product_code != 0xA3 {
            return Err(anyhow!(
                "IDU Cmd0 decode: invalid recv product_code: {product_code}"
            ));
        }
        if product_code == 0xA3 {
            self.slave_connection_checker.reset_disconnect_count();
        }

        // byte 3
        let product_code = byte3;
        if product_code <= 0x6F {
            self.product_code = product_code;
        } else {
            return Err(anyhow!(
                "IDU Cmd0 decode: invalid send product_code: {product_code}"
            ));
        }

        // byte 4
        let addr = byte4;
        if addr != self.addr {
            return Err(anyhow!("IDU Cmd0 decode: invalid addr: {addr}"));
        }

        // byte 5
        let err = byte5;
        // 백업운전 에러 173은 에러로 표시하지 말 것
        let err = if err == 173 { 0.0 } else { err as f32 };

        data_sets.set("err", err);
        if err != 0.0 {
            if let Err(e) =
                data_manager::facility::set_status(self.id, Status::MiscError(err as i32))
            {
                error!("Failed to set status: {e}");
            }
        }

        // 242 에러가 발생하면, 연결 끊김으로 판단
        if err == 242.0 {
            if let Err(e) = self.connection_checker.disconnected() {
                error!("IDU Cmd0 decode: connection_checker.disconnected error: {e}");
            }
        }

        // byte 6
        let mode = byte6 & 0x07;
        data_sets.set("mode", mode as f32);
        let fan = (byte6 >> 3) & 0x01;
        data_sets.set("swing", fan as f32);
        let fan_speed = (byte6 >> 4) & 0x07;
        data_sets.set("fan", fan_speed as f32);
        let _cycle = (byte6 >> 7) & 0x01;

        // byte 7
        let settemp = byte7 & 0x0F;
        let settemp = settemp as f32 + 15.0 + (dot5 as f32 * 0.5);
        if mode == 1 /* DRY */ || mode == 2
        /* FAN */
        {
            // DRY, FAN 모드에서는 settemp를 설정하지 않음
        } else {
            // ulim, llim 을 확인한다.
            data_sets.set("settemp", settemp);
        };
        let oil = (byte7 >> 4) & 0x01;
        data_sets.set("oil_alarm", oil as f32);
        let plasma = (byte7 >> 5) & 0x01;
        data_sets.set("plasma", plasma as f32);
        let cmd7 = (byte7 >> 6) & 0x01;
        self.cmd7_flag = cmd7 == 1;
        let filter_sign = (byte7 >> 7) & 0x01;
        data_sets.set("filter", filter_sign as f32);

        // Dokit인지 판단한다.
        // Dokit인 경우 Oper 값만 설정하고 나머지 값은 설정하지 않는다.
        if byte7 & 0xF0 == 0xF0 {
            data_table()
                .write()
                .set(DeviceType::Dokit, self.address(), "oper", oper as f32)?;

            return Ok(());
        }

        // byte 8
        let roomtemp = byte8;
        let roomtemp = get_roomtemp(roomtemp as usize)?;
        let roomtemp = if roomtemp < -99.0 {
            -99.0
        } else if roomtemp > 99.0 {
            99.0
        } else {
            roomtemp
        };
        data_sets.set("roomtemp", roomtemp);

        // byte 9
        let pipein_temp = byte9;
        let pipein_temp = get_pipetemp(pipein_temp)? as f32 / 10.0;
        data_sets.set("pipe_intemp", pipein_temp as f32);

        // byte 10
        let pipeout_temp = byte10;
        let pipeout_temp = get_pipetemp(pipeout_temp)? as f32 / 10.0;
        data_sets.set("pipe_outtemp", pipeout_temp);

        // byte 11
        let lev_low_byte = byte11;

        // byte 12
        let lev_high_byte = byte12;
        let lev = (lev_high_byte as u16) << 8 | lev_low_byte as u16;
        data_sets.set("lev", lev as f32);

        // byte 13
        let capa = byte13;
        data_sets.set("capa", capa as f32);

        // byte 14
        let _sum_qj = byte14;

        // ACO 로직 처리
        let aco_enable = config().read().aco_enable;
        data_sets.set("aco_enable", aco_enable as u8 as f32);
        let aco_oper = data_sets.get("aco_oper") as u8;
        if mode == 0 /* COOL */ && aco_oper == 1 && aco_enable {
            let mut aco_upper = settemp;

            let mut aco_lower = data_sets.get("aco_lower");
            if aco_upper <= aco_lower {
                aco_lower = aco_upper - 1.0 /* aco_delta */;
            }

            if aco_lower < 18.0 {
                aco_lower = 18.0;
                aco_upper = aco_lower + 1.0 /* aco_delta */;
            }

            data_table()
                .write()
                .set(DeviceType::Idu, self.address(), "aco_upper", aco_upper)?;

            data_table()
                .write()
                .set(DeviceType::Idu, self.address(), "aco_lower", aco_lower)?;

            data_table()
                .write()
                .flush(DeviceType::Idu, self.address(), None);
        } else if mode == 4 /* HEAT */ && aco_oper == 1 && aco_enable {
            let mut aco_lower = settemp;

            let mut aco_upper = data_sets.get("aco_upper");
            if aco_upper <= aco_lower {
                aco_upper = aco_lower + 1.0 /* aco_delta */;
            }

            if aco_upper > 30.0 {
                aco_upper = 30.0;
                aco_lower = aco_upper - 1.0 /* aco_delta */;
            }

            data_table()
                .write()
                .set(DeviceType::Idu, self.address(), "aco_upper", aco_upper)?;

            data_table()
                .write()
                .set(DeviceType::Idu, self.address(), "aco_lower", aco_lower)?;

            data_table()
                .write()
                .flush(DeviceType::Idu, self.address(), None);
        }

        // CMD4에 대한 처리 진행
        if self.cmd4_flag {
            let cmd4_data_sets = data_table()
                .read()
                .gets(DeviceType::Idu, self.address())
                .unwrap_or_default();

            let cmd4_values = [
                "settemplock",
                "fanlock",
                "modelock",
                "settemp_llim",
                "fan_direction",
                "settemp_ulim",
            ];

            for value in cmd4_values.iter() {
                data_sets.set(value, cmd4_data_sets.get(value));
            }

            self.cmd4_flag = false;
        }

        data_table()
            .write()
            .sets(DeviceType::Idu, self.address(), data_sets)?;

        Ok(())
    }

이 코드에서 settemp 할 때 settemp_llim,settemp_ulim  을 확인하고 상하한을 맞춰야하는데 .. 코드를 어떻게 수정하면 될까
