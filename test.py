==468552== 368 bytes in 1 blocks are definitely lost in loss record 284 of 316                                                                                   
==468552==    at 0x487A410: calloc (vg_replace_malloc.c:1328)                                                                                                    
==468552==    by 0x110E23: CreatePopupWindow (App.c:462)                                                                                                         
==468552==    by 0x114B2B: Create_PopUp_Waiting_for_Connection_Dispaly_QR (ConnectApp.c:259)                                                                     
==468552==    by 0x497EBBF: lv_event_send (in /usr/lib/liblvgl.so.9.1.0)                                                                                         
==468552==    by 0x49130A7: ??? (in /usr/lib/liblvgl.so.9.1.0)                                                                                                   
==468552==    by 0x491317F: lv_obj_send_event (in /usr/lib/liblvgl.so.9.1.0)                                                                                     
==468552==    by 0x11A5BB: progressScreenTransitHandler (Popups.c:616)                                                                                           
==468552==    by 0x4988457: lv_timer_handler (in /usr/lib/liblvgl.so.9.1.0)                                                                                      
==468552==    by 0x10D94B: main (main.c:131)   

void Create_PopUp_Waiting_for_Connection_Dispaly_QR(POPUP_ID ePopupId)
{
	lv_ui*ui=Ui_GetInstance();

	CreatePopupWindow(ePopupId);

	ui->mpPopupPage->mPopData.mushTitle_TR = TR_TITLE_CONNECTION_PREPRATION;

	AppConnect_Status* AppStatus=Get_AppConnect_Status();

	ui->mpPopupPage->mPopData.QRString = AppStatus->QR;//QRString;
	ui->mpPopupPage->mPopData.mushQRInfo_TR = TR_APP_CONNECT_QR_INFO;
	ui->mpPopupPage->mPopData.mushBtnCancle_TR = TR_CANCEL;

	PopTitleQRInfoBtn(&ui->mpPopupPage->mPopData);

	lv_obj_add_event_cb(ui->mpPopupPage->mpBtnCancel,EventPopUpProc,LV_EVENT_CLICKED,NULL);

	ui->mEventTimers.mpTimerConnectAppWaiting=lv_timer_create(TimerEventsConnectAppWaiting,APP_CONNECT_POLL_TIME,NULL);

}

void  CreatePopupWindow(POPUP_ID ePopupId)
{
#if 1
	/* Init Popup  */
	lv_ui*ui=Ui_GetInstance();
	static bool bOnce=true;
	static lv_style_t style_Page;
	if(bOnce){
		lv_style_init(&style_Page);
		lv_style_set_border_width(&style_Page, DEVELOPER_OPT);
		lv_style_set_radius(&style_Page,0);
		bOnce=false;
	}

	ui->mpPopupPage=calloc(1,sizeof(ui_Popup));

	ui->mpPopupPage->mpPageWindowArea  = lv_obj_create(lv_scr_act());
	lv_obj_set_size(ui->mpPopupPage->mpPageWindowArea, SCREEN_WIDTH-1, SCREEN_HEIGHT-1);
	lv_obj_align(ui->mpPopupPage->mpPageWindowArea, LV_ALIGN_CENTER, 0, 0);
	lv_obj_set_scrollbar_mode(ui->mpPopupPage->mpPageWindowArea,LV_SCROLLBAR_MODE_OFF);
	lv_obj_remove_flag(ui->mpPopupPage->mpPageWindowArea, LV_OBJ_FLAG_SCROLLABLE);      
	lv_obj_add_style(ui->mpPopupPage->mpPageWindowArea, &style_Page,0);
	lv_obj_set_style_bg_color(ui->mpPopupPage->mpPageWindowArea, lv_color_make(COLOR_BLACK_RGB), LV_PART_MAIN);	

	if(ui->mucPopupCount==0)
	{
		ui->mpPopupPages=calloc(1,sizeof(ui_Popup*));
		ui->mpActivePopupIds=calloc(1,sizeof(UINT8));
	}
	else
	{
		ui->mpPopupPages=realloc(ui->mpPopupPages,sizeof(ui_Popup*)*(ui->mucPopupCount+1));
		ui->mpActivePopupIds=realloc(ui->mpActivePopupIds,sizeof(UINT8)*(ui->mucPopupCount+1));
	}
	ui->mucPopupCount++;
	ui->mpActivePopupIds[ui->mucPopupCount-1]=ePopupId;
	ui->mpPopupPages[ui->mucPopupCount-1]=ui->mpPopupPage;

	ui->mpPopupPage->mPopData.ePopId=ePopupId;
#if 1
	lv_obj_set_style_pad_left(ui->mpPopupPage->mpPageWindowArea, WIDGET_PADDING);
	lv_obj_set_style_pad_right(ui->mpPopupPage->mpPageWindowArea, WIDGET_PADDING);
	lv_obj_set_style_pad_top(ui->mpPopupPage->mpPageWindowArea, WIDGET_PADDING);
	lv_obj_set_style_pad_bottom(ui->mpPopupPage->mpPageWindowArea, WIDGET_PADDING);
#endif

#endif
}

