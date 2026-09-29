from selenium.webdriver.common.by import By

from pages.main_layout import MainLayout


class AdminPage(MainLayout):
    LIST_PATH = "/web/index.php/admin/viewSystemUsers"

    # 列表页搜索区
    USERNAME = MainLayout.field_input("Username")
    ROLE = MainLayout.field_dropdown("User Role")
    STATUS = MainLayout.field_dropdown("Status")
    SEARCH_BTN = (By.XPATH, "//button[@type='submit']")
    # Admin页的Reset不是type='reset'（和PIM页结构不同），按文字定位
    RESET_BTN = (By.XPATH, "//button[normalize-space()='Reset']")
    ADD_BTN = (By.XPATH, "//button[normalize-space()='Add']")

    # 新增用户页
    EMPLOYEE_NAME = (By.XPATH, "//input[@placeholder='Type for hints...']")
    PASSWORD = MainLayout.field_input("Password")
    CONFIRM_PASSWORD = MainLayout.field_input("Confirm Password")
    SAVE_BTN = (By.XPATH, "//button[@type='submit']")

    # 表格列：['', Username, User Role, Employee Name, Status, Actions]
    COL_USERNAME, COL_ROLE, COL_EMPLOYEE, COL_STATUS = 1, 2, 3, 4

    def open_list(self):
        self.open(self.LIST_PATH)
        self.wait_loading_gone()

    def search(self, username=None, role=None, status=None):
        if username:
            self.input_text(self.USERNAME, username)
        if role:
            self.select_dropdown(self.ROLE, role)
        if status:
            self.select_dropdown(self.STATUS, status)
        self.click(self.SEARCH_BTN)
        self.wait_loading_gone()

    def click_reset(self):
        self.click(self.RESET_BTN)
        self.wait_loading_gone()

    def get_username_value(self):
        return self.get_value(self.USERNAME)

    def column(self, index):
        """表格某一列的所有值"""
        return [row[index] for row in self.get_rows()]

    # ---------- 新增用户 ----------
    def open_add_form(self):
        self.click(self.ADD_BTN)
        self.wait_url_contains("saveSystemUser")

    def fill_user_form(self, role=None, employee=None, status=None,
                       username=None, password=None, confirm=None):
        """只填不提交，校验类用例用；参数为None的字段不填"""
        if role:
            self.select_dropdown(self.ROLE, role)
        if employee:
            self.input_autocomplete(self.EMPLOYEE_NAME, employee)
        if status:
            self.select_dropdown(self.STATUS, status)
        if username:
            self.input_text(self.USERNAME, username)
        if password:
            self.input_text(self.PASSWORD, password)
        if confirm:
            self.input_text(self.CONFIRM_PASSWORD, confirm)
        # 用户名是否重复、密码强度这些校验在失焦时才触发
        self.blur()

    def click_save(self):
        self.click(self.SAVE_BTN)

    def add_user(self, role, employee, status, username, password):
        """完整新增：保存成功后回到用户列表页"""
        self.open_add_form()
        self.fill_user_form(role, employee, status, username, password, password)
        self.click_save()
        self.wait_url_contains("viewSystemUsers")
        self.wait_loading_gone()

    def delete_user_if_exists(self, username):
        self.open_list()
        self.search(username=username)
        if self.get_record_count() > 0:
            self.delete_row_containing(username)

    def delete_user(self, username):
        """按用户名搜到后删除"""
        self.search(username=username)
        self.delete_row_containing(username)

    def change_user_status(self, username, status):
        """搜到用户 → 点铅笔进编辑页 → 改状态 → 保存，回到列表页"""
        self.search(username=username)
        self.click_row_edit(username)
        self.wait_url_contains("saveSystemUser")
        self.wait_loading_gone()
        # 编辑页数据是异步回填的：用户名还没回填就改下拉，会被回填覆盖
        self.wait.until(lambda d: self.get_value(self.USERNAME))
        self.select_dropdown(self.STATUS, status)
        self.click_save()
        self.wait_url_contains("viewSystemUsers")
        self.wait_loading_gone()

    # ---------- Job Titles（Admin → Job → Job Titles） ----------
    JOB_TITLE_PATH = "/web/index.php/admin/viewJobTitleList"
    JOB_TITLE_INPUT = MainLayout.field_input("Job Title")

    def open_job_titles(self):
        self.open(self.JOB_TITLE_PATH)
        self.wait_loading_gone()

    def add_job_title(self, title):
        """新增职位，保存后回到职位列表
        注意新增页地址是 saveJobTitle（单数），不是 saveJobTitles，等错了URL会一直超时"""
        self.open_job_titles()
        self.click(self.ADD_BTN)
        self.wait_url_contains("saveJobTitle")
        self.wait_for_element(self.JOB_TITLE_INPUT)
        self.input_text(self.JOB_TITLE_INPUT, title)
        self.click(self.SAVE_BTN)
        self.wait_url_contains("viewJobTitleList")
        self.wait_loading_gone()

    def job_title_exists(self, title):
        return self.is_visible((By.XPATH, self.row_containing(title)), timeout=5)

    def delete_job_title_if_exists(self, title):
        self.open_job_titles()
        if self.job_title_exists(title):
            self.delete_row_containing(title)
