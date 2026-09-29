import os

import allure
import pytest

from common.data_factory import new_employee
from common.yaml_util import ROOT_DIR
from pages.pim_page import PIMPage

# 不存在的员工ID。注意Employee Id最多10位：超长时页面不报错，但搜索条件不生效，会显示全部员工
NOT_EXIST_ID = "NOEXIST99"
AVATAR = os.path.join(ROOT_DIR, "resources", "avatar.png")


@pytest.fixture
def pim(login):
    """已登录并打开员工列表的PIM页面对象"""
    page = PIMPage(login)
    page.open_list()
    return page


@allure.feature("PIM员工管理")
class TestPIM:

    # ==================== P0 核心主流程 ====================
    @pytest.mark.p0
    @allure.title("TC_PIM_001 新增员工-仅填必填项")
    def test_add_employee_required_only(self, pim):
        emp = new_employee()
        emp_id = None
        try:
            with allure.step("只填姓名，ID用系统自动生成的"):
                emp_id = pim.add_employee_required_only(emp["first"], emp["last"])
            with allure.step("回列表按姓名搜索"):
                pim.open_list()
                pim.search_by_name(emp["last"])
                rows = pim.get_rows()
                assert len(rows) == 1, f"按姓 {emp['last']} 应搜到1条，实际 {len(rows)} 条"
                assert rows[0][1] == emp_id, f"ID应为系统生成的 {emp_id}，实际 {rows[0][1]}"
        finally:
            if emp_id:
                pim.delete_employee_if_exists(emp_id)

    @pytest.mark.p0
    @allure.title("TC_PIM_002 新增员工-指定Employee Id")
    def test_add_employee_success(self, pim):
        emp = new_employee()
        try:
            with allure.step("填写姓名和ID并保存"):
                pim.add_employee(emp["first"], emp["last"], emp["id"])
            with allure.step("回列表按ID搜索，验证新员工存在"):
                pim.open_list()
                pim.search_by_id(emp["id"])
                rows = pim.get_rows()
                assert len(rows) == 1, f"按ID {emp['id']} 应搜到1条，实际 {len(rows)} 条"
                assert rows[0][1] == emp["id"], f"ID列应为 {emp['id']}，实际 {rows[0][1]}"
                assert rows[0][3] == emp["last"], f"姓应为 {emp['last']}，实际 {rows[0][3]}"
        finally:
            # 这条用例自己新建的数据，断言失败也要清理
            pim.delete_employee_if_exists(emp["id"])

    @pytest.mark.p0
    @allure.title("TC_PIM_003 按员工ID搜索")
    def test_search_by_id(self, pim, temp_employee):
        pim.search_by_id(temp_employee["id"])
        rows = pim.get_rows()
        assert pim.get_record_count() == 1, f"应搜到1条，实际 {pim.get_record_count()} 条"
        assert rows[0][1] == temp_employee["id"]

    @pytest.mark.p0
    @allure.title("TC_PIM_004 编辑员工姓名")
    def test_edit_employee_name(self, pim, temp_employee):
        with allure.step("进入员工详情，改名字并保存"):
            pim.open_employee(temp_employee["id"])
            assert "Successfully Updated" in pim.update_first_name("Edited")
        with allure.step("回列表搜索，验证显示新名字"):
            pim.open_list()
            pim.search_by_id(temp_employee["id"])
            rows = pim.get_rows()
            assert "Edited" in rows[0][2], f"名字列应为Edited，实际 {rows[0][2]}"

    @pytest.mark.p0
    @allure.title("TC_PIM_005 删除员工")
    def test_delete_employee(self, pim, temp_employee):
        with allure.step("搜到该员工并删除"):
            pim.delete_employee_by_id(temp_employee["id"])
        with allure.step("再搜一次，应无记录"):
            pim.search_by_id(temp_employee["id"])
            assert pim.get_record_count() == 0, "删除后仍能搜到该员工"

    @pytest.mark.p0
    @allure.title("TC_PIM_006 按员工姓名搜索")
    def test_search_by_name(self, pim, temp_employee):
        pim.search_by_name(temp_employee["last"])
        rows = pim.get_rows()
        assert len(rows) == 1, f"按姓 {temp_employee['last']} 应搜到1条，实际 {len(rows)} 条"
        assert rows[0][3] == temp_employee["last"]

    # ==================== P1 重要功能 ====================
    @pytest.mark.p1
    @allure.title("TC_PIM_007 点Add跳转到新增员工页")
    def test_click_add_button(self, pim):
        pim.click_add()
        assert "addEmployee" in pim.driver.current_url

    @pytest.mark.p1
    @allure.title("TC_PIM_008 Reset清空搜索条件")
    def test_reset_clears_conditions(self, pim):
        pim.input_id("0123")
        pim.click_reset()
        assert pim.get_employee_id_value() == "", "Reset后Employee Id输入框未清空"

    @pytest.mark.p1
    @allure.title("TC_PIM_009 搜索不存在的员工ID")
    def test_search_not_found(self, pim):
        pim.search_by_id(NOT_EXIST_ID)
        assert pim.get_record_count() == 0
        assert pim.get_rows() == []

    @pytest.mark.p1
    @allure.title("TC_PIM_010 搜索不存在的员工姓名")
    def test_search_name_not_found(self, pim):
        hints = pim.get_autocomplete_hints(PIMPage.NAME_INPUT, "NotExistUser999")
        assert hints == ["No Records Found"], f"下拉提示应为No Records Found，实际 {hints}"

    # 判定表：姓名、ID两个条件，每个"填对/不填/填错"，挑出有代表性的组合
    # 每行 = (用例ID, 用例名, 姓名怎么填, ID怎么填, 预期条数)；"match"=填这个员工的，"wrong"=填不存在的
    SEARCH_TABLE = [
        ("TC_PIM_011", "姓名对+ID对", "match", "match", 1),
        ("TC_PIM_012", "只填姓名", "match", None, 1),
        ("TC_PIM_013", "只填ID", None, "match", 1),
        ("TC_PIM_014", "姓名对+ID错", "match", "wrong", 0),
    ]

    @pytest.mark.p1
    @allure.title("{tc} 组合搜索判定表：{case_name}")
    @pytest.mark.parametrize(
        "tc, case_name, name_mode, id_mode, expected",
        SEARCH_TABLE,
        ids=[f"{row[0]} {row[1]}" for row in SEARCH_TABLE],
    )
    def test_search_combination(self, pim, temp_employee, tc, case_name, name_mode, id_mode, expected):
        name = temp_employee["last"] if name_mode == "match" else None
        emp_id = {"match": temp_employee["id"], "wrong": NOT_EXIST_ID, None: None}[id_mode]
        pim.search(name=name, emp_id=emp_id)
        assert pim.get_record_count() == expected, (
            f"[{case_name}] 预期 {expected} 条，实际 {pim.get_record_count()} 条"
        )

    @pytest.mark.p1
    @allure.title("TC_PIM_015 新增员工上传头像")
    def test_add_employee_with_photo(self, pim):
        emp = new_employee()
        try:
            with allure.step("填姓名、ID，选择头像文件"):
                pim.click_add()
                pim.fill_employee_form(emp["first"], emp["last"], emp["id"])
                pim.choose_photo(AVATAR)
                assert pim.photo_previewed(), "选择头像后没有出现预览"
            with allure.step("保存"):
                pim.click_save()
                pim.wait_url_contains("viewPersonalDetails")
        finally:
            pim.delete_employee_if_exists(emp["id"])

    @pytest.mark.p1
    @allure.title("TC_PIM_016 删除确认弹窗点取消")
    def test_cancel_delete(self, pim, temp_employee):
        pim.search_by_id(temp_employee["id"])
        pim.cancel_delete_row(temp_employee["id"])
        pim.search_by_id(temp_employee["id"])
        assert pim.get_record_count() == 1, "点了取消，员工却被删了"

    # ==================== P2 边界与校验 ====================
    @pytest.mark.p2
    @allure.title("TC_PIM_017 新增员工First Name为空")
    def test_add_employee_first_name_required(self, pim):
        pim.click_add()
        pim.fill_employee_form("", "OnlyLast")
        pim.click_save()
        assert "Required" in pim.get_field_errors()
        assert "addEmployee" in pim.driver.current_url, "必填项为空不应保存成功"

    @pytest.mark.p2
    @allure.title("TC_PIM_018 新增员工Last Name为空")
    def test_add_employee_last_name_required(self, pim):
        pim.click_add()
        pim.fill_employee_form("OnlyFirst", "")
        pim.click_save()
        assert "Required" in pim.get_field_errors()
        assert "addEmployee" in pim.driver.current_url, "必填项为空不应保存成功"

    @pytest.mark.p2
    @allure.title("TC_PIM_019 新增员工ID重复")
    def test_add_employee_duplicate_id(self, pim, temp_employee):
        pim.click_add()
        pim.fill_employee_form("Dup", "Check", temp_employee["id"])
        assert "Employee Id already exists" in pim.get_field_errors(timeout=5)

    @pytest.mark.p2
    @allure.title("TC_PIM_020 First Name超过30个字符")
    def test_first_name_too_long(self, pim):
        # 边界值：30是上限，31是上限+1
        pim.click_add()
        pim.input_text(PIMPage.FIRST_NAME, "a" * 31)
        pim.blur()
        assert "Should not exceed 30 characters" in pim.get_field_errors()

    @pytest.mark.p2
    @allure.title("TC_PIM_021 Employee Id超过10个字符")
    def test_employee_id_too_long(self, pim):
        pim.click_add()
        pim.input_text(PIMPage.FORM_ID_INPUT, "12345678901")
        pim.blur()
        assert "Should not exceed 10 characters" in pim.get_field_errors()

    @pytest.mark.p2
    @allure.title("TC_PIM_022 搜索框Employee Id填11位（现状记录）")
    def test_search_id_too_long(self, pim):
        # 自动化过程中发现：新增页会校验ID最多10位，但列表页搜索框不校验，
        # 11位时页面不报错，搜索条件被悄悄忽略，显示的是全部员工（静默失败，比报错更难发现）
        # 这条记录现状；产品确认是bug后，把预期改成"提示超长"或"无记录"
        pim.search_by_id("NOTEXIST999")
        assert pim.get_record_count() > 0, "现状应为条件不生效、显示全部员工；如果变成0条，说明已修复，更新本用例"
