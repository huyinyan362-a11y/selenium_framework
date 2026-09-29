# Base层：所有页面类都会用到的通用浏览器操作
# 原则：这里不出现任何业务元素的定位符，只放"怎么操作"，不放"操作谁"
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from common.yaml_util import CONFIG


class BasePage:
    # OrangeHRM通用的loading遮罩（表单提交、表格刷新时出现）
    LOADING = (By.CSS_SELECTOR, ".oxd-form-loader, .oxd-loading-spinner")
    # 右下角成功/失败提示
    TOAST = (By.CSS_SELECTOR, ".oxd-toast")
    # 表单字段下方的红字提示
    FIELD_ERRORS = (By.CSS_SELECTOR, ".oxd-input-field-error-message")

    def __init__(self, driver):
        self.driver = driver
        self.timeout = CONFIG["timeout"]
        self.wait = WebDriverWait(driver, self.timeout)

    # ---------- 查找 ----------
    def wait_for_element(self, locator, timeout=None):
        """等元素可见再返回（不是只等存在于DOM）"""
        return WebDriverWait(self.driver, timeout or self.timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def find_all(self, locator):
        """返回所有匹配的元素（列表），用于表格行、下拉选项"""
        self.wait_for_element(locator)
        return self.driver.find_elements(*locator)

    # ---------- 操作：等待都封在操作内部，调用方只写一句 ----------
    def click(self, locator, wait_loading=True):
        """先等loading遮罩消失，再等元素可点击（存在+可见+enabled）后点击
        element_to_be_clickable只看元素自己的状态，不知道有遮罩盖在上面，所以遮罩要单独等
        wait_loading=False：点弹窗里的按钮时用。弹窗打开期间背后的表单loading一直在，
        要等你点了Confirm才消失，这时还等loading消失就会互相卡死"""
        if wait_loading:
            self.wait.until(EC.invisibility_of_element_located(self.LOADING))
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def input_text(self, locator, text):
        """清空后输入。OrangeHRM是Vue页面，clear()有时清不掉，所以用Ctrl+A再删"""
        element = self.wait_for_element(locator)
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.DELETE)
        element.send_keys(text)

    def js_click(self, locator):
        """JS点击兜底：元素被遮挡时用。代价是绕过真实用户行为，可能掩盖真bug，只在确认是框架问题时用"""
        element = self.wait_for_element(locator)
        self.driver.execute_script("arguments[0].click();", element)

    def select_dropdown(self, dropdown_locator, option_text):
        """OrangeHRM的下拉框是div做的，不是<select>，Selenium自带的Select类用不了
        做法：先点开下拉框，再点文本匹配的选项"""
        self.click(dropdown_locator)
        option = (By.XPATH, f"//div[@role='listbox']//span[normalize-space()='{option_text}']")
        self.click(option)

    def input_autocomplete(self, locator, text):
        """自动补全输入框（Type for hints...）：只输入不选提示，提交会报Invalid
        输入后等下拉里出现包含text的选项再点。刚输入时选项是"Searching...."，不含text，所以会自动等到真结果"""
        self.input_text(locator, text)
        option = (By.XPATH, f"//div[@role='listbox']//span[contains(normalize-space(),'{text}')]")
        self.click(option)

    def get_autocomplete_hints(self, locator, text):
        """输入后返回下拉提示的文字列表，等"Searching...."结束再读
        用于断言"搜不到"：不存在的名字，提示是 ['No Records Found']"""
        self.input_text(locator, text)
        listbox = (By.CSS_SELECTOR, "div[role='listbox']")
        self.wait_for_element(listbox)
        self.wait.until(lambda d: "Searching" not in d.find_element(*listbox).text)
        return [line for line in self.driver.find_element(*listbox).text.split("\n") if line]

    def select_first_option(self, dropdown_locator):
        """下拉框选第一个真实选项（跳过"-- Select --"），用于选项内容会变的公共环境"""
        self.click(dropdown_locator)
        option = (By.XPATH, "(//div[@role='listbox']//div[@role='option'][not(contains(.,'Select'))])[1]")
        self.click(option)

    def get_dropdown_text(self, dropdown_locator):
        """下拉框当前显示的选项文字"""
        return self.wait_for_element(dropdown_locator).text.strip()

    def blur(self):
        """让当前输入框失焦：很多字段校验是失焦时才触发的，不失焦读不到错误提示"""
        self.driver.switch_to.active_element.send_keys(Keys.TAB)

    # ---------- 组件库通用定位：OrangeHRM所有表单都是 label + 输入控件 放在同一个input-group里 ----------
    @staticmethod
    def field_input(label):
        """按label文字找它下面的输入框，比如 field_input('Username')"""
        return (By.XPATH, f"//label[normalize-space()='{label}']/ancestor::div[contains(@class,'oxd-input-group')]//input")

    @staticmethod
    def field_dropdown(label):
        """按label文字找它下面的下拉框"""
        return (By.XPATH, f"//label[normalize-space()='{label}']/ancestor::div[contains(@class,'oxd-input-group')]//div[contains(@class,'oxd-select-text')]")

    def get_field_errors(self, timeout=3):
        """当前页面所有字段下方的红字提示，返回列表
        先最多等timeout秒让提示出现：点完保存立刻读可能还没渲染出来。
        断言"没有错误"时也需要这个等待，否则还没来得及出现就判定"没有"，是假通过"""
        self.is_visible(self.FIELD_ERRORS, timeout)
        return [e.text for e in self.driver.find_elements(*self.FIELD_ERRORS)]

    def wait_field_errors(self, condition, timeout=8):
        """异步校验（要调接口的，比如用户名是否重复）结果出来得晚，中间会先显示上一步的旧提示
        轮询到 condition(提示列表) 为True 或超时，返回最后一次读到的提示列表（不抛异常，交给断言判断）"""
        errors = []
        end = time.time() + timeout
        while time.time() < end:
            errors = [e.text for e in self.driver.find_elements(*self.FIELD_ERRORS)]
            if condition(errors):
                break
            time.sleep(0.3)
        return errors

    # ---------- 读取 ----------
    def get_text(self, locator):
        return self.wait_for_element(locator).text

    def get_value(self, locator):
        """输入框的内容在value属性里，不在.text里"""
        return self.wait_for_element(locator).get_attribute("value")

    def is_visible(self, locator, timeout=3):
        """判断元素是否可见，不抛异常，返回True/False"""
        try:
            self.wait_for_element(locator, timeout)
            return True
        except TimeoutException:
            return False

    # ---------- 等页面状态 ----------
    def wait_loading_gone(self, appear_timeout=2):
        """等loading遮罩消失——隐式等待做不到"等消失"，必须用显式等待
        先短暂等它出现：点完按钮的瞬间loading可能还没冒出来，直接判断"消失"会立刻通过，读到旧数据
        等不到出现说明请求很快已经结束，这是正常情况，不算失败"""
        try:
            WebDriverWait(self.driver, appear_timeout).until(
                EC.visibility_of_element_located(self.LOADING)
            )
        except TimeoutException:
            pass
        self.wait.until(EC.invisibility_of_element_located(self.LOADING))

    def wait_url_contains(self, text):
        self.wait.until(EC.url_contains(text))

    def get_toast_text(self):
        """读提示文字，用于断言"保存成功"之类"""
        return self.get_text(self.TOAST)

    def open(self, path=""):
        """打开 base_url + path，页面里只写相对路径，换环境不用改页面类"""
        self.driver.get(CONFIG["base_url"] + path)
