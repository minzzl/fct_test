void KeyEventTimer(lv_timer_t * timer)
{
	KeyCode* key1=lv_timer_get_user_data(timer);

	if(key1->KeyCode == 0 && key1->KeyAction ==0)
	{
		lv_log("===============Left Key Relesed========================\n");

		if(Ui_GetInstance()->mUiKeyLongPress.LeftKeyPress == true && Ui_GetInstance()->mUiKeyLongPress.RightKeyPress == true)
		{
			if (Ui_GetInstance()->LongPressKeytimer != NULL){
				lv_timer_delete(Ui_GetInstance()->LongPressKeytimer);
				Ui_GetInstance()->LongPressKeytimer = NULL;
				Ui_GetInstance()->mUiKeyLongPress.LeftKeyPress = false;
			}
		}


		if(Ui_GetInstance()->mUiKeyLongPress.LeftKeyPress)
		{
			lv_obj_send_event(Ui_GetInstance()->mpEventKeyWidget,LV_EVENT_CLICKED,key1);
		}
		Ui_GetInstance()->mUiKeyLongPress.LeftKeyPress = false;
	}
	else if(key1->KeyCode == 0 && key1->KeyAction ==1)
	{
		lv_log("===============Left Key Pressed========================\n");

		pthread_mutex_lock(&serviceHandleMutex);
		callPWM(serviceHandle);
		pthread_mutex_unlock(&serviceHandleMutex);

		Ui_GetInstance()->mUiKeyLongPress.LeftKeyPress = true;

		if(Ui_GetInstance()->mUiKeyLongPress.LeftKeyPress == true && Ui_GetInstance()->mUiKeyLongPress.RightKeyPress == true)
		{
			static KeyCode keyLong={1,KEY_LR_LONG,KEY_PRESSED};
			if (Ui_GetInstance()->LongPressKeytimer == NULL){
				Ui_GetInstance()->LongPressKeytimer = lv_timer_create(LongPressKeyTimer, 10,&keyLong);
				}
		}
	}
	else if(key1->KeyCode == 2 && key1->KeyAction ==0)
	{
		lv_log("===============Right Key Relesed========================\n");

		if(Ui_GetInstance()->mUiKeyLongPress.LeftKeyPress == true && Ui_GetInstance()->mUiKeyLongPress.RightKeyPress == true)
		{
			if (Ui_GetInstance()->LongPressKeytimer != NULL){
				lv_timer_delete(Ui_GetInstance()->LongPressKeytimer);
				Ui_GetInstance()->LongPressKeytimer = NULL;
				Ui_GetInstance()->mUiKeyLongPress.RightKeyPress = false;
			}
		}


		if(Ui_GetInstance()->mUiKeyLongPress.RightKeyPress)
		{
			lv_obj_send_event(Ui_GetInstance()->mpEventKeyWidget,LV_EVENT_CLICKED,key1);
		}
		Ui_GetInstance()->mUiKeyLongPress.RightKeyPress = false;
	}
	else if(key1->KeyCode == 2 && key1->KeyAction ==1)
	{
		lv_log("===============Right Key Pressed========================\n");

		pthread_mutex_lock(&serviceHandleMutex);
		callPWM(serviceHandle);
		pthread_mutex_unlock(&serviceHandleMutex);

		Ui_GetInstance()->mUiKeyLongPress.RightKeyPress = true;

		if(Ui_GetInstance()->mUiKeyLongPress.LeftKeyPress == true && Ui_GetInstance()->mUiKeyLongPress.RightKeyPress == true){
			
			static KeyCode keyLong={1,KEY_LR_LONG,KEY_PRESSED};
			if (Ui_GetInstance()->LongPressKeytimer == NULL){
				Ui_GetInstance()->LongPressKeytimer = lv_timer_create(LongPressKeyTimer, 10,&keyLong);

			}
		}
	}
	else if(key1->KeyCode == 1 && key1->KeyAction ==0)
	{
		lv_log("===============OK Key Pressed========================\n");
		pthread_mutex_lock(&serviceHandleMutex);
		callPWM(serviceHandle);
		pthread_mutex_unlock(&serviceHandleMutex);

		lv_obj_send_event(Ui_GetInstance()->mpEventKeyWidget,LV_EVENT_CLICKED,key1);
	}
	if (Ui_GetInstance()->EventTimer != NULL){
		lv_timer_delete(Ui_GetInstance()->EventTimer);
		Ui_GetInstance()->EventTimer = NULL;
	}

}



