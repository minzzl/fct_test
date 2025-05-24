void* key_thread(void *arg)
{
    static int ex1 = -1, ex2 = -1, ex3 = -1;

    while (1) {
        int v1 = read_gpio_value(LEFT_PIN);
        int v2 = read_gpio_value(CENTER_PIN);
        int v3 = read_gpio_value(RIGHT_PIN);
        if (v1 == -1 || v2 == -1 || v3 == -1) continue;

        /* active-low → active-high 변환 */
        v1 = !v1;  v2 = !v2;  v3 = !v3;

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
