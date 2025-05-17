void DestroyPopup(UINT16 ulPopId) {
    INT16 ind = -1;
    lv_ui* ui = Ui_GetInstance();
    
    // 팝업 ID를 찾아 인덱스를 찾음
    for (int i = 0; i < ui->mucPopupCount; i++) {
        if (ui->mpActivePopupIds[i] == ulPopId) {
            ind = i;
            break;
        }
    }
    
    if (ind != -1) {
        // 팝업 페이지의 객체를 삭제
        lv_obj_del(ui->mpPopupPages[ind]->mpPageWindowArea);
        
        // mPopData의 BtnMatrixMap 해제
        if (ui->mpPopupPages[ind]->mPopData.BtnMatrixMap) {
            for (int i = 0; ui->mpPopupPages[ind]->mPopData.BtnMatrixMap[i][0] != '\0'; i++) {
                free(ui->mpPopupPages[ind]->mPopData.BtnMatrixMap[i]);
            }
            free(ui->mpPopupPages[ind]->mPopData.BtnMatrixMap);
        }

        // 팝업 페이지 구조체 메모리 해제
        free(ui->mpPopupPages[ind]);

        // 배열에서 팝업을 제거
        for (int i = ind; i < ui->mucPopupCount - 1; i++) {
            ui->mpPopupPages[i] = ui->mpPopupPages[i + 1];
            ui->mpActivePopupIds[i] = ui->mpActivePopupIds[i + 1];
        }

        // 배열 크기 조정
        ui->mucPopupCount--;
        if (ui->mucPopupCount > 0) {
            ui->mpPopupPages = realloc(ui->mpPopupPages, sizeof(ui_Popup*) * ui->mucPopupCount);
            ui->mpActivePopupIds = realloc(ui->mpActivePopupIds, sizeof(UINT8) * ui->mucPopupCount);
        } else {
            free(ui->mpPopupPages);
            free(ui->mpActivePopupIds);
            ui->mpPopupPages = NULL;
            ui->mpActivePopupIds = NULL;
            ui->mpPopupPage = NULL;
            ui->mScreenType = SCR_TYPE_PAGE;
        }
    }
}



void TimerEventsConnectAppWaiting(lv_timer_t* ptimerData)
{
	printf("TimerEventsConnectAppWaiting\n");
	lv_ui*ui=Ui_GetInstance();

	if (ui->mEventTimers.mpTimerConnectAppWaiting==NULL) return;
	// 현재 앱 연결 상태 
	pthread_mutex_lock(&serviceHandleMutex);
	callStatusAppConnect(serviceHandle);
	pthread_mutex_unlock(&serviceHandleMutex);


	AppConnect_Status* AppStatus=Get_AppConnect_Status();

#if WITHOUT_ENGINE

	if(strcmp("Ready"/*AppStatus.Status*/,APP_CONNECT_STATUS_READY)==0)

#else
		printf("AppStatus->Status: %s\n",AppStatus->Status);
		if(strcmp(AppStatus->Status,APP_CONNECT_STATUS_CONNECTED)==0)
#endif
		{
			ui->isAppConnected=true;
			ui->mpPopupPage->mPopData.ePopAction=ACTION_CONNECTED;
			lv_obj_send_event(ui->mpPopupPage->mpBtnCancel,LV_EVENT_CLICKED,ui->mpPopupPage);
			lv_timer_delete(ui->mEventTimers.mpTimerConnectAppWaiting);
			ui->mEventTimers.mpTimerConnectAppWaiting=NULL;
		}
		else if(strcmp(AppStatus->Status,APP_CONNECT_STATUS_Error)==0)
		{
			ui->isAppConnected=false;
			ui->mpPopupPage->mPopData.ePopAction=ACTION_ERR;
			lv_obj_send_event(ui->mpPopupPage->mpBtnCancel,LV_EVENT_CLICKED,ui->mpPopupPage);
			lv_timer_delete(ui->mEventTimers.mpTimerConnectAppWaiting);
			ui->mEventTimers.mpTimerConnectAppWaiting=NULL;
		}else if(strcmp(AppStatus->Status,APP_CONNECT_STATUS_DISCONNECTED)==0)
		{
			// 현재 블루투스 상태
			pthread_mutex_lock(&serviceHandleMutex);
			callGetBluetoothStatus(serviceHandle);
			pthread_mutex_unlock(&serviceHandleMutex);
		}

}

timer는 이런식으로 삭제해서 괜찮을 것 같고, 내가 1차 적으로 이렇게 DestroyPopup 을 수정해봤는데 이건 어때?
