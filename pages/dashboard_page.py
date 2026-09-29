from selenium.webdriver.common.by import By

from pages.main_layout import MainLayout


class DashboardPage(MainLayout):
    PATH = "/web/index.php/dashboard/index"
    WIDGET_NAMES = (By.CSS_SELECTOR, ".orangehrm-dashboard-widget-name p")

    def open_dashboard(self):
        self.open(self.PATH)
        self.wait_loading_gone()

    def get_widget_names(self):
        return [e.text for e in self.find_all(self.WIDGET_NAMES)]
