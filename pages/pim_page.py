from selenium.webdriver.common.by import By

from pages.main_layout import MainLayout


class PIMPage(MainLayout):
    LIST_PATH = "/web/index.php/pim/viewEmployeeList"

    # ---------- 员工列表页：搜索区 ----------
    ADD_BTN = (By.XPATH, "//button[normalize-space()='Add']")
    NAME_INPUT = (By.XPATH, "(//input[@placeholder='Type for hints...'])[1]")
    ID_INPUT = MainLayout.field_input("Employee Id")
    SEARCH_BTN = (By.XPATH, "//button[@type='submit']")
    RESET_BTN = (By.XPATH, "//button[@type='reset']")

    # ---------- 新增员工页 ----------
    FIRST_NAME = (By.NAME, "firstName")
    LAST_NAME = (By.NAME, "lastName")
    FORM_ID_INPUT = ID_INPUT  # 新增页的Employee Id和列表页是同一种label结构，定位共用
    SAVE_BTN = (By.XPATH, "//button[@type='submit']")
    FIELD_ERROR = (By.CSS_SELECTOR, ".oxd-input-field-error-message")

    # ================= 列表页操作 =================
    def open_list(self):
        self.open(self.LIST_PATH)
        self.wait_loading_gone()

    def click_add(self):
        self.click(self.ADD_BTN)
        self.wait_url_contains("addEmployee")

    def click_search(self):
        """点搜索后等表格刷新完，调用方直接读结果，不用自己等"""
        self.click(self.SEARCH_BTN)
        self.wait_loading_gone()

    def click_reset(self):
        self.click(self.RESET_BTN)
        self.wait_loading_gone()

    def input_name(self, name):
        self.input_autocomplete(self.NAME_INPUT, name)

    def input_id(self, emp_id):
        self.input_text(self.ID_INPUT, emp_id)

    def search(self, name=None, emp_id=None):
        """组合搜索：传了哪个条件就填哪个，判定表用例用它"""
        if name:
            self.input_name(name)
        if emp_id:
            self.input_id(emp_id)
        self.click_search()

    def search_by_id(self, emp_id):
        self.search(emp_id=emp_id)

    def search_by_name(self, name):
        self.search(name=name)

    def get_employee_id_value(self):
        return self.get_value(self.ID_INPUT)

    def delete_employee_by_id(self, emp_id):
        """按ID搜索后删除ID等于emp_id的那一行"""
        self.search_by_id(emp_id)
        self.delete_row_containing(emp_id)

    def delete_employee_if_exists(self, emp_id):
        """清理用：搜到就删，搜不到什么都不做（用例本身已经删掉的情况）"""
        self.open_list()
        self.search_by_id(emp_id)
        if self.get_record_count() > 0:
            self.delete_row_containing(emp_id)

    # ================= 新增页操作 =================
    def fill_employee_form(self, first_name, last_name, emp_id=None):
        """只填表单不提交，校验类用例（必填、重复ID）用它"""
        self.input_text(self.FIRST_NAME, first_name)
        self.input_text(self.LAST_NAME, last_name)
        if emp_id:
            # 系统会自动生成一个Employee Id，input_text会先全选删除再输入
            self.input_text(self.FORM_ID_INPUT, emp_id)

    def click_save(self):
        self.click(self.SAVE_BTN)

    def add_employee(self, first_name, last_name, emp_id):
        """完整新增流程：保存成功后会跳转到员工详情页"""
        self.click_add()
        self.fill_employee_form(first_name, last_name, emp_id)
        self.click_save()
        self.wait_url_contains("viewPersonalDetails")

    def get_field_error(self):
        """表单字段下方的红字提示，比如 Required / Employee Id already exists"""
        return self.get_text(self.FIELD_ERROR)

    def add_employee_required_only(self, first_name, last_name):
        """只填必填项新增，Employee Id用系统自动生成的；返回这个ID，用例结束按它清理"""
        self.click_add()
        self.input_text(self.FIRST_NAME, first_name)
        self.input_text(self.LAST_NAME, last_name)
        # 自动生成的ID是异步填进去的，等它有值再读
        self.wait.until(lambda d: self.get_value(self.FORM_ID_INPUT))
        emp_id = self.get_value(self.FORM_ID_INPUT)
        self.click_save()
        self.wait_url_contains("viewPersonalDetails")
        return emp_id

    # ---------- 头像上传 ----------
    PHOTO_INPUT = (By.CSS_SELECTOR, "input[type='file']")
    FORM_IMAGES = (By.XPATH, "//form//img")

    def choose_photo(self, file_path):
        """<input type=file>是隐藏的，不能点，直接send_keys文件路径"""
        self.driver.find_element(*self.PHOTO_INPUT).send_keys(file_path)

    def photo_previewed(self):
        """选完文件后预览图的src会变成 data:image 开头的base64"""
        self.wait.until(lambda d: any(
            (img.get_attribute("src") or "").startswith("data:image")
            for img in d.find_elements(*self.FORM_IMAGES)))
        return True

    # ---------- 编辑员工 ----------
    DETAIL_SAVE_BTN = (By.XPATH, "(//button[@type='submit'])[1]")  # 详情页第一个Save属于Personal Details

    def open_employee(self, emp_id):
        """按ID搜到后点这一行，进入员工详情页"""
        self.search_by_id(emp_id)
        self.click((By.XPATH, self.row_containing(emp_id)))
        self.wait_url_contains("viewPersonalDetails")
        self.wait_loading_gone()
        # 详情数据是异步加载的：名字还没回填就输入，会被回填的旧值覆盖
        self.wait.until(lambda d: self.get_value(self.FIRST_NAME))

    def update_first_name(self, new_name):
        """改名字并保存，返回提示文字"""
        self.input_text(self.FIRST_NAME, new_name)
        self.click(self.DETAIL_SAVE_BTN)
        return self.get_toast_text()
