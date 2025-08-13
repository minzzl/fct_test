
void init_gpio_pins(void) {
    unexport_gpio(LEFT_PIN);
    unexport_gpio(RIGHT_PIN);
    unexport_gpio(CENTER_PIN);

    export_gpio(LEFT_PIN);
    export_gpio(RIGHT_PIN);
    export_gpio(CENTER_PIN);

    set_gpio_direction(LEFT_PIN, "in");
    set_gpio_direction(RIGHT_PIN, "in");
    set_gpio_direction(CENTER_PIN, "in");
}

int read_gpio_value(const char *pin) {
    char path[256];
    snprintf(path, sizeof(path), "/sys/devices/platform/amba/fd500000.gpio/gpiochip16/gpio/gpio%s/value", pin);
    int fd = open(path, O_RDONLY);
    if (fd == -1) {
        perror("Failed to open gpio value for reading");
        return -1; // 오류 발생 시 -1 반환
    }
    
    char value_str[3];
    if (read(fd, value_str, sizeof(value_str) - 1) == -1) {
        perror("Failed to read value");
        close(fd);
        return -1; // 오류 발생 시 -1 반환
    }
    
    value_str[2] = '\0'; // 문자열 종료
    close(fd);
    return atoi(value_str);
}

void unexport_gpio(const char *pin) {
    int fd = open("/sys/class/gpio/unexport", O_WRONLY);
    if (fd == -1) {
        perror("Failed to open unexport for writing");
    }
    if (write(fd, pin, strlen(pin)) == -1) {
        perror("Failed to unexport pin");
        close(fd);
    }
    close(fd);
}

void export_gpio(const char *pin) {
    int fd = open("/sys/class/gpio/export", O_WRONLY);
    if (fd == -1) {
        perror("Failed to open export for writing");
        exit(1);
    }
    if (write(fd, pin, strlen(pin)) == -1) {
        perror("Failed to export pin");
        close(fd);
        exit(1);
    }
    close(fd);
}

void set_gpio_direction(const char *pin, const char *direction) {
    char path[35];
    snprintf(path, sizeof(path), "/sys/class/gpio/gpio%s/direction", pin);
    int fd = open(path, O_WRONLY);
    if (fd == -1) {
        perror("Failed to open gpio direction for writing");
        exit(1);
    }
    if (write(fd, direction, strlen(direction)) == -1) {
        perror("Failed to set direction");
        close(fd);
        exit(1);
    }
    close(fd);
}


void* key_thread(void *arg)
{
    bool first_pass = true;
    static int ex1 = -1, ex2 = -1, ex3 = -1;

    while (1) {
        int v1 = read_gpio_value(LEFT_PIN);
        int v2 = read_gpio_value(CENTER_PIN);
        int v3 = read_gpio_value(RIGHT_PIN);
        if (v1 == -1 || v2 == -1 || v3 == -1) continue;

        /* active-low → active-high 변환 */
        v1 = !v1;  v2 = !v2;  v3 = !v3;

        if(first_pass){
            first_pass = false;
            ex1 = v1;  ex2 = v2;  ex3 = v3;
            first_pass = false;
            usleep(10000); // 첫 번째 폴링 후 10ms 대기
            continue;
        }

        /* ------------- Left ------------- */
        if (v1 != ex1) {
            while (Ui_GetInstance()->EventTimer) usleep(1);
            key.KeyCode   = 0;
            key.KeyAction = v1;
            Ui_GetInstance()->EventTimer =
                lv_timer_create(KeyEventTimer, 10, &key);
        }

        /* ------------- OK --------------- */
        if (v2 != ex2) {
            while (Ui_GetInstance()->EventTimer) usleep(1);
            key.KeyCode   = 1;
            key.KeyAction = v2;
            Ui_GetInstance()->EventTimer =
                lv_timer_create(KeyEventTimer, 10, &key);
        }

        /* ------------- Right ------------ */
        if (v3 != ex3) {
            while (Ui_GetInstance()->EventTimer) usleep(1);
            key.KeyCode   = 2;
            key.KeyAction = v3;
            Ui_GetInstance()->EventTimer =
                lv_timer_create(KeyEventTimer, 10, &key);
        }

        /* 모든 이벤트를 보낸 뒤에야 이전 값 업데이트 */
        ex1 = v1;  ex2 = v2;  ex3 = v3;

        /* 폴링 주기 10 ms */
        usleep(10000);
    }
}


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

좌우키가 동시에 눌러졌을때 3초 동안은 눌러져야 좌우키가 동시에 눌러졌다고 판단하게끔하려면 어떻게 수정해야할까
