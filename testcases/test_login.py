import allure
import pytest

from common.case_util import params
from common.yaml_util import CONFIG, load_yaml
from pages.login_page import LoginPage

DATA = load_yaml("data/login.yaml")
ERROR_CASES = DATA["login_error_cases"]
REQUIRED_CASES = DATA["login_required_cases"]


@pytest.fixture
def login_page(driver):
    """未登录状态的登录页"""
    page = LoginPage(driver)
    page.open()
    return page


@allure.feature("登录")
class TestLogin:

    @pytest.mark.p0
    @allure.title("TC_LOGIN_001 正确账号密码登录成功")
    def test_login_success(self, login_page):
        login_page.login(CONFIG["username"], CONFIG["password"])
        assert "dashboard" in login_page.driver.current_url, "登录后未跳转到dashboard"

    # 优先级打在每条数据上（params），不打在方法上：同一个方法里"密码错误"是P0，其他是P1/P2
    @allure.title("{case[tc]} 登录失败：{case[case_name]}")
    @pytest.mark.parametrize("case", params(ERROR_CASES))
    def test_login_error(self, login_page, case):
        login_page.input_and_submit(case["username"], case["password"])
        actual = login_page.get_error_message()
        assert actual == case["expected"], f"[{case['case_name']}] 预期提示 {case['expected']}，实际 {actual}"
        assert "auth/login" in login_page.driver.current_url, "登录失败后应停留在登录页"

    @allure.title("{case[tc]} 必填校验：{case[case_name]}")
    @pytest.mark.parametrize("case", params(REQUIRED_CASES))
    def test_login_required(self, login_page, case):
        login_page.input_and_submit(case["username"], case["password"])
        actual = login_page.get_required_message()
        assert actual == case["expected"], f"[{case['case_name']}] 预期提示 {case['expected']}，实际 {actual}"
        assert "auth/login" in login_page.driver.current_url, "必填项为空不应登录成功"

    @pytest.mark.p1
    @allure.title("TC_LOGIN_006 登录后刷新页面保持登录")
    def test_refresh_keeps_login(self, login_page):
        login_page.login(CONFIG["username"], CONFIG["password"])
        login_page.driver.refresh()
        login_page.wait_url_contains("dashboard")
        assert "auth/login" not in login_page.driver.current_url, "刷新后被踢回登录页"

    @pytest.mark.p1
    @allure.title("TC_LOGIN_007 点忘记密码跳转到重置页")
    def test_forgot_password(self, login_page):
        login_page.click_forgot_password()
        assert "requestPasswordResetCode" in login_page.driver.current_url

    @pytest.mark.p2
    @allure.title("TC_LOGIN_013 密码输入框密文显示")
    def test_password_masked(self, login_page):
        assert login_page.get_password_type() == "password", "密码框不是密文，存在泄露风险"

    @pytest.mark.p2
    @allure.title("TC_LOGIN_014 重置密码页点Cancel返回登录页")
    def test_reset_password_cancel(self, login_page):
        login_page.click_forgot_password()
        login_page.cancel_reset_password()
        assert "auth/login" in login_page.driver.current_url
