import allure
import pytest

from pages.dashboard_page import DashboardPage

# 菜单跳转：每条带自己的用例ID和优先级（PIM是核心模块入口，定P0）
MENUS = [
    ("TC_DASH_004", "p0", "PIM", "pim/viewEmployeeList", "PIM"),
    ("TC_DASH_006", "p1", "Admin", "admin/viewSystemUsers", "Admin"),
    ("TC_DASH_007", "p1", "Leave", "leave/viewLeaveList", "Leave"),
    ("TC_DASH_008", "p1", "Recruitment", "recruitment/viewCandidates", "Recruitment"),
    ("TC_DASH_009", "p1", "My Info", "pim/viewPersonalDetails", "PIM"),
    ("TC_DASH_010", "p1", "Directory", "directory/viewDirectory", "Directory"),
]
MENU_PARAMS = [
    pytest.param(tc, menu, url, title, id=f"{tc} {menu}", marks=getattr(pytest.mark, pri))
    for tc, pri, menu, url, title in MENUS
]

WIDGETS = [
    "Time at Work", "My Actions", "Quick Launch", "Buzz Latest Posts",
    "Employees on Leave Today", "Employee Distribution by Sub Unit",
    "Employee Distribution by Location",
]


@pytest.fixture
def dashboard(login):
    """登录后默认就在Dashboard"""
    page = DashboardPage(login)
    page.wait_loading_gone()
    return page


@allure.feature("Dashboard与导航")
class TestDashboard:

    @pytest.mark.p0
    @allure.title("TC_DASH_001 登录后Dashboard页头标题正确")
    def test_dashboard_title(self, dashboard):
        assert dashboard.get_header_title() == "Dashboard"

    @pytest.mark.p0
    @allure.title("TC_DASH_002 退出登录后回到登录页")
    def test_logout(self, dashboard):
        dashboard.logout()
        assert "auth/login" in dashboard.driver.current_url

    @pytest.mark.p0
    @allure.title("TC_DASH_003 退出后直接访问内部页面被重定向")
    def test_access_after_logout(self, dashboard):
        dashboard.logout()
        dashboard.open(DashboardPage.PATH)
        dashboard.wait_url_contains("auth/login")
        assert "auth/login" in dashboard.driver.current_url, "退出后仍能访问内部页面，存在越权风险"

    @allure.title("{tc} 菜单跳转：{menu}")
    @pytest.mark.parametrize("tc, menu, url_part, title", MENU_PARAMS)
    def test_menu_navigation(self, dashboard, tc, menu, url_part, title):
        dashboard.go_menu(menu)
        dashboard.wait_url_contains(url_part)
        assert dashboard.get_header_title().startswith(title), (
            f"点 {menu} 后页头应为 {title}，实际 {dashboard.get_header_title()}"
        )

    @pytest.mark.p1
    @allure.title("TC_DASH_005 Dashboard显示全部7个组件")
    def test_dashboard_widgets(self, dashboard):
        actual = dashboard.get_widget_names()
        missing = [w for w in WIDGETS if w not in actual]
        assert not missing, f"缺少组件：{missing}，实际显示：{actual}"

    @pytest.mark.p2
    @allure.title("TC_DASH_011 菜单搜索框过滤")
    def test_menu_search(self, dashboard):
        assert dashboard.search_menu("Recru") == ["Recruitment"]

    @pytest.mark.p2
    @allure.title("TC_DASH_012 菜单搜索不区分大小写")
    def test_menu_search_case_insensitive(self, dashboard):
        assert dashboard.search_menu("admin") == ["Admin"]

    @pytest.mark.p2
    @allure.title("TC_DASH_013 菜单搜索无匹配")
    def test_menu_search_no_match(self, dashboard):
        assert dashboard.search_menu("xyz") == []

    @pytest.mark.p2
    @allure.title("TC_DASH_014 修改密码两次新密码不一致")
    def test_change_password_mismatch(self, dashboard):
        dashboard.open_change_password()
        dashboard.fill_new_password("Abc12345", "Abc99999")
        assert "Passwords do not match" in dashboard.get_field_errors()