void LongPressKeyTimer(lv_timer_t * timer)
{
   // ★추가: 3초 경과 측정을 위한 정적 시작 시간
   static uint32_t s_lr_start_ms = 0;
   // 둘 다 계속 눌려있는지 확인 (연속 유지 조건)
   if (!(Ui_GetInstance()->mUiKeyLongPress.LeftKeyPress &&
         Ui_GetInstance()->mUiKeyLongPress.RightKeyPress)) {
       // 하나라도 떼졌으면 타이머 종료 및 초기화 (이벤트 미발생)
       if (Ui_GetInstance()->LongPressKeytimer){
           lv_timer_delete(Ui_GetInstance()->LongPressKeytimer);
           Ui_GetInstance()->LongPressKeytimer = NULL;
       }
       s_lr_start_ms = 0;
       return;
   }
   // 첫 진입(타이머가 처음 돌기 시작) 시각 기록
   if (s_lr_start_ms == 0) {
       s_lr_start_ms = lv_tick_get();
       return; // 다음 틱부터 경과 검사
   }
   // 3초(3000ms) 이상 연속 유지되었는지 검사
   if (lv_tick_elaps(s_lr_start_ms) >= 3000) {
       lv_log("=============================== Both Keys are Long Pressed (>=3s) =======================\n");
       KeyCode* keyLong = lv_timer_get_user_data(timer);
       printf("KeyAction:%d,  KeyCode:%d, keyLong:%d\n",
              keyLong->KeyAction, keyLong->KeyCode, keyLong->Type);
       // 동시-롱 이벤트 전송
       lv_obj_send_event(Ui_GetInstance()->mpEventKeyWidget, LV_EVENT_CLICKED, keyLong);
       // 기존 플래그/타이머 정리 (개별 클릭 억제 효과 유지)
       Ui_GetInstance()->bLongPressKeytimerLeftFlag  = false;
       Ui_GetInstance()->bLongPressKeytimerRightFlag = false;
       if (Ui_GetInstance()->LongPressKeytimer){
           lv_timer_delete(Ui_GetInstance()->LongPressKeytimer);
           Ui_GetInstance()->LongPressKeytimer = NULL;
       }
       // 개별 Release 시 클릭 안 나가도록 올-프레스 플래그도 원래대로 내림(기존 코드 유지)
       Ui_GetInstance()->mUiKeyLongPress.LeftKeyPress  = false;
       Ui_GetInstance()->mUiKeyLongPress.RightKeyPress = false;
       s_lr_start_ms = 0; // 다음 사이클 대비 초기화
   }
}


근데 좌우키가 눌러졌다는거는 static KeyCode keyLong={1,KEY_LR_LONG,KEY_PRESSED}; 로 판단을 하고 있어서 3초 검사가 의미 없는 것 같기도해 . 
	else if(pKeyCode->KeyAction==KEY_PRESSED && pKeyCode->KeyCode==KEY_LR_LONG && ui->mUiState.mucCurrentState==WINDOW_OPENSOURCE)
			{
				ui->mUiState.mucCurrentState=POP_ID_RESET_PASSWORD;
				lv_obj_send_event(ui->mpEventStateSwitch,LV_EVENT_CLICKED,NULL);
			}
		}

이런식으로 하고 있었거든

3초 검사를 완료하고 static KeyCode keyLong={1,KEY_LR_LONG,KEY_PRESSED}; 로 설정을 해주던가 해야할 것 같아
