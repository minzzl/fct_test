 static bool popup_exists(POPUP_ID id){
    lv_ui *ui = Ui_GetInstance();
    for(int i=0;i<ui->mucPopupCount;i++)
        if(ui->mpActivePopupIds[i]==id) return true;
    return false;
}

void Create_PopUp_Waiting_for_Connection_Dispaly_QR(POPUP_ID id){
    if(popup_exists(id)) return;          // ← 중복 방지
    CreatePopupWindow(id);
    ...
}
