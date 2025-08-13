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
	lv_log("=============================== Both Keys are Long Pressed =======================\n");
	if(Ui_GetInstance()->LongPressKeytimer)
	{
		while (timer == NULL);

		KeyCode* keyLong=lv_timer_get_user_data(timer);
		printf("KeyAction:%d,  KeyCode:%d, keyLong:%d\n", keyLong->KeyAction, keyLong->KeyCode, keyLong->Type);
		lv_obj_send_event(Ui_GetInstance()->mpEventKeyWidget,LV_EVENT_CLICKED,keyLong);
	
		Ui_GetInstance()->bLongPressKeytimerLeftFlag = false;
		Ui_GetInstance()->bLongPressKeytimerRightFlag = false;

		lv_timer_delete(Ui_GetInstance()->LongPressKeytimer);
		Ui_GetInstance()->LongPressKeytimer = NULL;

		Ui_GetInstance()->mUiKeyLongPress.LeftKeyPress = false;
		Ui_GetInstance()->mUiKeyLongPress.RightKeyPress = false;

		
	}
}


아 확인해보니 이런게 있긴했어
