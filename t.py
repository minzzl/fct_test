
void Create_DataLogging()
{
	lv_ui*ui=Ui_GetInstance();

	ui->mpDataloggingPage=calloc(1, sizeof(ui_DataLogging));
	if(ui->mpDataloggingPage==NULL)
	{
		lv_log("%s\n","Failed to allocate ui->mpConnectAppPage");
	}

	ui->mpDataloggingPage->mpPageWindowArea=CreatePageArea(ui->mpPageWindowArea);

	ui->mpDataloggingPage->mpLayoutTitleText = CreateLayout(ui->mpDataloggingPage->mpPageWindowArea, LV_ALIGN_CENTER, TITLE_X_Y_HEIGHT_WIDTH);
	lv_obj_align_to(ui->mpDataloggingPage->mpLayoutTitleText, ui->mpTopArea, LV_ALIGN_OUT_BOTTOM_MID, 0,0);

	ui->mpDataloggingPage->mpLabelDataLogging = CreateTitle(ui->mpDataloggingPage->mpLayoutTitleText, TR_TITLE_DATA_LOGGING);
	lv_obj_set_style_text_font(ui->mpDataloggingPage->mpLabelDataLogging, &KR_FONT_24B, LV_PART_MAIN | LV_STATE_DEFAULT);

	if (ui->isDataLoggingON)
	{
		// 배경 추가
		ui->mpDataloggingPage->mpLayoutLoadingData = CreateLayout(ui->mpDataloggingPage->mpPageWindowArea, LV_ALIGN_CENTER, 0, 0, 185, 40);
		lv_obj_align_to(ui->mpDataloggingPage->mpLayoutLoadingData, ui->mpDataloggingPage->mpLayoutTitleText, LV_ALIGN_OUT_BOTTOM_MID, 0, 28);

		// 배경 스타일 적용
		lv_obj_set_style_bg_color(ui->mpDataloggingPage->mpLayoutLoadingData, lv_color_make(51, 51, 51), LV_PART_MAIN);
		lv_obj_set_style_radius(ui->mpDataloggingPage->mpLayoutLoadingData, 50, LV_PART_MAIN); // 둥근 모서리
		lv_obj_set_style_bg_opa(ui->mpDataloggingPage->mpLayoutLoadingData, LV_OPA_COVER, LV_PART_MAIN);
		lv_obj_set_style_border_width(ui->mpDataloggingPage->mpLayoutLoadingData, 0, LV_PART_MAIN);

		lv_obj_set_flex_flow(ui->mpDataloggingPage->mpLayoutLoadingData, LV_FLEX_FLOW_ROW);  // 🔥 가로 정렬 (아이콘 왼쪽, 텍스트 오른쪽)
		lv_obj_set_flex_align(ui->mpDataloggingPage->mpLayoutLoadingData, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);

		extern const lv_img_dsc_t ic_status_loading_1;
		extern const lv_img_dsc_t ic_status_loading_2;
		extern const lv_img_dsc_t ic_status_loading_3;
		extern const lv_img_dsc_t ic_status_loading_4;

		 static const lv_img_dsc_t * frames[] = {
			&ic_status_loading_1,
			&ic_status_loading_2,
			&ic_status_loading_3,
			&ic_status_loading_4,
		};		
		
		lv_obj_t *anim = lv_animimg_create(ui->mpDataloggingPage->mpLayoutLoadingData);
		lv_animimg_set_src(anim, (const void **)frames, sizeof(frames)/sizeof(frames[0]));
		lv_animimg_set_duration(anim, 500); // 전체 1회전 500ms (프레임 4개면 프레임당 ~125ms)
		lv_animimg_set_repeat_count(anim, LV_ANIM_REPEAT_INFINITE);
		lv_obj_align(anim, LV_ALIGN_LEFT_MID, 0, 0);
		lv_animimg_start(anim);
		ui->mpDataloggingPage->mpLoaderImage = anim;        // 기존 포인터 재활용(타입은 lv_obj_t*)
		ui->mpDataloggingPage->mpLabelLogging_OR_Stopped =CreateText(ui->mpDataloggingPage->mpLayoutLoadingData, TR_LOGGING_DATA, LV_ALIGN_CENTER, 0, 0);
		lv_obj_align_to(ui->mpDataloggingPage->mpLabelLogging_OR_Stopped, ui->mpDataloggingPage->mpLoaderImage,LV_ALIGN_OUT_RIGHT_MID, 8, 0);
	}
	else
	{
		// 배경 추가
		ui->mpDataloggingPage->mpLayoutLoadingData = CreateLayout(ui->mpDataloggingPage->mpPageWindowArea, LV_ALIGN_CENTER, 0, 0, 130, 40);
		lv_obj_align_to(ui->mpDataloggingPage->mpLayoutLoadingData, ui->mpDataloggingPage->mpLayoutTitleText, LV_ALIGN_OUT_BOTTOM_MID, 0, 28);

		// 배경 스타일 적용
		lv_obj_set_style_bg_color(ui->mpDataloggingPage->mpLayoutLoadingData, lv_color_make(51, 51, 51), LV_PART_MAIN);
		lv_obj_set_style_radius(ui->mpDataloggingPage->mpLayoutLoadingData, 50, LV_PART_MAIN); // 둥근 모서리
		lv_obj_set_style_bg_opa(ui->mpDataloggingPage->mpLayoutLoadingData, LV_OPA_COVER, LV_PART_MAIN);
		lv_obj_set_style_border_width(ui->mpDataloggingPage->mpLayoutLoadingData, 0, LV_PART_MAIN);

		lv_obj_set_flex_flow(ui->mpDataloggingPage->mpLayoutLoadingData, LV_FLEX_FLOW_ROW);  // 🔥 가로 정렬 (아이콘 왼쪽, 텍스트 오른쪽)
		lv_obj_set_flex_align(ui->mpDataloggingPage->mpLayoutLoadingData, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);

		extern const lv_img_dsc_t ic_status_stop;
		ui->mpDataloggingPage->mpLoaderImage = CreateImage(ui->mpDataloggingPage->mpLayoutLoadingData, &ic_status_stop, LV_ALIGN_LEFT_MID, 0, 0);

		ui->mpDataloggingPage->mpLabelLogging_OR_Stopped = CreateText(ui->mpDataloggingPage->mpLayoutLoadingData, TR_STOPPED_LOGGING, LV_ALIGN_CENTER, 0, 0);
		lv_obj_align_to(ui->mpDataloggingPage->mpLabelLogging_OR_Stopped, ui->mpDataloggingPage->mpLoaderImage, LV_ALIGN_OUT_RIGHT_MID, 8, 0);
	}


	ui->mpDataloggingPage->mpLayoutTextBtn =CreateLayout(ui->mpDataloggingPage->mpPageWindowArea, LV_ALIGN_CENTER, 0 ,0 , 258, 83);
	lv_obj_align_to(ui->mpDataloggingPage->mpLayoutTextBtn, ui->mpDataloggingPage->mpLayoutTitleText, LV_ALIGN_OUT_BOTTOM_MID, 0, 84);

	ui->mpDataloggingPage->mpLabelKeyPress = CreateImageText(ui->mpDataloggingPage->mpLayoutTextBtn, (ui->isDataLoggingON ? TR_O_PRESS_STOP_LOGGING : TR_O_PRESS_START_LOGGING), LV_ALIGN_CENTER, 0, 0);


}


근데 칸을 벗어나서 로딩 아이콘이 너무 크게 보이는데 ??? 
