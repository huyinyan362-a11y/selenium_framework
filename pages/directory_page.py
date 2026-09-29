from selenium.webdriver.common.by import By

from pages.main_layout import MainLayout


class DirectoryPage(MainLayout):
    PATH = "/web/index.php/directory/viewDirectory"

    NAME_INPUT = (By.XPATH, "//input[@placeholder='Type for hints...']")
    SEARCH_BTN = (By.XPATH, "//button[@type='submit']")
    RESET_BTN = (By.XPATH, "//button[@type='reset']")
    CARD_NAMES = (By.CSS_SELECTOR, ".orangehrm-directory-card-header")

    def open_directory(self):
        """等第一张卡片出现：卡片是异步加载的，只等loading容易读到还没加载的空页面"""
        self.open(self.PATH)
        self.wait_loading_gone()
        self.wait_for_element(self.CARD_NAMES)

    def search_by_name(self, name):
        self.input_autocomplete(self.NAME_INPUT, name)
        self.click(self.SEARCH_BTN)
        self.wait_loading_gone()

    def click_reset(self):
        self.click(self.RESET_BTN)
        self.wait_loading_gone()

    def get_card_names(self):
        """通讯录是卡片不是表格；没有卡片时返回空列表"""
        return [e.text.strip() for e in self.driver.find_elements(*self.CARD_NAMES)]

    def get_name_value(self):
        return self.get_value(self.NAME_INPUT)

    # ---------- 卡片详情 ----------
    CARDS = (By.CSS_SELECTOR, ".orangehrm-directory-card")
    SIDEBAR = (By.CSS_SELECTOR, ".orangehrm-corporate-directory-sidebar")

    def open_first_card(self):
        """点第一张卡片，右侧弹出这个员工的详情；返回卡片上的名字"""
        name = self.get_card_names()[0]
        self.click((By.XPATH, "(//div[contains(@class,'orangehrm-directory-card')])[1]"))
        self.wait_for_element(self.SIDEBAR)
        return name

    def get_sidebar_text(self):
        return self.get_text(self.SIDEBAR)
