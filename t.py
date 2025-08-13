[Error] (2729313.087, +2729313087)       _lv_inv_area: Asserted at expression: !disp->rendering_in_progress (Invalidate area is not allowed during rendering.) lv_refr.c:257
^[[A[Engine queue] : 108 Ready


앱 강제 종료 하려고 하면 이런 오류도 나는데 혹시 내가 고려해야했던게 있나?

static void arc_set_start_exec(void * obj, int32_t v)
{
   // 각도 wrap
   int32_t start = v % 360;
   if(start < 0) start += 360;
   int32_t end = start + 90;
   if(end >= 360) end -= 360;
   lv_arc_set_start_angle((lv_obj_t *)obj, start);
   lv_arc_set_end_angle  ((lv_obj_t *)obj, end);
}

void Create_DataLogging()
{
	lv_ui* ui = Ui_GetInstance();
	ui->mpDataloggingPage = calloc(1, sizeof(ui_DataLogging));
	if (ui->mpDataloggingPage == NULL) {
		lv_log("%s\n","Failed to allocate ui->mpConnectAppPage");
		return;
	}
	ui->mpDataloggingPage->mpPageWindowArea = CreatePageArea(ui->mpPageWindowArea);
	ui->mpDataloggingPage->mpLayoutTitleText = CreateLayout(ui->mpDataloggingPage->mpPageWindowArea, LV_ALIGN_CENTER, TITLE_X_Y_HEIGHT_WIDTH);
	lv_obj_align_to(ui->mpDataloggingPage->mpLayoutTitleText, ui->mpTopArea, LV_ALIGN_OUT_BOTTOM_MID, 0, 0);
	ui->mpDataloggingPage->mpLabelDataLogging = CreateTitle(ui->mpDataloggingPage->mpLayoutTitleText, TR_TITLE_DATA_LOGGING);
	lv_obj_set_style_text_font(ui->mpDataloggingPage->mpLabelDataLogging, &KR_FONT_24B, LV_PART_MAIN | LV_STATE_DEFAULT);
	/* 공통: 배경 레이아웃 */
	const lv_coord_t BOX_W = ui->isDataLoggingON ? 185 : 130;
	ui->mpDataloggingPage->mpLayoutLoadingData = CreateLayout(ui->mpDataloggingPage->mpPageWindowArea, LV_ALIGN_CENTER, 0, 0, BOX_W, 40);
	lv_obj_align_to(ui->mpDataloggingPage->mpLayoutLoadingData, ui->mpDataloggingPage->mpLayoutTitleText, LV_ALIGN_OUT_BOTTOM_MID, 0, 28);
	/* 배경 스타일 */
	lv_obj_set_style_bg_color(ui->mpDataloggingPage->mpLayoutLoadingData, lv_color_make(51, 51, 51), LV_PART_MAIN);
	lv_obj_set_style_radius   (ui->mpDataloggingPage->mpLayoutLoadingData, 50, LV_PART_MAIN);
	lv_obj_set_style_bg_opa   (ui->mpDataloggingPage->mpLayoutLoadingData, LV_OPA_COVER, LV_PART_MAIN);
	lv_obj_set_style_border_width(ui->mpDataloggingPage->mpLayoutLoadingData, 0, LV_PART_MAIN);
	/* 행 레이아웃 + 간격(아이콘-텍스트 사이 8px) */
	lv_obj_set_flex_flow (ui->mpDataloggingPage->mpLayoutLoadingData, LV_FLEX_FLOW_ROW);
	lv_obj_set_flex_align(ui->mpDataloggingPage->mpLayoutLoadingData,
							LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
	lv_obj_set_style_pad_column(ui->mpDataloggingPage->mpLayoutLoadingData, 8, LV_PART_MAIN);
	/* 아이콘 래퍼(고정 크기) */
	const lv_coord_t WRAP = 24;   // 화면에 보여줄 고정 아이콘 크기
	lv_obj_t *icon_wrap = lv_obj_create(ui->mpDataloggingPage->mpLayoutLoadingData);
	lv_obj_remove_style_all(icon_wrap);
	lv_obj_set_size(icon_wrap, WRAP, WRAP);
	lv_obj_set_style_min_width (icon_wrap, WRAP, LV_PART_MAIN);
	lv_obj_set_style_max_width (icon_wrap, WRAP, LV_PART_MAIN);
	lv_obj_set_style_min_height(icon_wrap, WRAP, LV_PART_MAIN);
	lv_obj_set_style_max_height(icon_wrap, WRAP, LV_PART_MAIN);

	if (ui->isDataLoggingON)
	{
		// (생략) mpLayoutLoadingData 스타일/플렉스, pad_column=8, icon_wrap(24x24) 생성은 기존 그대로
		/* 90° 웻지를 그릴 arc (벡터) */
		lv_obj_t *arc = lv_arc_create(icon_wrap);
		lv_obj_remove_style_all(arc);
		const lv_coord_t WRAP = 24;
		lv_obj_set_size(arc, WRAP, WRAP);
		lv_obj_center(arc);
		lv_arc_set_bg_angles(arc, 0, 360);      
		// 배경 트랙(옵션)
		lv_obj_set_style_arc_color(arc, lv_color_make(120,120,120), LV_PART_MAIN | LV_STATE_DEFAULT);
		lv_obj_set_style_arc_opa  (arc, LV_OPA_40,                  LV_PART_MAIN | LV_STATE_DEFAULT);
		lv_obj_set_style_arc_width(arc, 3,                           LV_PART_MAIN | LV_STATE_DEFAULT);
		// 인디케이터(실제로 보이는 90° 웻지)
		lv_obj_set_style_arc_color  (arc, lv_color_white(), LV_PART_INDICATOR | LV_STATE_DEFAULT);
		lv_obj_set_style_arc_opa    (arc, LV_OPA_COVER,     LV_PART_INDICATOR | LV_STATE_DEFAULT);
		lv_obj_set_style_arc_width  (arc, 3,                LV_PART_INDICATOR | LV_STATE_DEFAULT);
		lv_obj_set_style_arc_rounded(arc, true,             LV_PART_INDICATOR | LV_STATE_DEFAULT);
		// 조작 비활성
		lv_arc_set_mode(arc, LV_ARC_MODE_NORMAL);
		lv_obj_clear_flag(arc, LV_OBJ_FLAG_CLICKABLE);
		// 초기 각도: 0~90 (항상 90° 유지)
		lv_arc_set_start_angle(arc, 0);
		lv_arc_set_end_angle  (arc, 90);
		// 애니메이션: 시작각을 0→360으로 부드럽게 회전
		lv_anim_t a;
		lv_anim_init(&a);
		lv_anim_set_var(&a, arc);
		lv_anim_set_exec_cb(&a, arc_set_start_exec);  // ← 전역 콜백 사용
		lv_anim_set_values(&a, 0, 360);
		lv_anim_set_time(&a, 1000);                   // 1회전 1000ms
		lv_anim_set_repeat_count(&a, LV_ANIM_REPEAT_INFINITE);
		lv_anim_set_path_cb(&a, lv_anim_path_linear);
		lv_anim_start(&a);
		ui->mpDataloggingPage->mpLoaderImage = arc;
		// 텍스트 (pad_column으로 간격 유지)
		ui->mpDataloggingPage->mpLabelLogging_OR_Stopped =
			CreateText(ui->mpDataloggingPage->mpLayoutLoadingData, TR_LOGGING_DATA, LV_ALIGN_CENTER, 0, 0);
		}
	else
	{
		/* ───────── 정지 상태: 비트맵 ───────── */
		extern const lv_img_dsc_t ic_status_stop;
		lv_obj_t *stop_img = CreateImage(icon_wrap, &ic_status_stop, LV_ALIGN_CENTER, 0, 0);
		ui->mpDataloggingPage->mpLoaderImage = stop_img;
		ui->mpDataloggingPage->mpLabelLogging_OR_Stopped =
			CreateText(ui->mpDataloggingPage->mpLayoutLoadingData, TR_STOPPED_LOGGING, LV_ALIGN_CENTER, 0, 0);
	}
	/* 하단 안내 텍스트 버튼 영역 */
	ui->mpDataloggingPage->mpLayoutTextBtn =
		CreateLayout(ui->mpDataloggingPage->mpPageWindowArea, LV_ALIGN_CENTER, 0, 0, 258, 83);
	lv_obj_align_to(ui->mpDataloggingPage->mpLayoutTextBtn,
					ui->mpDataloggingPage->mpLayoutTitleText, LV_ALIGN_OUT_BOTTOM_MID, 0, 84);
	ui->mpDataloggingPage->mpLabelKeyPress =
		CreateImageText(ui->mpDataloggingPage->mpLayoutTextBtn,
						(ui->isDataLoggingON ? TR_O_PRESS_STOP_LOGGING : TR_O_PRESS_START_LOGGING),
						LV_ALIGN_CENTER, 0, 0);
}
