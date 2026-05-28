from hotix.engine.report_templates import get_report_template, normalize_universe_type


def test_normalize_universe_type_keeps_current_index_panel_compatible():
    assert normalize_universe_type("index_panel") == "index"
    assert normalize_universe_type("index") == "index"


def test_report_templates_use_type_specific_language():
    assert get_report_template("index").overview_title == "指数状态概览"
    assert get_report_template("etf").overview_title == "ETF 状态概览"
    assert get_report_template("stock").member_label == "个股"
    assert get_report_template("sector").universe_review_title == "板块轮动分析"
    assert get_report_template("unknown").member_label == "样本"
