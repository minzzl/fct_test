==474079== 128 bytes in 1 blocks are definitely lost in loss record 285 of 350                                                                                   
==474079==    at 0x487A410: calloc (vg_replace_malloc.c:1328)                                                                                                    
==474079==    by 0x119EB7: Create_PopUp_Input (NetworkInfoPage.c:399)                                                                                            
==474079==    by 0x497EBBF: lv_event_send (in /usr/lib/liblvgl.so.9.1.0)                                                                                         
==474079==    by 0x49130A7: ??? (in /usr/lib/liblvgl.so.9.1.0)                                                                                                   
==474079==    by 0x491317F: lv_obj_send_event (in /usr/lib/liblvgl.so.9.1.0)                                                                                     
==474079==    by 0x497EBBF: lv_event_send (in /usr/lib/liblvgl.so.9.1.0)                                                                                         
==474079==    by 0x49130A7: ??? (in /usr/lib/liblvgl.so.9.1.0)                                                                                                   
==474079==    by 0x491317F: lv_obj_send_event (in /usr/lib/liblvgl.so.9.1.0)                                                                                     
==474079==    by 0x113647: EventStateMachineProc (App.c:1464)                                                                                                    
==474079==    by 0x113647: EventStateMachineProc (App.c:1188)                                                                                                    
==474079==    by 0x497EBBF: lv_event_send (in /usr/lib/liblvgl.so.9.1.0)                                                                                         
==474079==    by 0x49130A7: ??? (in /usr/lib/liblvgl.so.9.1.0)                                                                                                   
==474079==    by 0x491317F: lv_obj_send_event (in /usr/lib/liblvgl.so.9.1.0)                                                                                     
==474079==                                                                                                                                                       
==474079== 128 bytes in 1 blocks are definitely lost in loss record 286 of 350                                                                                   
==474079==    at 0x487A410: calloc (vg_replace_malloc.c:1328)                                                                                                    
==474079==    by 0x119EB7: Create_PopUp_Input (NetworkInfoPage.c:399)                                                                                            
==474079==    by 0x497EBBF: lv_event_send (in /usr/lib/liblvgl.so.9.1.0)                                                                                         
==474079==    by 0x49130A7: ??? (in /usr/lib/liblvgl.so.9.1.0)                                                                                                   
==474079==    by 0x491317F: lv_obj_send_event (in /usr/lib/liblvgl.so.9.1.0)                                                                                     
==474079==    by 0x497EBBF: lv_event_send (in /usr/lib/liblvgl.so.9.1.0)                                                                                         
==474079==    by 0x49130A7: ??? (in /usr/lib/liblvgl.so.9.1.0)                                                                                                   
==474079==    by 0x491317F: lv_obj_send_event (in /usr/lib/liblvgl.so.9.1.0)                                                                                     
==474079==    by 0x113767: EventStateMachineProc (App.c:1519)                                                                                                    
==474079==    by 0x113767: EventStateMachineProc (App.c:1188)                                                                                                    
==474079==    by 0x497EBBF: lv_event_send (in /usr/lib/liblvgl.so.9.1.0)                                                                                         
==474079==    by 0x49130A7: ??? (in /usr/lib/liblvgl.so.9.1.0)                                                                                                   
==474079==    by 0x491317F: lv_obj_send_event (in /usr/lib/liblvgl.so.9.1.0)                                                                                     
==474079==                                                                                                                                                       
==474079== 128 bytes in 1 blocks are definitely lost in loss record 287 of 350                                                                                   
==474079==    at 0x487A410: calloc (vg_replace_malloc.c:1328)                                                                                                    
==474079==    by 0x119EB7: Create_PopUp_Input (NetworkInfoPage.c:399)                                                                                            
==474079==    by 0x497EBBF: lv_event_send (in /usr/lib/liblvgl.so.9.1.0)                                                                                         
==474079==    by 0x49130A7: ??? (in /usr/lib/liblvgl.so.9.1.0)                                                                                                   
==474079==    by 0x491317F: lv_obj_send_event (in /usr/lib/liblvgl.so.9.1.0)                                                                                     
==474079==    by 0x497EBBF: lv_event_send (in /usr/lib/liblvgl.so.9.1.0)                                                                                         
==474079==    by 0x49130A7: ??? (in /usr/lib/liblvgl.so.9.1.0)                                                                                                   
==474079==    by 0x491317F: lv_obj_send_event (in /usr/lib/liblvgl.so.9.1.0)                                                                                     
==474079==    by 0x1135F7: EventStateMachineProc (App.c:1416)                                                                                                    
==474079==    by 0x1135F7: EventStateMachineProc (App.c:1188)                                                                                                    
==474079==    by 0x497EBBF: lv_event_send (in /usr/lib/liblvgl.so.9.1.0)                                                                                         
==474079==    by 0x49130A7: ??? (in /usr/lib/liblvgl.so.9.1.0)                                                                                                   
==474079==    by 0x491317F: lv_obj_send_event (in /usr/lib/liblvgl.so.9.1.0)  

