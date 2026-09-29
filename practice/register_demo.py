# 测试脚本：调用PO类，不直接写定位表达式
import time
import os
import sys

# 让Python能找到common和pages这两个文件夹里的模块（都在项目根目录下）
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.driver_factory import get_driver
from pages.register_page import RegisterPage

# resources文件夹跟testcases是平级的，都在项目根目录下
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_PATH = os.path.join(PROJECT_ROOT, "resources", "register_page.html")
URL = "file:///" + HTML_PATH.replace("\\", "/")

driver = get_driver()

try:
    driver.get(URL)
    time.sleep(1)

    register_page = RegisterPage(driver)
    register_page.register(username="hu", password="1234", confirm_password="1234")

    time.sleep(1)
    result = register_page.get_result_message()
    print("注册结果：", result)
    assert result == "注册成功", f"注册失败：{result}"

finally:
    time.sleep(2)
    driver.quit()
