import allure
import pytest

from pages.directory_page import DirectoryPage
from pages.pim_page import PIMPage


@pytest.fixture
def directory(login):
    page = DirectoryPage(login)
    page.open_directory()
    return page


@allure.feature("Directory通讯录")
class TestDirectory:

    @pytest.mark.p0
    @allure.title("TC_DIR_001 跨模块：PIM新建的员工在通讯录能搜到")
    def test_new_employee_in_directory(self, temp_employee, directory):
        directory.open_directory()
        directory.search_by_name(temp_employee["last"])
        names = directory.get_card_names()
        assert len(names) == 1, f"应搜到1张卡片，实际 {names}"
        assert temp_employee["last"] in names[0]

    @pytest.mark.p1
    @allure.title("TC_DIR_002 通讯录默认显示员工卡片")
    def test_default_cards(self, directory):
        assert directory.get_record_count() > 0
        assert directory.get_card_names(), "默认应显示员工卡片"

    @pytest.mark.p1
    @allure.title("TC_DIR_003 选中员工后Reset")
    def test_reset(self, directory):
        # 用页面上第一张卡片的名字，保证下拉里一定有这个人
        first_word = directory.get_card_names()[0].split()[0]
        directory.input_autocomplete(DirectoryPage.NAME_INPUT, first_word)
        directory.click_reset()
        assert directory.get_name_value() == ""

    @pytest.mark.p1
    @allure.title("TC_DIR_004 跨模块：PIM删除员工后通讯录搜不到")
    def test_deleted_employee_not_in_directory(self, temp_employee, directory):
        with allure.step("在PIM删除测试员工"):
            pim = PIMPage(directory.driver)
            pim.open_list()
            pim.delete_employee_by_id(temp_employee["id"])
        with allure.step("通讯录搜这个员工"):
            directory.open_directory()
            hints = directory.get_autocomplete_hints(DirectoryPage.NAME_INPUT, temp_employee["last"])
            assert hints == ["No Records Found"], f"删除的员工仍出现在通讯录提示里：{hints}"

    @pytest.mark.p2
    @allure.title("TC_DIR_005 只输入未选提示就Reset（现状记录）")
    def test_reset_with_unselected_text(self, directory):
        # 自动化跑出来的发现：自动补全框只输入不选，表单里记录的值其实还是空，
        # Reset把"空"恢复成"空"，界面上的文字没被清掉。用户看到点了Reset框里还有字
        # 这条记录现状；修复后把预期改成 == "" 即可
        directory.input_text(DirectoryPage.NAME_INPUT, "abc")
        directory.click_reset()
        assert directory.get_name_value() == "abc"

    @pytest.mark.p2
    @allure.title("TC_DIR_006 搜索不存在的姓名")
    def test_search_name_not_found(self, directory):
        hints = directory.get_autocomplete_hints(DirectoryPage.NAME_INPUT, "NotExistUser999")
        assert hints == ["No Records Found"], f"实际提示：{hints}"

    @pytest.mark.p2
    @allure.title("TC_DIR_007 点卡片显示员工详情")
    def test_card_detail(self, directory):
        name = directory.open_first_card()
        assert name.split()[0] in directory.get_sidebar_text(), "右侧详情不是点的这个员工"