void Create_PopUp_Input(POPUP_ID ePopupId)
{
    lv_ui* ui = Ui_GetInstance();

    CreatePopupWindow(ePopupId);

	switch (ePopupId)
	{
		case POP_ID_NETWORK_INFO_SET_IP:
			ui->mpPopupPage->mPopData.mushLblInformation_TR = TR_INPUT_IP;
			break;
		case POP_ID_NETWORK_INFO_SET_GW:
			ui->mpPopupPage->mPopData.mushLblInformation_TR = TR_INPUT_GW;
			break;
		case POP_ID_NETWORK_INFO_SET_SM:
			ui->mpPopupPage->mPopData.mushLblInformation_TR = TR_INPUT_SUBNET;
			break;
		// case POP_ID_NETWORK_INFO_SET_DNS:
		// 	ui->mpPopupPage->mPopData.mushLblInformation_TR = TR_INPUT_DNS;
		// 	break;
		default:
			printf("의도하지 않은 POPID\n");
			break;
	}
 
    // 버튼 배열 할당 (0-9까지 10개 + 지움 버튼 1개 + 취소 + 다음)
    ui->mpPopupPage->mPopData.BtnMatrixMap = calloc(17, sizeof(char*));
    ui->mpPopupPage->mPopData.mucDynamicBtnCount = 16;

    //버튼 배열 초기화
    const char * kb_map[] = {
        "1", "2", "3", "4", "5", LV_SYMBOL_BACKSPACE, "\n",
         "6", "7", "8", "9", "0",LV_SYMBOL_NEW_LINE,"\n",
        textData[TR_CANCEL], textData[TR_NEXT],""
    };

    // kb_map을 사용하여 버튼 배열 설정
    for (int i = 0; i < sizeof(kb_map) / sizeof(kb_map[0]); i++) {
        ui->mpPopupPage->mPopData.BtnMatrixMap[i] = calloc(strlen(kb_map[i]) + 1, sizeof(char));
        strcpy(ui->mpPopupPage->mPopData.BtnMatrixMap[i], kb_map[i]);
    }

    PopKeypadBtn(&ui->mpPopupPage->mPopData);

	// 모든 입력 칸에 대해 이벤트 콜백 추가
    lv_obj_add_event_cb(ui->mpPopupPage->mpBtnMatrix, EventPopUpProc, LV_EVENT_CLICKED, ui->mpPopupPage->mpTextBoxes);

    lv_btnmatrix_set_selected_btn(ui->mpPopupPage->mpBtnMatrix, 0);

	ui->mpPopupPage->mPopData.btn_status = (BtnStatus *)calloc(ui->mpPopupPage->mPopData.mucDynamicBtnCount, sizeof(BtnStatus));


	for(uint32_t i = 0; i < ui->mpPopupPage->mPopData.mucDynamicBtnCount; i++)
	{
		ui->mpPopupPage->mPopData.btn_status[i].index = i;
		ui->mpPopupPage->mPopData.btn_status[i].is_disabled = false;
		
	}

	// 두 번째 버튼 비활성화
	lv_buttonmatrix_set_button_ctrl(ui->mpPopupPage->mpBtnMatrix, 5, LV_BUTTONMATRIX_CTRL_DISABLED);
	ui->mpPopupPage->mPopData.btn_status[5].is_disabled = true;
	// 두 번째 버튼 비활성화
	lv_buttonmatrix_set_button_ctrl(ui->mpPopupPage->mpBtnMatrix, 11, LV_BUTTONMATRIX_CTRL_DISABLED);
	ui->mpPopupPage->mPopData.btn_status[11].is_disabled = true;
	// 두 번째 버튼 비활성화
	lv_buttonmatrix_set_button_ctrl(ui->mpPopupPage->mpBtnMatrix, 13, LV_BUTTONMATRIX_CTRL_DISABLED);
	ui->mpPopupPage->mPopData.btn_status[13].is_disabled = true;
}
