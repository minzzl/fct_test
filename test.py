==479833== 368 bytes in 1 blocks are definitely lost in loss record 288 of 322                                                                                   
==479833==    at 0x487A410: calloc (vg_replace_malloc.c:1328)                                                                                                    
==479833==    by 0x110E23: CreatePopupWindow (App.c:462)                                                                                                         
==479833==    by 0x114B4B: Create_PopUp_Waiting_for_Connection_Dispaly_QR (ConnectApp.c:259)                                                                     
==479833==    by 0x497EBBF: lv_event_send (in /usr/lib/liblvgl.so.9.1.0)                                                                                         
==479833==    by 0x49130A7: ??? (in /usr/lib/liblvgl.so.9.1.0)                                                                                                   
==479833==    by 0x491317F: lv_obj_send_event (in /usr/lib/liblvgl.so.9.1.0)                                                                                     
==479833==    by 0x11A5DB: progressScreenTransitHandler (Popups.c:616)                                                                                           
==479833==    by 0x4988457: lv_timer_handler (in /usr/lib/liblvgl.so.9.1.0)                                                                                      
==479833==    by 0x10D94B: main (main.c:131)    

	case POP_ID_HOMEPAGE_PREPARING:
				{
					if(mpPopupPage->mPopData.ePopAction==ACTION_PROGRESS)	
					{
						lv_bar_set_value(mpPopupPage->mpProgressBar,mpPopupPage->mPopData.mucBarValue,LV_ANIM_OFF);

						// 상태를 확인하고, 만약 실패 했을 경우 .. 
						AppConnect_Status* status=Get_AppConnect_Status();

						bool is_failed = strcmp((char*)status->Status, APP_CONNECT_STATUS_Error) == 0; 

						if(is_failed){
							UpdateState(POP_ID_HOMEPAGE_PREPARING,POP_ID_HOMEPAGE_FAIL,WINDOW_HOME,SCR_TYPE_POPUP);
							lv_obj_send_event(ui->mpEventStateSwitch,LV_EVENT_CLICKED,NULL);
						}

						if(mpPopupPage->mPopData.mucBarValue>=100)
						{
							progressTransit_data* data = malloc(sizeof(progressTransit_data));
							data->ui = ui;
							data->ePopupId_now = POP_ID_HOMEPAGE_PREPARING;
							data->ePopupId_next = POP_ID_HOMEPAGE_WAITING;
							data->ePopupId_next_next = WINDOW_CONNECT_APP;
							lv_timer_t * timer = lv_timer_create(progressScreenTransitHandler, WAIT_TIME, data);

						}
					}
					else if(mpPopupPage->mPopData.ePopAction==ACTION_CANCEL)
					{
						// disconnect 호출
						pthread_mutex_lock(&serviceHandleMutex);
						callStopAppConnect(serviceHandle);
						pthread_mutex_unlock(&serviceHandleMutex);

						if (ui->mEventTimers.mpTimerConnectAppPreparing != NULL){
							lv_timer_delete(ui->mEventTimers.mpTimerConnectAppPreparing);
							ui->mEventTimers.mpTimerConnectAppPreparing = NULL;
							Get_Progress_Bar_Value()->ulProgressValue = 0;
						}
						UpdateState(POP_ID_HOMEPAGE_PREPARING,WINDOW_HOME,WINDOW_NETWORK_INFO, SCR_TYPE_POPUP);
						lv_obj_send_event(ui->mpEventStateSwitch,LV_EVENT_CLICKED,NULL);
					}
				}
				break;

			case POP_ID_HOMEPAGE_WAITING:
				{
					if(mpPopupPage->mPopData.ePopAction==ACTION_CANCEL)
					{

						// disconnect 호출
						pthread_mutex_lock(&serviceHandleMutex);
						callStopAppConnect(serviceHandle);
						pthread_mutex_unlock(&serviceHandleMutex);

						if (ui->mEventTimers.mpTimerConnectAppWaiting != NULL){
							lv_timer_delete(ui->mEventTimers.mpTimerConnectAppWaiting);
							ui->mEventTimers.mpTimerConnectAppWaiting = NULL;
							Get_Progress_Bar_Value()->ulProgressValue = 0;
						}

						UpdateState(POP_ID_HOMEPAGE_WAITING,WINDOW_HOME,WINDOW_NETWORK_INFO,SCR_TYPE_POPUP);
						lv_obj_send_event(ui->mpEventStateSwitch,LV_EVENT_CLICKED,NULL);

					}
					else if(mpPopupPage->mPopData.ePopAction==ACTION_ERR)
					{
						UpdateState(POP_ID_HOMEPAGE_WAITING,POP_ID_HOMEPAGE_FAIL,WINDOW_HOME,SCR_TYPE_POPUP);
						lv_obj_send_event(ui->mpEventStateSwitch,LV_EVENT_CLICKED,NULL);
					}
					else if(mpPopupPage->mPopData.ePopAction==ACTION_CONNECTED)
					{
						ui->isAppConnected=true;
						ui->mUiState.mucCurrentState=WINDOW_CONNECT_APP;
						UpdateState(POP_ID_HOMEPAGE_WAITING,WINDOW_CONNECT_APP,WINDOW_BACKUP,SCR_TYPE_POPUP);
						lv_obj_send_event(ui->NagivBar.mNavig[ui->mUiState.mucCurrentState],LV_EVENT_CLICKED,NULL);
						lv_obj_send_event(ui->mpEventStateSwitch,LV_EVENT_CLICKED,NULL);

					}

				}
				break; 

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
