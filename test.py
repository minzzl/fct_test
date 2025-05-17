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
