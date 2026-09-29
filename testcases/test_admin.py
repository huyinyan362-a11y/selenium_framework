import allure
import pytest

from common.data_factory import new_system_user, unique_suffix
from pages.admin_page import AdminPage


@pytest.fixture
def admin(login):
    page = AdminPage(login)
    page.open_list()
    return page


@pytest.fixture
def temp_system_user(temp_employee, admin):
    """前置：给PIM建的测试员工开一个ESS账号；后置：删掉账号（员工由temp_employee清理）
    fixture依赖链：temp_system_user → temp_employee → login → driver"""
    user = new_system_user()
    admin.open_list()
    admin.add_user("ESS", temp_employee["last"], "Enabled", user["username"], user["password"])
    yield user
    admin.delete_user_if_exists(user["username"])


ROLE_PARAMS = [
    pytest.param("TC_ADMIN_004", "Admin", id="TC_ADMIN_004 Admin"),
    pytest.param("TC_ADMIN_005", "ESS", id="TC_ADMIN_005 ESS"),
]


@allure.feature("Admin用户管理")
class TestAdmin:

    # ==================== P0 ====================
    @pytest.mark.p0
    @allure.title("TC_ADMIN_001 跨模块：给PIM新建员工开系统账号")
    def test_add_system_user_for_new_employee(self, temp_employee, admin):
        user = new_system_user()
        try:
            with allure.step("新增系统用户，关联刚在PIM建的员工"):
                admin.add_user("ESS", temp_employee["last"], "Enabled", user["username"], user["password"])
            with allure.step("按用户名搜索，验证角色、员工、状态"):
                admin.search(username=user["username"])
                rows = admin.get_rows()
                assert len(rows) == 1, f"应搜到1条，实际 {len(rows)} 条"
                row = rows[0]
                assert row[AdminPage.COL_ROLE] == "ESS"
                assert temp_employee["last"] in row[AdminPage.COL_EMPLOYEE]
                assert row[AdminPage.COL_STATUS] == "Enabled"
        finally:
            admin.delete_user_if_exists(user["username"])

    @pytest.mark.p0
    @allure.title("TC_ADMIN_002 删除系统用户")
    def test_delete_system_user(self, temp_system_user, admin):
        admin.delete_user(temp_system_user["username"])
        admin.search(username=temp_system_user["username"])
        assert admin.get_record_count() == 0, "删除后仍能搜到该用户"

    # ==================== P1 ====================
    @pytest.mark.p1
    @allure.title("TC_ADMIN_003 按用户名搜索")
    def test_search_by_username(self, admin):
        admin.search(username="Admin")
        usernames = admin.column(AdminPage.COL_USERNAME)
        assert usernames, "Admin账号应该存在"
        assert all(u == "Admin" for u in usernames), f"结果里有别的用户名：{usernames}"

    @pytest.mark.p1
    @allure.title("{tc} 按角色筛选：{role}")
    @pytest.mark.parametrize("tc, role", ROLE_PARAMS)
    def test_filter_by_role(self, admin, tc, role):
        admin.search(role=role)
        roles = admin.column(AdminPage.COL_ROLE)
        assert roles, f"角色 {role} 应至少有1个用户"
        assert set(roles) == {role}, f"筛选 {role}，结果里出现了 {set(roles)}"

    @pytest.mark.p1
    @allure.title("TC_ADMIN_006 按状态筛选：Enabled")
    def test_filter_by_status(self, admin):
        admin.search(status="Enabled")
        statuses = admin.column(AdminPage.COL_STATUS)
        assert statuses and set(statuses) == {"Enabled"}, f"实际状态：{set(statuses)}"

    @pytest.mark.p1
    @allure.title("TC_ADMIN_007 搜索不存在的用户名")
    def test_search_not_found(self, admin):
        admin.search(username="no_such_user_x")
        assert admin.get_record_count() == 0

    @pytest.mark.p1
    @allure.title("TC_ADMIN_008 Reset清空搜索条件")
    def test_reset(self, admin):
        admin.input_text(AdminPage.USERNAME, "Admin")
        admin.click_reset()
        assert admin.get_username_value() == ""

    @pytest.mark.p1
    @allure.title("TC_ADMIN_009 组合搜索：用户名Admin+角色ESS")
    def test_search_admin_with_ess_role(self, admin):
        # 判定表：两个条件是"与"关系，Admin账号是Admin角色，加上ESS条件后应无记录
        admin.search(username="Admin", role="ESS")
        assert admin.get_record_count() == 0

    @pytest.mark.p1
    @allure.title("TC_ADMIN_010 禁用系统用户后按Disabled能搜到")
    def test_disable_user(self, temp_system_user, admin):
        admin.change_user_status(temp_system_user["username"], "Disabled")
        admin.open_list()
        admin.search(username=temp_system_user["username"], status="Disabled")
        assert admin.column(AdminPage.COL_STATUS) == ["Disabled"]

    @pytest.mark.p1
    @allure.title("TC_ADMIN_011 新增职位Job Title")
    def test_add_job_title(self, admin):
        title = f"AutoJob{unique_suffix()}"
        try:
            admin.add_job_title(title)
            assert admin.job_title_exists(title), f"职位列表里没有 {title}"
        finally:
            admin.delete_job_title_if_exists(title)

    # ==================== P2 表单校验 ====================
    @pytest.mark.p2
    @allure.title("TC_ADMIN_012 新增用户什么都不填")
    def test_add_user_required(self, admin):
        admin.open_add_form()
        admin.click_save()
        errors = admin.get_field_errors()
        # 实测4个必填：User Role、Employee Name、Status、Username（密码框为空时提示的是别的文字）
        assert errors.count("Required") >= 4, f"必填提示不足：{errors}"
        assert "saveSystemUser" in admin.driver.current_url

    @pytest.mark.p2
    @allure.title("TC_ADMIN_013 两次密码不一致")
    def test_password_mismatch(self, admin):
        admin.open_add_form()
        admin.fill_user_form(password="Abc12345", confirm="Abc99999")
        assert "Passwords do not match" in admin.get_field_errors()

    @pytest.mark.p2
    @allure.title("TC_ADMIN_014 用户名4位（最小长度-1）")
    def test_username_too_short(self, admin):
        admin.open_add_form()
        admin.fill_user_form(username="abcd")
        admin.click_save()
        assert "Should be at least 5 characters" in admin.get_field_errors()

    @pytest.mark.p2
    @allure.title("TC_ADMIN_015 用户名5位（最小长度）")
    def test_username_min_length(self, admin):
        # 边界值另一侧：和上一条成对，5位是下限，不该出现长度提示
        admin.open_add_form()
        admin.fill_user_form(username=f"u{unique_suffix()[-4:]}")
        # 长度提示可能在输入过程中短暂出现过，等它消失（最多8秒）再断言
        errors = admin.wait_field_errors(lambda e: "Should be at least 5 characters" not in e)
        assert "Should be at least 5 characters" not in errors

    @pytest.mark.p2
    @allure.title("TC_ADMIN_016 用户名已存在")
    def test_username_exists(self, admin):
        # 重名校验要调接口，结果出来前页面会先显示长度校验的旧提示，所以轮询等结果
        admin.open_add_form()
        admin.fill_user_form(username="Admin")
        errors = admin.wait_field_errors(lambda e: "Already exists" in e)
        assert "Already exists" in errors, f"实际提示：{errors}"

    @pytest.mark.p2
    @allure.title("TC_ADMIN_017 密码6位（最小长度-1）")
    def test_password_too_short(self, admin):
        admin.open_add_form()
        admin.fill_user_form(password="Abc123")
        assert "Should have at least 7 characters" in admin.get_field_errors()

    @pytest.mark.p2
    @allure.title("TC_ADMIN_018 密码不含数字")
    def test_password_without_number(self, admin):
        admin.open_add_form()
        admin.fill_user_form(password="Abcdefgh")
        assert "Your password must contain minimum 1 number" in admin.get_field_errors()
