    fn decode_super5_page38to3c(&mut self, bytes: Bytes) -> Result<()> {
        info!("*******************ODU super5 page38to3c decode is not implemented yet");

        info!("addr: {}, product_code: {}", self.odu_addr, self.product_code);

        let odu_data_sets = data_table()
        .read()
        .gets(DeviceType::Odu, self.address())
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
        let _page = byte5;

        // byte 10
        let idu_count = byte as u32;
        
        






        Ok(())
    }
      
}

이 코드에 // byte 10 에 실내기 대수가 있어. page에 따라 다르긴한데, 12개 혹은 13개이고 그 이후부터는 실내기 주소랑 누적전력이 전달되. 이거의 c 코드는 다음과 같아. 비슷하게 idu_count 에 따라서 값을 파싱하도록 코드를 추가해야해

int ProcessRxDataFromODUPage0_Smart(char *odu_addr, uchar *rs485buf_rx,psqlite3 pdb, int port)
{
	DEF_MON_ODU_CMDE_SMART_PLUG rcv_from_odu;
	//char odu_type[30] = { 0, };
	memcpy((char *) &rcv_from_odu, (char *) rs485buf_rx, 64);

	int page = rcv_from_odu.page;
	int i;
	int addr;
	unsigned int power = 0;
	int idu_cnt_total = 0;
	int idu_cnt_in_this_page = 0;
	int current_or_accm = 0;		//1 순시 , 0 누적을 의미함.

	if(page <= 0x37) //page 0x33 ~ 0x37 순시 소전량, page 0x38 ~ 0x3C 누적 소전량
		current_or_accm = 1;

	//사실 ODU가 page에 12 값을 줄 것 같긴 하지만 혹시 모르니까..
//	if(page == 0x37 || page == 0x3C)
//		idu_cnt = 12;

	idu_cnt_total = rcv_from_odu.idu_count;

	if (page == 0x33 || page == 0x38)
	{
		if (idu_cnt_total <= 13)
			idu_cnt_in_this_page = idu_cnt_total;
		else
			idu_cnt_in_this_page = 13;
	}
	else if (page == 0x34 || page == 0x39)
	{
		if (idu_cnt_total <= 26)
			idu_cnt_in_this_page = idu_cnt_total - 13;
		else
			idu_cnt_in_this_page = 13;
	}
	else if (page == 0x35 || page == 0x3A)
	{
		if (idu_cnt_total <= 39)
			idu_cnt_in_this_page = idu_cnt_total - 26;
		else
			idu_cnt_in_this_page = 13;
	}
	else if (page == 0x36 || page == 0x3B)
	{
		if (idu_cnt_total <= 52)
			idu_cnt_in_this_page = idu_cnt_total - 39;
		else
			idu_cnt_in_this_page = 13;
	}
	else if (page == 0x37 || page == 0x3C)
	{
		if (idu_cnt_total <= 64)
			idu_cnt_in_this_page = idu_cnt_total - 52;
		else
			idu_cnt_in_this_page = 12;
	}
	else
		printf("Not supported page!!!\n");


	for(i=0; i<idu_cnt_in_this_page; i++)
	{
		addr = rcv_from_odu.idu_info[i].idu_addr;
		power = (rcv_from_odu.idu_info[i].idu_power_upper << 16 ) | (rcv_from_odu.idu_info[i].idu_power_middle << 8 ) | (rcv_from_odu.idu_info[i].idu_power_lower);

		//pinfo 에다가만 값을 써놓으면 pwrdist 가 알아서 디비에 적는다.

		if(current_or_accm)		// 순시
			pinfo->monitor.pdi[addr].pwrInst = power;
		else
			pinfo->monitor.pdi[addr].pwrAccm = power;

	}
	return 0;
}

나는 0x38 ~ 3c까지만 확인하면 돼.
