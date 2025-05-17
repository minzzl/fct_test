==474079== 124 bytes in 1 blocks are definitely lost in loss record 281 of 350                                                                                   
==474079==    at 0x487519C: malloc (vg_replace_malloc.c:381)                                                                                                     
==474079==    by 0x4E94AD3: strdup (strdup.c:42)                                                                                                                 
==474079==    by 0x11A36B: Create_PopUp_Open_Source_License (OpenSource.c:98)                                                                                    
==474079==    by 0x497EBBF: lv_event_send (in /usr/lib/liblvgl.so.9.1.0)                                                                                         
==474079==    by 0x49130A7: ??? (in /usr/lib/liblvgl.so.9.1.0)                                                                                                   
==474079==    by 0x491317F: lv_obj_send_event (in /usr/lib/liblvgl.so.9.1.0)                                                                                     
==474079==    by 0x11316F: EventStateMachineProc (App.c:1271)                                                                                                    
==474079==    by 0x11316F: EventStateMachineProc (App.c:1188)                                                                                                    
==474079==    by 0x497EBBF: lv_event_send (in /usr/lib/liblvgl.so.9.1.0)                                                                                         
==474079==    by 0x49130A7: ??? (in /usr/lib/liblvgl.so.9.1.0)                                                                                                   
==474079==    by 0x491317F: lv_obj_send_event (in /usr/lib/liblvgl.so.9.1.0)                                                                                     
==474079==    by 0x497EBBF: lv_event_send (in /usr/lib/liblvgl.so.9.1.0)                                                                                         
==474079==    by 0x49130A7: ??? (in /usr/lib/liblvgl.so.9.1.0)    

void Create_PopUp_Open_Source_License() {
    printf("Create_PopUp_Open_Source_License\n");
    lv_ui* ui = Ui_GetInstance();

    CreatePopupWindow(POP_ID_OPEN_SOURCE_LICENSE);

    // 파일 열기
    FILE* file = fopen("openSource.txt", "r");
    if (!file) {
        printf("Failed to open openSource.txt\n");
        return; // 파일 열기 실패 시 함수 종료
    } else {
        printf("openSource.txt opened\n");
    }

    // 파일 크기 계산
    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    fseek(file, 0, SEEK_SET); // 파일 포인터를 처음으로 되돌림
    printf("File size: %ld bytes\n", file_size);

    // 한 페이지에 표시할 최대 줄 수 계산
    int max_lines_per_page = MAX_LINES_PER_PAGE;
    printf("Max lines per page: %d\n", max_lines_per_page);

    // 텍스트를 읽어올 버퍼
    char buffer[MAX_LINES_PER_PAGE * (MAX_CHARS_PER_LINE + 1)] = {0}; // 한 페이지에 표시할 최대 텍스트 크기
    char line[MAX_CHARS_PER_LINE + 1] = {0}; // 한 줄을 읽어올 버퍼
    int line_count = 0;

    // 파일에서 한 줄씩 읽기
    while (fgets(line, sizeof(line), file)) {
        // 줄바꿈 문자 제거
        line[strcspn(line, "\n")] = '\0';

        // 버퍼에 줄 추가
        strncat(buffer, line, sizeof(buffer) - strlen(buffer) - 1);
        strncat(buffer, "\n", sizeof(buffer) - strlen(buffer) - 1);

        line_count++;
        if (line_count >= max_lines_per_page) {
            break; // 한 화면에 표시할 줄 수를 초과하면 중단
        }
    }

    fclose(file);

    printf("Buffer content:\n%s\n", buffer);

    // OpenSource에 buffer 내용을 복사
    ui->mpPopupPage->mPopData.OpenSource = strdup(buffer);

    printf("ui->mpPopupPage->mPopData.OpenSource:\n%s\n", ui->mpPopupPage->mPopData.OpenSource);

    // 총 페이지 수 계산
    ui->mpPopupPage->mPopData.mucPageTotalCount = (file_size / (MAX_LINES_PER_PAGE * MAX_CHARS_PER_LINE)) + 
                                                  ((file_size % (MAX_LINES_PER_PAGE * MAX_CHARS_PER_LINE)) > 0 ? 1 : 0);
    printf("Total pages: %d\n", ui->mpPopupPage->mPopData.mucPageTotalCount);

    ui->mpPopupPage->mPopData.BtnMatrixMap=calloc(4,sizeof(char*));
	ui->mpPopupPage->mPopData.BtnMatrixMap[0]=calloc(strlen(textData[TR_PREV])+1,sizeof(char));
	ui->mpPopupPage->mPopData.BtnMatrixMap[1]=calloc(strlen(textData[TR_CLOSE])+1,sizeof(char));
    ui->mpPopupPage->mPopData.BtnMatrixMap[2]=calloc(strlen(textData[TR_NEXT_BUTTON])+1,sizeof(char));
	ui->mpPopupPage->mPopData.BtnMatrixMap[3]=calloc(1,sizeof(char));

	strcpy(ui->mpPopupPage->mPopData.BtnMatrixMap[0],textData[TR_PREV]);
	strcpy(ui->mpPopupPage->mPopData.BtnMatrixMap[1],textData[TR_CLOSE]);
    strcpy(ui->mpPopupPage->mPopData.BtnMatrixMap[2],textData[TR_NEXT_BUTTON]);
	strcpy(ui->mpPopupPage->mPopData.BtnMatrixMap[3],"");

    // 팝업 표시
    PopOpensource(&ui->mpPopupPage->mPopData);
    printf("PopOpensource OK\n");

    lv_obj_add_event_cb(ui->mpPopupPage->mpBtnMatrix, EventPopUpProc, LV_EVENT_CLICKED, NULL);
}
