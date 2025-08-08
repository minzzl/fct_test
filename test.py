// byte 3
        let product_code = byte3;
        if (0x80..=0x89).contains(&product_code) {
            self.product_code = product_code;

            // 멀티 V 연동 AWHP 프로토콜인지 체크
            if product_code >= 0x86 {
                self.multi_v_flag = true;
            } else {
                self.multi_v_flag = false;
                // HPWH인 경우, 멀티 V 연동 AWHP 프로토콜로 판단
                if self.is_hpwh {
                    self.multi_v_flag = true;
                }
            }

             // is_unknown == false일 때 장치 타입 수동 설정
            if !self.is_unknown {
                let device_type = match product_code {
                    0x80 | 0x82 | 0x83 => "singleAwhp",
                    0x81               => "heatOnlyAwhp",
                    0x86               => "GHU",
                    0x87               => "EHU",
                    0x88               => "hydrokit",
                    0x89               => "casecade",
                    _                  => "unknown",
                };

                if let Err(e) = data_manager::facility::set_sub_type(
                    self.id,
                    device_type,
                ){
                    error!("Failed to set awhp subtype device: {e}");
                }
            }
        } else if product_code == 0xA7 {
            self.slave_connection_checker.reset_disconnect_count();
        } else {
            return Err(anyhow!(
                "AWHP Cmd0 decode: invalid send product_code: {product_code}"
            ));
        }

   Compiling lgap_comm v0.5.0 (/home/root/app.lgap_comm)
error[E0308]: mismatched types
   --> src/device/awhp.rs:496:21
    |
494 |                 if let Err(e) = data_manager::facility::set_sub_type(
    |                                 ------------------------------------ arguments to this function are incorrect
495 |                     self.id,
496 |                     device_type,
    |                     ^^^^^^^^^^^- help: try using a conversion method: `.to_string()`
    |                     |
    |                     expected `String`, found `&str`
    |
