from datetime import date, datetime, timedelta

import allure
import pytest

from common.case_util import params
from common.yaml_util import load_yaml
from pages.leave_page import LeavePage

DATA = load_yaml("data/leave.yaml")
DATE_CASES = DATA["date_error_cases"]
ENTITLEMENT_CASES = DATA["entitlement_error_cases"]


def next_workday():
    """一周后的第一个工作日，按OrangeHRM的 yyyy-dd-mm 格式返回
    不写死日期：写死的日期过几个月就变成过去时间或落在周末，用例就会莫名失败"""
    day = date.today() + timedelta(days=7)
    while day.weekday() >= 5:
        day += timedelta(days=1)
    return day.strftime("%Y-%d-%m")


@pytest.fixture
def leave(login):
    page = LeavePage(login)
    page.open_list()
    return page


@pytest.fixture
def temp_entitlement(temp_employee, leave):
    """前置：给测试员工加10天假期额度；员工删除时额度一起没了，不用单独清理"""
    leave.add_entitlement(temp_employee["last"], "10")
    return temp_employee


@allure.feature("Leave请假")
class TestLeave:

    # ==================== P0 ====================
    @pytest.mark.p0
    @allure.title("TC_LEAVE_001 给员工添加假期额度")
    def test_add_entitlement(self, temp_employee, leave):
        leave.add_entitlement(temp_employee["last"], "10")
        # 列表里额度显示的是 "10"（确认弹窗里写的是10.00，两处格式不一样）
        cells = [cell for row in leave.get_rows() for cell in row]
        assert "10" in cells, f"额度列表里没有10天，实际 {cells}"

    @pytest.mark.p0
    @allure.title("TC_LEAVE_002 分配请假后请假列表能查到")
    def test_assign_leave(self, temp_entitlement, leave):
        with allure.step("给有额度的员工分配1天假"):
            leave.open_assign()
            leave.fill_assign(temp_entitlement["last"], next_workday())
            leave.click_assign()
            assert "Successfully" in leave.get_toast_text()
        with allure.step("请假列表按员工搜索（管理员分配的状态是Scheduled）"):
            leave.open_list()
            leave.search_leave(temp_entitlement["last"], extra_status="Scheduled")
            names = [row[LeavePage.COL_EMPLOYEE] for row in leave.get_rows()]
            assert any(temp_entitlement["last"] in n for n in names), f"列表里没有该员工的请假：{names}"

    # ==================== P1 ====================
    @pytest.mark.p1
    @allure.title("TC_LEAVE_003 请假列表默认带出当前假期周期")
    def test_default_date_range(self, leave):
        # 默认范围来自后台Leave Period配置，公共演示站别人能改（跑出过 2026-31-12 和 2027-31-01 两种）
        # 所以不写死具体日期，只断言不受环境影响的规则：格式合法、From早于To
        from_text, to_text = leave.get_dates()
        from_date = datetime.strptime(from_text, "%Y-%d-%m")
        to_date = datetime.strptime(to_text, "%Y-%d-%m")
        assert from_date < to_date, f"默认From {from_text} 应早于To {to_text}"

    @pytest.mark.p1
    @allure.title("TC_LEAVE_004 请假列表默认只看待审批")
    def test_default_status(self, leave):
        assert leave.get_status_chips() == ["Pending Approval"]

    @pytest.mark.p1
    @allure.title("TC_LEAVE_005 预置假期类型齐全")
    def test_leave_types(self, leave):
        names = leave.get_leave_type_names()
        assert LeavePage.LEAVE_TYPE_NAME in names, f"假期类型里没有 {LeavePage.LEAVE_TYPE_NAME}：{names}"

    @pytest.mark.p1
    @allure.title("TC_LEAVE_006 余额不足时分配请假给出提示")
    def test_assign_without_balance(self, temp_employee, leave):
        # 测试员工刚新建，没有任何额度
        leave.open_assign()
        leave.fill_assign(temp_employee["last"], next_workday())
        leave.click_assign()
        text = leave.get_dialog_text()
        assert "balance" in text.lower(), f"应弹出余额不足提示，实际：{text}"
        leave.close_dialog()

    # ==================== P2 ====================
    @allure.title("{case[tc]} 日期校验：{case[case_name]}")
    @pytest.mark.parametrize("case", params(DATE_CASES))
    def test_date_validation(self, leave, case):
        leave.set_dates(case["from_date"], case["to_date"])
        errors = leave.get_field_errors()
        assert case["expected"] in errors, f"[{case['case_name']}] 预期 {case['expected']}，实际 {errors}"

    @pytest.mark.p2
    @allure.title("TC_LEAVE_008 From等于To")
    def test_same_from_to_date(self, leave):
        # 边界值的另一侧：和"To早一天报错"成对，单独写因为预期是"没有错误"，不塞进上面的数据驱动
        leave.set_dates("2026-15-06", "2026-15-06")
        assert leave.get_field_errors(timeout=2) == []

    @pytest.mark.p2
    @allure.title("TC_LEAVE_012 月份超过12（现状记录）")
    def test_month_over_12_auto_swap(self, leave):
        # 自动化跑出来的发现：输入 2026-01-13（13月），系统不报错，而是把它改成 2026-13-01（1月13日）
        # 需求里没写这个行为，是容错设计还是bug要问产品。这条用例记录的是"现状"，
        # 产品确认是bug后，把预期改成"报格式错误"即可
        leave.set_dates("2026-01-13", "2026-31-12")
        assert leave.get_dates()[0] == "2026-13-01"
        assert leave.get_field_errors(timeout=2) == []

    @pytest.mark.p2
    @allure.title("TC_LEAVE_013 分配请假必填项为空")
    def test_assign_required(self, leave):
        leave.open_assign()
        leave.click_assign()
        errors = leave.get_field_errors()
        assert errors.count("Required") >= 3, f"员工、类型、日期都应提示Required，实际 {errors}"

    @allure.title("{case[tc]} 额度校验：{case[case_name]}")
    @pytest.mark.parametrize("case", params(ENTITLEMENT_CASES))
    def test_entitlement_validation(self, leave, case):
        leave.open_add_entitlement()
        leave.input_entitlement(case["value"])
        errors = leave.get_field_errors()
        assert case["expected"] in errors, f"[{case['case_name']}] 预期 {case['expected']}，实际 {errors}"
