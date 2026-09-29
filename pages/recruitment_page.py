from selenium.webdriver.common.by import By

from pages.main_layout import MainLayout


class RecruitmentPage(MainLayout):
    LIST_PATH = "/web/index.php/recruitment/viewCandidates"
    ADD_PATH = "/web/index.php/recruitment/addCandidate"

    # 公共演示站会有人关掉模块，这时页面显示 403 Module Forbidden
    FORBIDDEN = (By.XPATH, "//*[normalize-space()='Module Forbidden']")

    # 列表页
    CANDIDATE_NAME = (By.XPATH, "//input[@placeholder='Type for hints...']")
    KEYWORDS = (By.XPATH, "//input[@placeholder='Enter comma seperated words...']")
    SEARCH_BTN = (By.XPATH, "//button[@type='submit']")
    RESET_BTN = (By.XPATH, "//button[normalize-space()='Reset']")

    # 新增候选人页
    FIRST_NAME = (By.NAME, "firstName")
    LAST_NAME = (By.NAME, "lastName")
    EMAIL = MainLayout.field_input("Email")
    CONTACT = MainLayout.field_input("Contact Number")
    VACANCY = MainLayout.field_dropdown("Vacancy")
    SAVE_BTN = (By.XPATH, "//button[@type='submit']")

    # 候选人详情页
    STATUS_TEXT = (By.XPATH, "//p[contains(normalize-space(),'Status:')]")

    # 表格列：['', Vacancy, Candidate, Hiring Manager, Date of Application, Status, Actions]
    COL_CANDIDATE = 2

    def is_forbidden(self):
        return self.is_visible(self.FORBIDDEN, timeout=5)

    def open_list(self):
        self.open(self.LIST_PATH)
        self.wait_loading_gone()

    def open_add_form(self):
        """等表单输入框出现：表单没加载完就点Save，校验不会触发"""
        self.open(self.ADD_PATH)
        self.wait_loading_gone()
        self.wait_for_element(self.FIRST_NAME)

    def fill_candidate(self, first=None, last=None, email=None, contact=None, with_vacancy=False):
        if first:
            self.input_text(self.FIRST_NAME, first)
        if last:
            self.input_text(self.LAST_NAME, last)
        if email:
            self.input_text(self.EMAIL, email)
        if contact:
            self.input_text(self.CONTACT, contact)
        if with_vacancy:
            # 候选人关联了职位空缺，才有Shortlist/Reject这些流转按钮；职位空缺名会变，选第一个
            self.select_first_option(self.VACANCY)
        self.blur()

    def click_save(self):
        self.click(self.SAVE_BTN)

    def add_candidate(self, first, last, email, with_vacancy=False):
        """保存成功后跳转到候选人详情页 addCandidate/{id}"""
        self.open_add_form()
        self.fill_candidate(first, last, email, with_vacancy=with_vacancy)
        self.click_save()
        self.wait_url_contains("addCandidate/")
        self.wait_loading_gone()

    def search_by_name(self, name):
        self.input_autocomplete(self.CANDIDATE_NAME, name)
        self.click(self.SEARCH_BTN)
        self.wait_loading_gone()

    def click_reset(self):
        self.click(self.RESET_BTN)
        self.wait_loading_gone()

    def delete_candidate_if_exists(self, last_name):
        """清理用：先看下拉提示里有没有这个人，没有就直接返回
        不能直接"输入并选中"：用例已经删掉的话下拉只有No Records Found，会一直等到超时"""
        self.open_list()
        if self.is_forbidden():
            return
        hints = self.get_autocomplete_hints(self.CANDIDATE_NAME, last_name)
        if not any(last_name in h for h in hints):
            return
        self.click((By.XPATH, f"//div[@role='listbox']//span[contains(normalize-space(),'{last_name}')]"))
        self.click(self.SEARCH_BTN)
        self.wait_loading_gone()
        # 候选人列显示的是全名，单元格不等于last_name，所以用"包含"匹配
        self.delete_row_containing(last_name, exact=False)

    # ---------- 状态流转（候选人详情页） ----------
    ERROR_TOAST = (By.XPATH, "//div[contains(@class,'oxd-toast')][contains(.,'Error')]")

    def change_status(self, action):
        """点 Shortlist / Reject → 进入状态变更页 → Save
        保存成功：先弹 Success 提示，再跳回详情页 addCandidate/{id}，返回None
        服务端报错：弹 Error 提示、页面停在原地，返回提示文字，交给用例断言（不吞掉错误）
        注意只认Error提示：成功时也会先弹提示再跳转，不能"一出现提示就当失败"""
        self.click((By.XPATH, f"//button[normalize-space()='{action}']"))
        self.wait_url_contains("changeCandidateVacancyStatus")
        self.wait_loading_gone()
        self.click(self.SAVE_BTN)
        self.wait.until(lambda d: "addCandidate" in d.current_url or d.find_elements(*self.ERROR_TOAST))
        if "addCandidate" not in self.driver.current_url:
            return self.get_text(self.ERROR_TOAST)
        self.wait_loading_gone()
        return None

    def get_status(self):
        """详情页上 'Status: Shortlisted' 这一行的文字"""
        return self.get_text(self.STATUS_TEXT)

    # ---------- 职位空缺（Vacancies） ----------
    VACANCY_LIST_PATH = "/web/index.php/recruitment/viewJobVacancy"
    VACANCY_ADD_PATH = "/web/index.php/recruitment/addJobVacancy"
    VACANCY_NAME = MainLayout.field_input("Vacancy Name")
    JOB_TITLE = MainLayout.field_dropdown("Job Title")
    HIRING_MANAGER = (By.XPATH, "//input[@placeholder='Type for hints...']")
    USER_NAME = (By.CSS_SELECTOR, ".oxd-userdropdown-name")

    def open_vacancies(self):
        self.open(self.VACANCY_LIST_PATH)
        self.wait_loading_gone()

    def add_vacancy(self, name):
        """招聘经理选当前登录用户：公共环境里别的员工随时可能被删，自己一定存在"""
        manager = self.get_text(self.USER_NAME).split()[0]
        self.open(self.VACANCY_ADD_PATH)
        self.wait_loading_gone()
        self.input_text(self.VACANCY_NAME, name)
        self.select_first_option(self.JOB_TITLE)
        self.input_autocomplete(self.HIRING_MANAGER, manager)
        self.click_save()
        self.wait_url_contains("addJobVacancy/")
        self.wait_loading_gone()

    def vacancy_exists(self, name):
        self.open_vacancies()
        return self.is_visible((By.XPATH, self.row_containing(name)), timeout=5)

    def delete_vacancy_if_exists(self, name):
        if self.vacancy_exists(name):
            self.delete_row_containing(name)
