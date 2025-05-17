void DestroyPopup(uint16_t popId)
{
    lv_ui *ui = Ui_GetInstance();
    int idx = -1;
    for (int i = 0; i < ui->mucPopupCount; ++i)
        if (ui->mpActivePopupIds[i] == popId) { idx = i; break; }
    if (idx == -1) return;

    ui_Popup *p = ui->mpPopupPages[idx];

    /* 1. LVGL 객체 제거 */
    if (p->mpPageWindowArea) lv_obj_del(p->mpPageWindowArea);

    /* 2. 타이머 제거 (있다면) */
    if (ui->mEventTimers.mpTimerConnectAppWaiting) {
        lv_timer_del(ui->mEventTimers.mpTimerConnectAppWaiting);
        ui->mEventTimers.mpTimerConnectAppWaiting = NULL;
    }

    /* 3. 가변 버퍼 해제 */
    if (p->mPopData.BtnMatrixMap) {
        char **map = p->mPopData.BtnMatrixMap;
        for (int r = 0; map[r]; ++r) free(map[r]);
        free(map);
    }

    /* 4. ui_Popup 구조체 free (누수 해결!) */
    free(p);

    /* 5. 배열 시프팅 */
    for (int i = idx; i < ui->mucPopupCount - 1; ++i) {
        ui->mpPopupPages[i]   = ui->mpPopupPages[i+1];
        ui->mpActivePopupIds[i] = ui->mpActivePopupIds[i+1];
    }

    /* 6. 카운트 감소 후 realloc */
    --ui->mucPopupCount;
    ui->mpPopupPages = realloc(ui->mpPopupPages,
        ui->mucPopupCount * sizeof(ui_Popup*));
    ui->mpActivePopupIds = realloc(ui->mpActivePopupIds,
        ui->mucPopupCount * sizeof(uint8_t));

    /* 7. 현재 팝업 포인터 보정 */
    ui->mpPopupPage = (ui->mucPopupCount) ?
                      ui->mpPopupPages[ui->mucPopupCount-1] : NULL;
    if (ui->mucPopupCount == 0) ui->mScreenType = SCR_TYPE_PAGE;
}