static void progressScreenTransitHandler(lv_timer_t * timer) {
    progressTransit_data* data = (progressTransit_data*)timer->user_data; // 사용자 데이터를 통해 TimerData 구조체를 가져옴
    lv_ui* ui = data->ui; // UI 객체 가져오기

    // 다음 화면으로 전환하는 로직
    UpdateState(data->ePopupId_now, data->ePopupId_next, data->ePopupId_next_next, SCR_TYPE_POPUP);
    lv_obj_send_event(ui->mpEventStateSwitch, LV_EVENT_CLICKED, NULL);

    // 타이머 삭제
    lv_timer_del(timer);
	free(data); // 메모리 해제
}

void UpdateState(UINT16 ushPrevious,UINT16 ushCurrent, UINT16 ushNextState,UINT16 ushScreenType)
{
	printf("UpdateState\n");
	lv_ui*ui=Ui_GetInstance();
	ui->mScreenType = ushScreenType;
	ui->mUiState.mucPreviousState = ushPrevious;
	ui->mUiState.mucCurrentState = ushCurrent;
	ui->mUiState.mucNextState = ushNextState;
	lv_log("Updated States ScrType: %d prev: %d, current:%d, next:%d\n",ushScreenType,ui->mUiState.mucPreviousState,ui->mUiState.mucCurrentState,ui->mUiState.mucNextState);

	DestroyPopup(ushPrevious);
}

void DestroyPopup(UINT16 ulPopId)
{
	INT16 ind=-1;
	lv_ui*ui=Ui_GetInstance();
	for(int i=0;i<ui->mucPopupCount;i++)
	{
		if(ui->mpActivePopupIds[i]==ulPopId)
		{
			ind=i;
			break;
		}
	}
	if(ind!=-1)
	{
		
	
		lv_obj_del(ui->mpPopupPages[ind]->mpPageWindowArea);
		
		if(ui->mpPopupPages[ind]->mPopData.ePopType==POP_TYPE_OPENSOURCE || ui->mpPopupPages[ind]->mPopData.ePopType==POP_TYPE_TITLE_INFO_OK_CANCEL_BTN || ui->mpPopupPages[ind]->mPopData.ePopType==POP_TYPE_INFO_BTN_DYNAMIC || ui->mpPopupPages[ind]->mPopData.ePopType==POP_TYPE_KEYBOARD )
		{
			if(ui->mpPopupPages[ind]->mPopData.BtnMatrixMap){
				int i=0;
				for(i;ui->mpPopupPages[ind]->mPopData.BtnMatrixMap[i][0]!='\0';i++)
				{
					free(ui->mpPopupPages[ind]->mPopData.BtnMatrixMap[i]);
				}
				free(ui->mpPopupPages[ind]->mPopData.BtnMatrixMap[i]);
			}
		}
		else if(ui->mpPopupPages[ind]->mPopData.ePopType==POP_TYPE_INFO_PROGRESS||POP_TYPE_TITLE_PROGRESS_BTN||POP_TYPE_TITLE_QR_INFO_BTN)
		{
			
		}
		for(int i=ind;i<ui->mucPopupCount;i++)
		{
			ui->mpPopupPages[i]=ui->mpPopupPages[i+1];
			ui->mpActivePopupIds[i]=ui->mpActivePopupIds[i+1];
		}
		ui->mpPopupPages=realloc(ui->mpPopupPages,sizeof(ui_Popup*)*(ui->mucPopupCount-1));
		ui->mpActivePopupIds=realloc(ui->mpActivePopupIds,sizeof(UINT8)*(ui->mucPopupCount-1));
		ui->mucPopupCount--;
		
		if(ui->mucPopupCount==0)
		{
			ui->mpActivePopupIds=NULL;
			ui->mpPopupPages=NULL;
			ui->mpPopupPage=NULL;
			ui->mScreenType=SCR_TYPE_PAGE;
		}
		else
		{
			ui->mpPopupPage=ui->mpPopupPages[ui->mucPopupCount-1];
		}

	}


}
