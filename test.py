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
        } else if product_code == 0xA7 {
            self.slave_connection_checker.reset_disconnect_count();
        } else {
            return Err(anyhow!(
                "AWHP Cmd0 decode: invalid send product_code: {product_code}"
            ));
        }

지금 이런식으로 되어있는 코드에서 

is_unknown 값이 false 일때 아래와 같이 장치 타입을 설정하는 api 를 호출해서 장치 타입을 수동 설정해줘야하거든 

if self.is_unknown {
                // ODU 타입이 설정되지 않은 경우 QuickInstall을 수행
                let mut device_info = Self::decode_search(bytes, self.addr)?;
                let facility_info = data_manager::facility::get(self.id)?;
                device_info.name = facility_info.name.clone();
                device_info.facility_id = Some(self.id);

                if let Err(e) = quick_install::install_lgap(
                    device_info.into_lgap_install_info(self.port, LgapType::Odu),
                ) {
                    error!("Failed to install LGAP device: {e}");
                }
            }
            // 추가적인 QuickInstall 요청을 보내지 않도록 아래 플래그 설정
            self.is_unknown = false;
        }

0x80, 0x82, 0x83 이면 singAwhp로,
0x81 이면 heatOnlyAwhp로,
0x86 이면 GHU
0x87 이면 EHU
0x88 이면 Hydrokit 
0x89 이면 casecade 

(이름은 무조건 camelcase)




