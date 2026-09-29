from selenium.webdriver.common.by import By

from pages.main_layout import MainLayout


class LeavePage(MainLayout):
    LIST_PATH = "/web/index.php/leave/viewLeaveList"

    FROM_DATE = MainLayout.field_input("From Date")
    TO_DATE = MainLayout.field_input("To Date")
    STATUS_CHIPS = (By.CSS_SELECTOR, ".oxd-multiselect-chips-area .oxd-chip")
    FILTER_HEADER = (By.CSS_SELECTOR, ".oxd-table-filter-header")  # 点这里让日期框失焦，触发校验并关掉日历弹层

    def open_list(self):
        self.open(self.LIST_PATH)
        self.wait_loading_gone()

    def get_dates(self):
        return self.get_value(self.FROM_DATE), self.get_value(self.TO_DATE)

    def get_status_chips(self):
        return [e.text for e in self.find_all(self.STATUS_CHIPS)]

    def set_dates(self, from_date, to_date):
        """填日期后点空白处失焦：日期校验是失焦时触发的，不失焦读不到错误提示"""
        self.input_text(self.FROM_DATE, from_date)
        self.click(self.FILTER_HEADER)
        self.input_text(self.TO_DATE, to_date)
        self.click(self.FILTER_HEADER)

    # ---------- 请假列表：按员工+状态搜索 ----------
    EMPLOYEE = (By.XPATH, "//input[@placeholder='Type for hints...']")
    STATUS_SELECT = MainLayout.field_dropdown("Show Leave with Status")
    SEARCH_BTN = (By.XPATH, "//button[@type='submit']")
    COL_EMPLOYEE = 2  # ['', Date, Employee Name, Leave Type, ...]

    def search_leave(self, employee, extra_status=None):
        """默认只看Pending Approval；管理员直接分配的请假状态是Scheduled，要额外勾上"""
        if extra_status:
            self.select_dropdown(self.STATUS_SELECT, extra_status)
        self.input_autocomplete(self.EMPLOYEE, employee)
        self.click(self.SEARCH_BTN)
        self.wait_loading_gone()

    # ---------- 假期额度（Entitlements → Add） ----------
    ENTITLEMENT_PATH = "/web/index.php/leave/addLeaveEntitlement"
    LEAVE_TYPE = MainLayout.field_dropdown("Leave Type")
    ENTITLEMENT = MainLayout.field_input("Entitlement")
    SUBMIT_BTN = (By.XPATH, "//button[@type='submit']")
    CONFIRM_BTN = (By.XPATH, "//div[contains(@class,'oxd-dialog-sheet')]//button[normalize-space()='Confirm']")
    LEAVE_TYPE_NAME = "CAN - Personal"  # 预置假期类型

    def open_add_entitlement(self):
        self.open(self.ENTITLEMENT_PATH)
        self.wait_loading_gone()
        self.wait_for_element(self.ENTITLEMENT)

    def input_entitlement(self, value):
        self.input_text(self.ENTITLEMENT, value)
        self.blur()

    def add_entitlement(self, employee, days):
        """选员工、假期类型，填额度 → Save → 确认弹窗点Confirm → 跳到额度列表"""
        self.open_add_entitlement()
        self.input_autocomplete(self.EMPLOYEE, employee)
        self.select_dropdown(self.LEAVE_TYPE, self.LEAVE_TYPE_NAME)
        self.input_entitlement(days)
        self.click(self.SUBMIT_BTN)
        if self.is_visible(self.CONFIRM_BTN, timeout=5):
            self.click(self.CONFIRM_BTN, wait_loading=False)
        self.wait_url_contains("viewLeaveEntitlements")
        self.wait_loading_gone()

    # ---------- 分配请假（Assign Leave） ----------
    ASSIGN_PATH = "/web/index.php/leave/assignLeave"
    DIALOG = (By.CSS_SELECTOR, ".oxd-dialog-sheet")
    DIALOG_CANCEL = (By.XPATH, "//div[contains(@class,'oxd-dialog-sheet')]//button[normalize-space()='Cancel']")

    def open_assign(self):
        self.open(self.ASSIGN_PATH)
        self.wait_loading_gone()
        self.wait_for_element(self.EMPLOYEE)

    def fill_assign(self, employee, date):
        """选员工、假期类型、From Date（To Date会自动带出同一天）"""
        self.input_autocomplete(self.EMPLOYEE, employee)
        self.select_dropdown(self.LEAVE_TYPE, self.LEAVE_TYPE_NAME)
        self.input_text(self.FROM_DATE, date)
        self.blur()

    def click_assign(self):
        self.click(self.SUBMIT_BTN)

    def get_dialog_text(self):
        return self.get_text(self.DIALOG)

    def close_dialog(self):
        self.click(self.DIALOG_CANCEL, wait_loading=False)

    # ---------- 假期类型（Configure → Leave Types） ----------
    TYPES_PATH = "/web/index.php/leave/leaveTypeList"

    def get_leave_type_names(self):
        self.open(self.TYPES_PATH)
        self.wait_loading_gone()
        self.wait_for_element(self.ROWS)
        return [row[1] for row in self.get_rows()]
