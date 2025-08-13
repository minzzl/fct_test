    fn decode_super5_page38to3c(&mut self, bytes: Bytes) -> Result<()> {
        info!("*******************ODU super5 page38to3c decode is not implemented yet");

        info!("addr: {}, product_code: {}", self.odu_addr, self.product_code);

        let odu_data_sets = data_table()
        .read()
        .gets(DeviceType::OduUnit, self.address())
        .unwrap_or_default();

        let smart_plug_enable = odu_data_sets.get("smart_plug_enable") as f32;

        info!(
            "ODU super5 page38to3c decode: smart_plug_enable: {}",
            smart_plug_enable
        );

        //smart_plug_enable 이 true 일 때만 해석함
        if smart_plug_enable == 0.0 {
            return Ok(());
        }

        let mut bytes = bytes;
        let check_bytes = bytes.clone();

        let byte0 = bytes.get_u8();
        let length = byte0 & 0x7F;
        if length != 0x40 {
            return Err(anyhow!(
                "ODU super5 page38to3c decode: invalid length: {length}"
            ));
        }

        if bytes.remaining() < length as usize - 1 {
            return Err(anyhow!("ODU super5 page38to3c decode: invalid length"));
        }

        let byte1 = bytes.get_u8();
        let cmd = (byte1 >> 3) & 0x0F;
        if cmd != 0xe {
            return Err(anyhow!("ODU super5 page38to3c decode: invalid cmd: {cmd}"));
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
        let page = byte5;

        // byte 10
        let idu_count_total = byte10 as u32;

        // 이 페이지에 실리는 IDU 개수 계산
        let idu_count_in_this_page: u32 = match page {
            0x38 => { if idu_count_total <= 13 { idu_count_total } else { 13 } }
            0x39 => { if idu_count_total <= 26 { idu_count_total - 13 } else { 13 } }
            0x3A => { if idu_count_total <= 39 { idu_count_total - 26 } else { 13 } }
            0x3B => { if idu_count_total <= 52 { idu_count_total - 39 } else { 13 } }
            0x3C => { if idu_count_total <= 64 { idu_count_total - 52 } else { 12 } }
            _    => 0,
        };

        for i in 0..(idu_count_in_this_page as usize) {
            let off = base + i * 4;
            let idu_addr  = check_bytes[off] as u32;
            let pwr_upper = check_bytes[off + 1] as u32;
            let pwr_mid   = check_bytes[off + 2] as u32;
            let pwr_low   = check_bytes[off + 3] as u32;
            let power     = (pwr_upper << 16) | (pwr_mid << 8) | pwr_low;
                
            data_sets.set("power", accum_power as f32 / 10.0);

            data_table()
            .write()
            .sets(DeviceType::Idu, idu_addr, data_sets)?;

        }
        Ok(())
    }
      
}

여기서 base 이런거 쓸 필요없이 byte11 쓰면 되는거 아닐까?
