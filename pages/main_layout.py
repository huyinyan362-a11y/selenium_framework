# 登录后所有页面共用的布局：侧边菜单、顶部栏、用户下拉、列表表格
# 放在这里而不是BasePage：这些是OrangeHRM的业务元素，BasePage只放通用浏览器操作
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class MainLayout(BasePage):
    HEADER_TITLE = (By.CSS_SELECTOR, ".oxd-topbar-header-breadcrumb h6")
    MENU_SEARCH = (By.XPATH, "//aside//input[@placeholder='Search']")
    MENU_ITEMS = (By.CSS_SELECTOR, ".oxd-main-menu-item span")
    USER_DROPDOWN = (By.CSS_SELECTOR, ".oxd-userdropdown-tab")
    LOGOUT = (By.XPATH, "//a[normalize-space()='Logout']")

    # 列表页通用表格
    ROWS = (By.CSS_SELECTOR, ".oxd-table-body .oxd-table-card")
    RECORD_TEXT = (By.CSS_SELECTOR, ".orangehrm-horizontal-padding span")  # "(65) Records Found"
    CONFIRM_DELETE_BTN = (By.XPATH, "//button[normalize-space()='Yes, Delete']")

    # ---------- 菜单与顶部栏 ----------
    def go_menu(self, name):
        """点侧边菜单，比如 go_menu('PIM')"""
        self.click((By.XPATH, f"//a[contains(@class,'oxd-main-menu-item')][.//span[normalize-space()='{name}']]"))
        self.wait_loading_gone()

    def get_header_title(self):
        return self.get_text(self.HEADER_TITLE)

    def search_menu(self, keyword):
        """菜单搜索框过滤，返回过滤后剩下的菜单名"""
        self.input_text(self.MENU_SEARCH, keyword)
        return [e.text for e in self.driver.find_elements(*self.MENU_ITEMS)]

    def logout(self):
        self.click(self.USER_DROPDOWN)
        self.click(self.LOGOUT)
        self.wait_url_contains("auth/login")

    # ---------- 修改密码（右上角用户下拉进入） ----------
    CHANGE_PASSWORD = (By.XPATH, "//a[normalize-space()='Change Password']")
    NEW_PASSWORD = BasePage.field_input("Password")
    CONFIRM_PASSWORD = BasePage.field_input("Confirm Password")

    def open_change_password(self):
        self.click(self.USER_DROPDOWN)
        self.click(self.CHANGE_PASSWORD)
        self.wait_url_contains("updatePassword")

    def fill_new_password(self, password, confirm):
        """只填新密码和确认密码，不提交——共用Admin账号，真改掉别人就登不上了"""
        self.input_text(self.NEW_PASSWORD, password)
        self.input_text(self.CONFIRM_PASSWORD, confirm)
        self.blur()

    # ---------- 列表表格 ----------
    def get_record_count(self):
        """把 '(65) Records Found' 解析成 65；'No Records Found' 返回 0"""
        text = self.get_text(self.RECORD_TEXT)
        match = re.search(r"\((\d+)\)", text)
        return int(match.group(1)) if match else 0

    def get_rows(self):
        """返回表格每一行的单元格文字；没有结果返回空列表
        不用find_all：它会等元素出现，没结果时要白等到超时"""
        return [
            [cell.text for cell in row.find_elements(By.CSS_SELECTOR, ".oxd-table-cell")]
            for row in self.driver.find_elements(*self.ROWS)
        ]

    @staticmethod
    def row_containing(text, exact=True):
        """某个单元格文字等于text（exact=False时是"包含text"）的那一行"""
        cond = f"normalize-space()='{text}'" if exact else f"contains(normalize-space(),'{text}')"
        return f"//div[contains(@class,'oxd-table-card')][.//div[{cond}]]"

    def delete_row_containing(self, text, exact=True):
        """等目标行出现 → 点这一行的垃圾桶 → 确认 → 等这一行消失
        不点"第一行"：点完搜索表格可能还没刷新，第一行还是旧数据，会点到马上被替换的元素，甚至删错"""
        row = (By.XPATH, self.row_containing(text, exact))
        trash = (By.XPATH, self.row_containing(text, exact) + "//button[.//i[contains(@class,'bi-trash')]]")
        self.wait_for_element(row)
        self.click(trash)
        self.click(self.CONFIRM_DELETE_BTN)
        self.wait.until(EC.invisibility_of_element_located(row))

    CANCEL_DELETE_BTN = (By.XPATH, "//button[normalize-space()='No, Cancel']")
    DIALOG = (By.CSS_SELECTOR, ".oxd-dialog-sheet")

    def cancel_delete_row(self, text, exact=True):
        """点垃圾桶 → 确认弹窗点 No, Cancel → 等弹窗关闭"""
        row = self.row_containing(text, exact)
        self.wait_for_element((By.XPATH, row))
        self.click((By.XPATH, row + "//button[.//i[contains(@class,'bi-trash')]]"))
        self.click(self.CANCEL_DELETE_BTN)
        self.wait.until(EC.invisibility_of_element_located(self.DIALOG))

    def click_row_edit(self, text, exact=True):
        """点这一行的铅笔图标，进入编辑页"""
        row = self.row_containing(text, exact)
        self.wait_for_element((By.XPATH, row))
        self.click((By.XPATH, row + "//button[.//i[contains(@class,'bi-pencil')]]"))
