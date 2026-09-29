# PO模式：注册页封装（改造版，继承BasePage，用它提供的通用方法）
from selenium.webdriver.common.by import By
from pages.base_page import BasePage


# TODO 1: 把class后面的括号里加上BasePage，表示RegisterPage继承BasePage
class RegisterPage(BasePage):
    def __init__(self, driver):
        # TODO 2: 调用父类的构造方法super().__init__(driver)，而不是自己写self.driver = driver
        super().__init__(driver)

        # 定位表达式不用变，还是集中写在这里
        self.username_input = (By.ID, "username")
        self.password_input = (By.ID, "password")
        self.confirm_password_input = (By.ID, "confirmPassword")
        self.captcha_text = (By.ID, "captchaText")
        self.captcha_input = (By.ID, "captchaInput")
        self.submit_btn = (By.ID, "submitBtn")
        self.result_msg = (By.ID, "resultMsg")

    def input_username(self, username):
        # TODO 3: 改成调用父类的方法：self.input_text(self.username_input, username)
        self.input_text(self.username_input,username)        

    def input_password(self, password):
        # TODO 4: 改成调用self.input_text(...)
        self.input_text(self.password_input,password)

    def input_confirm_password(self, confirm_password):
        # TODO 5: 改成调用self.input_text(...)
        self.input_text(self.confirm_password_input,confirm_password)

    def input_captcha(self):
        # TODO 6: 改成调用self.get_text(self.captcha_text)读取验证码文字
        # 再调用self.input_text(self.captcha_input, 验证码文字)输入
        captcha = self.get_text(self.captcha_text)
        self.input_text(self.captcha_input,captcha)
    def click_submit(self):
        # TODO 7: 改成调用self.click(self.submit_btn)
        self.click(self.submit_btn)
    def get_result_message(self):
        # TODO 8: 改成调用self.get_text(self.result_msg)
        return self.get_text(self.result_msg)

    def register(self, username, password, confirm_password):
        self.input_username(username)
        self.input_password(password)
        self.input_confirm_password(confirm_password)
        self.input_captcha()
        self.click_submit()
