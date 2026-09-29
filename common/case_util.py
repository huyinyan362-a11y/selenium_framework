# 参数化工具：让同一个测试方法里的每条数据带上自己的用例ID和优先级
import pytest


def params(cases):
    """把YAML/列表里的用例转成pytest.param：
    - ids 显示成 "TC_LOGIN_002 密码错误"，报告里一眼看出是哪条用例
    - 每条数据单独打优先级标记，pytest -m p0 才能只挑出P0那几条
    每条用例需要有 tc、case_name、priority 三个字段"""
    return [
        pytest.param(case, id=f"{case['tc']} {case['case_name']}",
                     marks=getattr(pytest.mark, case["priority"].lower()))
        for case in cases
    ]
