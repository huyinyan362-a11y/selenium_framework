import allure
import pytest

from common.driver_factory import get_driver
from common.yaml_util import CONFIG
from common.data_factory import new_employee
from pages.login_page import LoginPage
from pages.pim_page import PIMPage


@pytest.fixture(scope="function")
def driver():
    # yield前面：前置操作——每条用例开一个新浏览器，用例之间零污染
    d = get_driver()
    yield d
    # yield后面：后置操作——用例失败也会执行，不会残留浏览器进程
    d.quit()


@pytest.fixture(scope="function")
def login(driver):
    """只负责登录，返回已登录的driver；进哪个模块由用例自己决定"""
    login_page = LoginPage(driver)
    login_page.open()
    login_page.login(CONFIG["username"], CONFIG["password"])
    return driver


@pytest.fixture
def temp_employee(login):
    """前置：在PIM新建一个测试员工；后置：删掉它。PIM、Admin、Directory的用例都会用
    fixture依赖链：temp_employee → login → driver，pytest自动按顺序执行，倒序清理"""
    pim = PIMPage(login)
    emp = new_employee()
    pim.open_list()
    pim.add_employee(emp["first"], emp["last"], emp["id"])
    pim.open_list()  # 新增后停在详情页，回到列表页作为干净的起点；其他模块的用例会自己打开页面
    yield emp
    pim.delete_employee_if_exists(emp["id"])


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """pytest钩子：每条用例的setup/call/teardown三个阶段结束后都会调用一次
    setup(fixture，比如登录)或call(用例本体)失败时截图，贴进Allure报告，用例代码一行不用改
    不截teardown：那时浏览器已经quit，截图会报错"""
    outcome = yield
    report = outcome.get_result()

    if report.when in ("setup", "call") and report.failed:
        # item.funcargs里存着这条用例用到的所有fixture；用了login也一定用了driver
        d = item.funcargs.get("driver")
        if d:
            allure.attach(
                d.get_screenshot_as_png(),
                name=f"失败截图_{item.name}",
                attachment_type=allure.attachment_type.PNG,
            )
