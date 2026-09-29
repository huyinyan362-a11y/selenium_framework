import allure
import pytest

from common.data_factory import unique_suffix
from pages.myinfo_page import MyInfoPage


@pytest.fixture
def myinfo(login):
    page = MyInfoPage(login)
    page.open_my_info()
    return page


@allure.feature("My Info个人信息")
class TestMyInfo:
    # 注意：这里改的是共用Admin账号的真实数据，每条修改类用例都先记原值、结束时恢复

    @pytest.mark.p0
    @allure.title("TC_MYINFO_001 修改Other Id刷新后仍是新值")
    def test_update_other_id(self, myinfo):
        original = myinfo.get_other_id()
        new_value = unique_suffix()
        try:
            with allure.step("修改并保存"):
                myinfo.set_other_id(new_value)
                assert "Successfully Updated" in myinfo.save_and_get_toast()
            with allure.step("刷新页面，验证数据真的保存到后端"):
                # 只看提示不够：提示是前端弹的，刷新后值还在才说明后端存了
                myinfo.open_my_info()
                assert myinfo.get_other_id() == new_value
        finally:
            myinfo.open_my_info()
            myinfo.set_other_id(original)
            myinfo.save()

    @pytest.mark.p1
    @allure.title("TC_MYINFO_002 修改国籍刷新后仍是新值")
    def test_update_nationality(self, myinfo):
        original = myinfo.get_nationality()
        new_value = "Japanese" if original == "Chinese" else "Chinese"
        try:
            myinfo.set_nationality(new_value)
            assert "Successfully Updated" in myinfo.save_and_get_toast()
            myinfo.open_my_info()
            assert myinfo.get_nationality() == new_value
        finally:
            myinfo.open_my_info()
            myinfo.set_nationality(original)
            myinfo.save()

    @pytest.mark.p1
    @allure.title("TC_MYINFO_003 切换到Contact Details页")
    def test_open_contact_details(self, myinfo):
        myinfo.open_tab("Contact Details", "contactDetails")
        assert myinfo.is_visible(MyInfoPage.MOBILE), "Contact Details页没有显示联系方式表单"

    @pytest.mark.p1
    @allure.title("TC_MYINFO_004 修改手机号刷新后仍是新值")
    def test_update_mobile(self, myinfo):
        myinfo.open_contact_details()
        original = myinfo.get_value(MyInfoPage.MOBILE)
        new_value = f"138{unique_suffix()}"
        try:
            myinfo.input_text(MyInfoPage.MOBILE, new_value)
            assert "Successfully Updated" in myinfo.save_and_get_toast()
            myinfo.open_contact_details()
            assert myinfo.get_value(MyInfoPage.MOBILE) == new_value
        finally:
            myinfo.open_contact_details()
            myinfo.input_text(MyInfoPage.MOBILE, original)
            myinfo.save()

    @pytest.mark.p1
    @allure.title("TC_MYINFO_005 新增并删除紧急联系人")
    def test_emergency_contact(self, myinfo):
        name = f"Auto{unique_suffix()}"
        myinfo.open_emergency_contacts()
        try:
            with allure.step("新增紧急联系人"):
                myinfo.add_emergency_contact(name, "Friend", "13800000000")
                assert myinfo.emergency_contact_exists(name)
            with allure.step("删除后列表里消失"):
                myinfo.delete_row_containing(name)
                assert not myinfo.emergency_contact_exists(name)
        finally:
            if myinfo.emergency_contact_exists(name):
                myinfo.delete_row_containing(name)

    @pytest.mark.p2
    @allure.title("TC_MYINFO_006 清空First Name保存")
    def test_first_name_required(self, myinfo):
        myinfo.clear_first_name()
        myinfo.save()
        assert "Required" in myinfo.get_field_errors()

    @pytest.mark.p2
    @allure.title("TC_MYINFO_007 清空Last Name保存")
    def test_last_name_required(self, myinfo):
        myinfo.clear_last_name()
        myinfo.save()
        assert "Required" in myinfo.get_field_errors()

    @pytest.mark.p2
    @allure.title("TC_MYINFO_008 工作邮箱格式非法")
    def test_invalid_work_email(self, myinfo):
        # 这个字段失焦时不校验，点Save才校验
        myinfo.open_contact_details()
        myinfo.input_text(MyInfoPage.WORK_EMAIL, "abc")
        myinfo.save()
        assert "Expected format: admin@example.com" in myinfo.get_field_errors()

    @pytest.mark.p2
    @allure.title("TC_MYINFO_009 紧急联系人必填项为空")
    def test_emergency_contact_required(self, myinfo):
        myinfo.open_emergency_contacts()
        myinfo.open_emergency_form()
        myinfo.save()
        errors = myinfo.get_field_errors()
        assert errors.count("Required") == 2, f"姓名、关系应提示Required，实际 {errors}"
        assert "At least one phone number is required" in errors
