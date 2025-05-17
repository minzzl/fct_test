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

void PopTitleQRInfoBtn(PopupData*pPopupData)
{
	lv_ui*ui=Ui_GetInstance();

	ui->mScreenType=SCR_TYPE_POPUP;
	pPopupData->ePopType = POP_TYPE_TITLE_QR_INFO_BTN;

	ui->mpPopupPage->mpLayoutTitle = CreateLayout(ui->mpPopupPage->mpPageWindowArea, LV_ALIGN_TOP_MID, 0, 0, 320, 45);

	ui->mpPopupPage->mpLabelTitle = CreateText(ui->mpPopupPage->mpLayoutTitle, pPopupData->mushTitle_TR, LV_ALIGN_BOTTOM_MID, 0, 0);

	lv_obj_set_style_text_font(ui->mpPopupPage->mpLabelTitle, &KR_FONT_24B, LV_PART_MAIN | LV_STATE_DEFAULT);

	ui->mpPopupPage->mpLayoutQRCode = CreateLayout(ui->mpPopupPage->mpPageWindowArea, LV_ALIGN_CENTER, 0, 0, 80, 80);

	lv_obj_set_style_bg_opa(ui->mpPopupPage->mpLayoutQRCode, 255, LV_PART_MAIN);

	lv_obj_set_style_radius(ui->mpPopupPage->mpLayoutQRCode, 5, LV_PART_MAIN);

	ui->mpPopupPage->mpQRCode=CreateQR(ui->mpPopupPage->mpLayoutQRCode, pPopupData->QRString, 75, LV_ALIGN_CENTER,0,0);

	lv_obj_align_to(ui->mpPopupPage->mpLayoutQRCode, ui->mpPopupPage->mpLayoutTitle, LV_ALIGN_OUT_BOTTOM_MID, 0, 7);

	ui->mpPopupPage->mpLayoutQRInfoText = CreateLayout(ui->mpPopupPage->mpPageWindowArea, LV_ALIGN_CENTER, 0, 0, 320, 52);

	ui->mpPopupPage->mpLabelInformation = CreateText(ui->mpPopupPage->mpLayoutQRInfoText, pPopupData->mushQRInfo_TR,LV_ALIGN_CENTER,0,0);

	lv_obj_set_style_text_font(ui->mpPopupPage->mpLabelInformation, &KR_FONT_18M, LV_PART_MAIN | LV_STATE_DEFAULT);

	lv_obj_align_to(ui->mpPopupPage->mpLayoutQRInfoText, ui->mpPopupPage->mpLayoutQRCode, LV_ALIGN_OUT_BOTTOM_MID, 0, 4);

	ui->mpPopupPage->mpBtnCancel=CreateButton(ui->mpPopupPage->mpPageWindowArea,pPopupData->mushBtnCancle_TR,LV_ALIGN_BOTTOM_MID,0,0);


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


뭔가 기존에 이런식해서 화면 전환 될때  DestroyPopup 을 호출해서 동적 메모리 할당하려고 했는데,, 뭔가 부족한 부분이 있는 것 같아
