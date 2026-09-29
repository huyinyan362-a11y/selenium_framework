from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.username_input = (By.NAME, "username")
        self.password_input = (By.NAME, "password")
        self.login_btn = (By.CSS_SELECTOR, "button[type='submit']")
        self.error_msg = (By.CLASS_NAME, "oxd-alert-content-text")
        self.required_msg = (By.CLASS_NAME, "oxd-input-field-error-message")
        self.forgot_link = (By.CSS_SELECTOR, ".orangehrm-login-forgot-header")
        self.reset_cancel_btn = (By.XPATH, "//button[normalize-space()='Cancel']")

    def get_password_type(self):
        """密码框的type属性：password 表示密文显示"""
        return self.wait_for_element(self.password_input).get_attribute("type")

    def click_forgot_password(self):
        self.click(self.forgot_link)
        self.wait_url_contains("requestPasswordResetCode")

    def cancel_reset_password(self):
        """重置密码页点Cancel，回到登录页"""
        self.click(self.reset_cancel_btn)
        self.wait_url_contains("auth/login")

    def login(self, username, password):
        """成功登录：提交后等跳转到dashboard"""
        self.input_and_submit(username, password)
        self.wait_url_contains("dashboard")

    def input_and_submit(self, username, password):
        """只输入并提交，不等跳转（用于失败场景）"""
        self.input_text(self.username_input, username)
        self.input_text(self.password_input, password)
        self.click(self.login_btn)

    def get_error_message(self):
        """登录失败的错误提示，比如 Invalid credentials"""
        return self.get_text(self.error_msg)

    def get_required_message(self):
        """必填项提示 Required"""
        return self.get_text(self.required_msg)
