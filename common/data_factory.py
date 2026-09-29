# 测试数据生成：演示站是公共环境，别人也在改数据，写死的数据会冲突
# 用时间戳保证每次运行、每个用例都不一样（并行跑时也不会互相干扰）
import time


def unique_suffix():
    """8位数字，取纳秒时间戳后8位"""
    return str(time.time_ns())[-8:]


def new_employee():
    """员工：ID最多10位，这里用8位"""
    s = unique_suffix()
    return {"first": "Auto", "last": f"T{s}", "id": s}


def new_candidate():
    s = unique_suffix()
    return {"first": "Cand", "last": f"C{s}", "email": f"cand{s}@test.com"}


def new_system_user():
    """系统用户：用户名至少5位，密码要求 >=7位且含数字和字母"""
    s = unique_suffix()
    return {"username": f"auto_{s}", "password": f"Pwd{s}a"}
