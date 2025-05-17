아직 빠져 있는 핵심만 콕콕 집어서 정리해볼게요.
(바로 고칠 수 있도록 문제 → 이유 → 패치 코드 순서)

⸻

1. ui_Popup 구조체 자체를 안 free 함

문제	왜 문제?	패치
lv_obj_del()은 LVGL 객체만 지우고, calloc()으로 만든 ui_Popup은 남아 있음	팝업 하나 뜰 때마다 누수	c\nfree(ui->mpPopupPages[ind]);\n


⸻

2. 버튼 매트릭스 해제 루프 버그

for(i; ui->mpPopupPages[ind]->mPopData.BtnMatrixMap[i][0] != '\0'; i++)
    free(ui->mpPopupPages[ind]->mPopData.BtnMatrixMap[i]);
free(ui->mpPopupPages[ind]->mPopData.BtnMatrixMap[i]);   // ← 여기가 잘못

	•	마지막 i는 NULL 터미네이터 행을 가리킴 → 미해제
	•	배열(이중포인터) 자체도 안 free

깔끔한 버전

char **map = p->mPopData.BtnMatrixMap;
if (map) {
    for (int r = 0; map[r]; ++r) free(map[r]);
    free(map);          // 배열 자체
}


⸻

3. 타이머를 안 지우면 콜백에서 크래시

if (ui->mEventTimers.mpTimerConnectAppWaiting)
    lv_timer_del(ui->mEventTimers.mpTimerConnectAppWaiting);

팝업이 사라졌는데 타이머가 남아 있으면
콜백이 이미 지워진 객체를 만져서 HardFault!

⸻

4. 배열 시프팅 오프바이원

for (int i = ind; i < ui->mucPopupCount - 1; ++i) {
    ui->mpPopupPages[i]   = ui->mpPopupPages[i+1];
    ui->mpActivePopupIds[i] = ui->mpActivePopupIds[i+1];
}

	•	i < cnt-1까지만 이동해야 마지막 인덱스 초과 접근을 피합니다.

⸻

5. realloc 전에 카운트 먼저 줄이기

realloc(ptr, 0) 은 구현마다 다르기도 하고,
지금 로직처럼 줄이기 전에 cnt-1을 넘기면 size=0까지 내려갑니다.

--ui->mucPopupCount;
ui->mpPopupPages = realloc(ui->mpPopupPages,
        sizeof(ui_Popup*) * ui->mucPopupCount);
ui->mpActivePopupIds = realloc(ui->mpActivePopupIds,
        sizeof(uint8_t)   * ui->mucPopupCount);


⸻

6. 실패-안전성: realloc 리턴 체크

void *tmp = realloc(ui->mpPopupPages, newSize);
if (!tmp) { /* out-of-mem ⇒ 기존 포인터는 여전히 유효 */ }
ui->mpPopupPages = tmp;


⸻

7. 새로 고친 DestroyPopup() (핵심만)

void DestroyPopup(uint16_t popId)
{
    lv_ui *ui = Ui_GetInstance();
    int idx = -1;
    for (int i = 0; i < ui->mucPopupCount; ++i)
        if (ui->mpActivePopupIds[i] == popId) { idx = i; break; }
    if (idx == -1) return;

    ui_Popup *p = ui->mpPopupPages[idx];

    /* 1. LVGL 객체 삭제 */
    if (p->mpPageWindowArea) lv_obj_del(p->mpPageWindowArea);

    /* 2. 타이머 정리 */
    if (ui->mEventTimers.mpTimerConnectAppWaiting)
        lv_timer_del(ui->mEventTimers.mpTimerConnectAppWaiting);

    /* 3. 가변 버퍼 해제 */
    if (p->mPopData.BtnMatrixMap) {
        char **map = p->mPopData.BtnMatrixMap;
        for (int r = 0; map[r]; ++r) free(map[r]);
        free(map);
    }

    /* 4. 구조체 free */
    free(p);

    /* 5. 배열에서 팝업 제거 */
    for (int i = idx; i < ui->mucPopupCount - 1; ++i) {
        ui->mpPopupPages[i]   = ui->mpPopupPages[i+1];
        ui->mpActivePopupIds[i] = ui->mpActivePopupIds[i+1];
    }
    --ui->mucPopupCount;

    ui->mpPopupPages = realloc(ui->mpPopupPages,
        sizeof(ui_Popup*) * ui->mucPopupCount);
    ui->mpActivePopupIds = realloc(ui->mpActivePopupIds,
        sizeof(uint8_t)   * ui->mucPopupCount);

    /* 6. 현재 팝업 포인터 보정 */
    ui->mpPopupPage = (ui->mucPopupCount) ?
        ui->mpPopupPages[ui->mucPopupCount-1] : NULL;

    if (ui->mucPopupCount == 0) ui->mScreenType = SCR_TYPE_PAGE;
}


⸻

8. 장기적으로 더 편하게 만드는 방법

방법	요점
링크드 리스트로 팝업 관리	중간 삭제 O(1), 시프팅/재할당 불필요
메모리 풀 (ui_Popup pool[MAX])	calloc/free 반복 → 파편화 방지
lv_obj_del_async() 사용	콜백 안에서 바로 지워도 안전
팝업 전용 Popup_Init / Popup_Deinit	생성-소멸 책임 한 곳에 모아 실수 감소


⸻

한 줄 정리
	•	누수 → ui_Popup free
	•	크래시 → 타이머·오프바이원·NULL 체크
	•	깔끔 → 시프팅·realloc 순서 / 실패-안전성

이렇게만 손보면 팝업 열고 닫을 때 생기던 메모리와 타이머 문제는 말끔히 사라질 거예요.
바로 적용해보고, 이상 있으면 또 알려줘요!

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
