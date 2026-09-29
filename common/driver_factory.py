# 公共工具：封装浏览器对象的创建过程
from selenium import webdriver


def get_driver():
    """创建并返回一个配置好的浏览器driver对象"""
    driver = webdriver.Edge()
    driver.maximize_window()
    return driver
