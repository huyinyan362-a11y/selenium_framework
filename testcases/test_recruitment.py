import allure
import pytest

from common.case_util import params
from common.data_factory import new_candidate, unique_suffix
from common.yaml_util import load_yaml
from pages.recruitment_page import RecruitmentPage

INVALID_EMAILS = load_yaml("data/recruitment.yaml")["invalid_email_cases"]
EMAIL_ERROR = "Expected format: admin@example.com"
PHONE_ERROR = "Allows numbers and only + - / ( )"


@pytest.fixture
def recruitment(login):
    """公共演示站上有人会关掉Recruitment模块（页面显示403 Module Forbidden）
    这是环境问题不是功能bug：标记为skip并写明原因，而不是报失败，避免假失败干扰判断"""
    page = RecruitmentPage(login)
    page.open_list()
    if page.is_forbidden():
        pytest.skip("环境问题：演示站Recruitment模块被关闭（403 Module Forbidden）")
    return page


@pytest.fixture
def temp_candidate(recruitment):
    """前置：新建一个关联了职位空缺的候选人（有空缺才有状态流转按钮）；后置：删掉"""
    cand = new_candidate()
    recruitment.add_candidate(cand["first"], cand["last"], cand["email"], with_vacancy=True)
    yield cand
    recruitment.delete_candidate_if_exists(cand["last"])


@allure.feature("Recruitment招聘")
class TestRecruitment:

    # ==================== P0 ====================
    @pytest.mark.p0
    @allure.title("TC_REC_001 新增候选人后列表能搜到")
    def test_add_candidate(self, recruitment):
        cand = new_candidate()
        try:
            with allure.step("填写姓名、邮箱并保存"):
                recruitment.add_candidate(cand["first"], cand["last"], cand["email"])
            with allure.step("回列表按姓名搜索"):
                recruitment.open_list()
                recruitment.search_by_name(cand["last"])
                names = [r[RecruitmentPage.COL_CANDIDATE] for r in recruitment.get_rows()]
                assert len(names) == 1, f"应搜到1条，实际 {names}"
                assert cand["last"] in names[0]
        finally:
            recruitment.delete_candidate_if_exists(cand["last"])

    @pytest.mark.p0
    @allure.title("TC_REC_002 候选人状态流转：Shortlist")
    def test_shortlist(self, temp_candidate, recruitment):
        error = recruitment.change_status("Shortlist")
        assert error is None, f"保存状态时服务端报错：{error}"
        assert "Shortlisted" in recruitment.get_status()

    # ==================== P1 ====================
    @pytest.mark.p1
    @allure.title("TC_REC_003 删除候选人")
    def test_delete_candidate(self, temp_candidate, recruitment):
        recruitment.open_list()
        recruitment.search_by_name(temp_candidate["last"])
        recruitment.delete_row_containing(temp_candidate["last"], exact=False)
        # 删除后不能再"输入并选中提示"——下拉里已经没有这个人了，只会显示No Records Found
        recruitment.open_list()
        hints = recruitment.get_autocomplete_hints(RecruitmentPage.CANDIDATE_NAME, temp_candidate["last"])
        assert hints == ["No Records Found"], f"删除后仍能搜到该候选人：{hints}"

    @pytest.mark.p1
    @allure.title("TC_REC_004 候选人状态流转：Reject")
    def test_reject(self, temp_candidate, recruitment):
        error = recruitment.change_status("Reject")
        assert error is None, f"保存状态时服务端报错：{error}"
        assert "Rejected" in recruitment.get_status()

    @pytest.mark.p1
    @allure.title("TC_REC_005 新增职位空缺")
    def test_add_vacancy(self, recruitment):
        name = f"AutoVac{unique_suffix()}"
        try:
            recruitment.add_vacancy(name)
            assert recruitment.vacancy_exists(name), f"职位空缺列表里没有 {name}"
        finally:
            recruitment.delete_vacancy_if_exists(name)

    @pytest.mark.p1
    @allure.title("TC_REC_006 Reset清空搜索条件")
    def test_reset(self, recruitment):
        # 用Keywords框：不依赖列表里一定有候选人（公共环境数据会变）
        recruitment.input_text(RecruitmentPage.KEYWORDS, "python")
        recruitment.click_reset()
        assert recruitment.get_value(RecruitmentPage.KEYWORDS) == ""

    # ==================== P2 ====================
    @pytest.mark.p2
    @allure.title("TC_REC_007 新增候选人什么都不填")
    def test_add_candidate_required(self, recruitment):
        recruitment.open_add_form()
        recruitment.click_save()
        assert recruitment.get_field_errors().count("Required") == 3

    @allure.title("{case[tc]} 邮箱格式非法：{case[case_name]}")
    @pytest.mark.parametrize("case", params(INVALID_EMAILS))
    def test_invalid_email(self, recruitment, case):
        recruitment.open_add_form()
        recruitment.fill_candidate(email=case["email"])
        recruitment.click_save()
        errors = recruitment.get_field_errors()
        assert EMAIL_ERROR in errors, f"[{case['case_name']}] 邮箱 {case['email']} 应提示格式错误，实际 {errors}"

    @pytest.mark.p2
    @allure.title("TC_REC_013 邮箱格式合法（有效等价类）")
    def test_valid_email(self, recruitment):
        recruitment.open_add_form()
        recruitment.fill_candidate(email="valid.user@test.com")
        recruitment.click_save()
        assert EMAIL_ERROR not in recruitment.get_field_errors()

    @pytest.mark.p2
    @allure.title("TC_REC_014 联系电话含字母")
    def test_phone_with_letters(self, recruitment):
        recruitment.open_add_form()
        recruitment.fill_candidate(contact="abc123")
        assert PHONE_ERROR in recruitment.get_field_errors()

    @pytest.mark.p2
    @allure.title("TC_REC_015 联系电话含允许的符号")
    def test_phone_with_allowed_symbols(self, recruitment):
        # 有效等价类：和上一条成对
        recruitment.open_add_form()
        recruitment.fill_candidate(contact="+86 (010) 123-456")
        assert PHONE_ERROR not in recruitment.get_field_errors(timeout=2)

    @pytest.mark.p2
    @allure.title("TC_REC_016 候选人名字超过30个字符")
    def test_first_name_too_long(self, recruitment):
        recruitment.open_add_form()
        recruitment.fill_candidate(first="a" * 31)
        assert "Should not exceed 30 characters" in recruitment.get_field_errors()
