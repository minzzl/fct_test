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

void*  key_thread(void *arg)
{
	int ex_value1 = -1, ex_value2 = -1, ex_value3 = -1;

    while (1) {
        int value1 = read_gpio_value(LEFT_PIN);
        int value2 = read_gpio_value(CENTER_PIN);
        int value3 = read_gpio_value(RIGHT_PIN);

        if (value1 == -1 || value2 == -1 || value3 == -1)
            continue;


		 // 값 반전
        value1 = (value1 == 0) ? 1 : 0;
        value2 = (value2 == 0) ? 1 : 0;
        value3 = (value3 == 0) ? 1 : 0;

		//printf("%d %d %d\n",value1,value2,value3);
        if (value1 != ex_value1 || value2 != ex_value2 || value3 != ex_value3) {

			// if (value1 != ex_value1 & value3 != ex_value3){
			// 	printf("longkey\n");

			// 	key.KeyCode = 3;
			// 	key.KeyAction = 0;
			// }
            if (value1 != ex_value1) {
				printf("left %d\n",value1);
                key.KeyCode = 0; // Left key
                key.KeyAction = value1;
            } else if (value2 != ex_value2) {
				printf("ok %d\n",value2);
                key.KeyCode = 1; // OK key
                key.KeyAction = value2;
            } else if (value3 != ex_value3) {
				printf("right %d\n",value3);
                key.KeyCode = 2; // Right key
                key.KeyAction = value3;
            } 
            printf("Setting to key value\n");
            ex_value1 = value1;
            ex_value2 = value2;
            ex_value3 = value3;
            
            while (Ui_GetInstance()->EventTimer) {
                usleep(1);
            };
            printf("Go to KeyEventTimer\n");
			Ui_GetInstance()->EventTimer=lv_timer_create(KeyEventTimer,10,&key);
        }

    // Add a sleep to reduce CPU usage
        usleep(10000); // 10ms
    }



}
