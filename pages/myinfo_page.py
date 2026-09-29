from selenium.webdriver.common.by import By

from pages.main_layout import MainLayout


class MyInfoPage(MainLayout):
    PATH = "/web/index.php/pim/viewMyDetails"  # 会自动跳到 viewPersonalDetails/empNumber/当前用户

    # 每个tab的表单都只有一个主Save，放在第一个；Personal Details页第二个Save属于自定义字段
    SAVE_BTN = (By.XPATH, "(//button[@type='submit'])[1]")

    # ---------- Personal Details ----------
    FIRST_NAME = (By.NAME, "firstName")
    LAST_NAME = (By.NAME, "lastName")
    OTHER_ID = MainLayout.field_input("Other Id")
    NATIONALITY = MainLayout.field_dropdown("Nationality")

    def open_my_info(self):
        self.open(self.PATH)
        self.wait_url_contains("viewPersonalDetails")
        self.wait_loading_gone()
        # 数据异步回填：名字有值了才算加载完，否则读到的是空值、改的值会被覆盖
        self.wait.until(lambda d: self.get_value(self.FIRST_NAME))

    def get_other_id(self):
        return self.get_value(self.OTHER_ID)

    def set_other_id(self, value):
        self.input_text(self.OTHER_ID, value)

    def clear_first_name(self):
        self.input_text(self.FIRST_NAME, "")

    def clear_last_name(self):
        self.input_text(self.LAST_NAME, "")

    def get_nationality(self):
        return self.get_dropdown_text(self.NATIONALITY)

    def set_nationality(self, name):
        self.select_dropdown(self.NATIONALITY, name)

    def save(self):
        self.click(self.SAVE_BTN)

    def save_and_get_toast(self):
        """保存并返回右下角提示文字，比如 'Success\\nSuccessfully Updated'"""
        self.save()
        return self.get_toast_text()

    # ---------- 左侧tab切换 ----------
    def open_tab(self, tab_name, url_part):
        self.click((By.XPATH, f"//a[contains(@class,'orangehrm-tabs-item')][normalize-space()='{tab_name}']"))
        self.wait_url_contains(url_part)
        self.wait_loading_gone()

    # ---------- Contact Details ----------
    MOBILE = MainLayout.field_input("Mobile")
    WORK_EMAIL = MainLayout.field_input("Work Email")

    def open_contact_details(self):
        self.open_my_info()
        self.open_tab("Contact Details", "contactDetails")
        self.wait_for_element(self.MOBILE)

    # ---------- Emergency Contacts ----------
    EC_ADD_BTN = (By.XPATH, "(//button[normalize-space()='Add'])[1]")  # 第二个Add属于附件
    EC_NAME = MainLayout.field_input("Name")
    EC_RELATIONSHIP = MainLayout.field_input("Relationship")

    def open_emergency_contacts(self):
        self.open_my_info()
        self.open_tab("Emergency Contacts", "viewEmergencyContacts")

    def open_emergency_form(self):
        self.click(self.EC_ADD_BTN)
        self.wait_for_element(self.EC_NAME)

    def add_emergency_contact(self, name, relationship, mobile):
        self.open_emergency_form()
        self.input_text(self.EC_NAME, name)
        self.input_text(self.EC_RELATIONSHIP, relationship)
        self.input_text(self.MOBILE, mobile)
        self.save()
        self.wait_loading_gone()
        self.wait_for_element((By.XPATH, self.row_containing(name)))

    def emergency_contact_exists(self, name):
        return self.is_visible((By.XPATH, self.row_containing(name)), timeout=3)
