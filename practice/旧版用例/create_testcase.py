import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

# 创建工作簿
wb = openpyxl.Workbook()

# 删除默认sheet
if 'Sheet' in wb.sheetnames:
    wb.remove(wb['Sheet'])

# ==================== 项目信息sheet ====================
ws_info = wb.create_sheet('项目信息', 0)
ws_info.column_dimensions['A'].width = 20
ws_info.column_dimensions['B'].width = 60

info_data = [
    ['项目名称', 'OrangeHRM Web自动化测试'],
    ['测试环境', 'https://opensource-demo.orangehrmlive.com/'],
    ['测试账号', 'Admin / admin123'],
    ['编写日期', '2026-09-06'],
    ['编写人', '胡艳艳'],
    ['框架技术栈', 'Python + Selenium + Pytest + POM模式'],
    ['测试范围', '登录模块、PIM员工管理模块']
]

for row_idx, (key, value) in enumerate(info_data, start=1):
    ws_info.cell(row_idx, 1, key).font = Font(bold=True)
    ws_info.cell(row_idx, 2, value)

# ==================== 登录模块用例 ====================
ws_login = wb.create_sheet('登录模块用例', 1)

# 设置列宽
ws_login.column_dimensions['A'].width = 15
ws_login.column_dimensions['B'].width = 10
ws_login.column_dimensions['C'].width = 12
ws_login.column_dimensions['D'].width = 25
ws_login.column_dimensions['E'].width = 15
ws_login.column_dimensions['F'].width = 35
ws_login.column_dimensions['G'].width = 25
ws_login.column_dimensions['H'].width = 40

# 表头
headers = ['用例ID', '优先级', '用例类型', '测试场景', '前置条件', '测试步骤', '测试数据', '预期结果']
header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
header_font = Font(bold=True, color='FFFFFF')

for col_idx, header in enumerate(headers, start=1):
    cell = ws_login.cell(1, col_idx, header)
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal='center', vertical='center')

# 登录用例数据
login_cases = [
    ['TC_Login_001', 'P0', '正常场景', '有效的用户名和密码登录', '无',
     '1. 打开登录页\n2. 输入用户名\n3. 输入密码\n4. 点击登录按钮',
     '用户名: Admin\n密码: admin123',
     '1. 登录成功\n2. 跳转到Dashboard页面\n3. URL包含"/dashboard"'],

    ['TC_Login_002', 'P1', '异常场景', '用户名正确,密码错误', '无',
     '1. 打开登录页\n2. 输入用户名\n3. 输入错误密码\n4. 点击登录按钮',
     '用户名: Admin\n密码: wrong123',
     '1. 登录失败\n2. 页面显示错误提示"Invalid credentials"\n3. 停留在登录页'],

    ['TC_Login_003', 'P1', '异常场景', '用户名错误,密码正确', '无',
     '1. 打开登录页\n2. 输入错误用户名\n3. 输入密码\n4. 点击登录按钮',
     '用户名: WrongUser\n密码: admin123',
     '1. 登录失败\n2. 页面显示错误提示"Invalid credentials"\n3. 停留在登录页'],

    ['TC_Login_004', 'P1', '异常场景', '用户名和密码都错误', '无',
     '1. 打开登录页\n2. 输入错误用户名\n3. 输入错误密码\n4. 点击登录按钮',
     '用户名: WrongUser\n密码: wrong123',
     '1. 登录失败\n2. 页面显示错误提示"Invalid credentials"\n3. 停留在登录页'],

    ['TC_Login_005', 'P2', '边界场景', '用户名为空', '无',
     '1. 打开登录页\n2. 用户名不填\n3. 输入密码\n4. 点击登录按钮',
     '用户名: (空)\n密码: admin123',
     '1. 登录失败\n2. 用户名输入框显示"Required"提示\n3. 不允许提交'],

    ['TC_Login_006', 'P2', '边界场景', '密码为空', '无',
     '1. 打开登录页\n2. 输入用户名\n3. 密码不填\n4. 点击登录按钮',
     '用户名: Admin\n密码: (空)',
     '1. 登录失败\n2. 密码输入框显示"Required"提示\n3. 不允许提交'],

    ['TC_Login_007', 'P2', '边界场景', '用户名和密码都为空', '无',
     '1. 打开登录页\n2. 用户名不填\n3. 密码不填\n4. 点击登录按钮',
     '用户名: (空)\n密码: (空)',
     '1. 登录失败\n2. 用户名和密码输入框都显示"Required"提示\n3. 不允许提交']
]

# 填充数据
thin_border = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)

for row_idx, case_data in enumerate(login_cases, start=2):
    for col_idx, value in enumerate(case_data, start=1):
        cell = ws_login.cell(row_idx, col_idx, value)
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)

        # P0用例标红
        if col_idx == 2 and value == 'P0':
            cell.font = Font(bold=True, color='FF0000')

# 设置行高
for row in range(2, len(login_cases) + 2):
    ws_login.row_dimensions[row].height = 60

# ==================== PIM模块用例 ====================
ws_pim = wb.create_sheet('PIM员工管理模块用例', 2)

# 设置列宽
ws_pim.column_dimensions['A'].width = 15
ws_pim.column_dimensions['B'].width = 10
ws_pim.column_dimensions['C'].width = 12
ws_pim.column_dimensions['D'].width = 25
ws_pim.column_dimensions['E'].width = 20
ws_pim.column_dimensions['F'].width = 40
ws_pim.column_dimensions['G'].width = 30
ws_pim.column_dimensions['H'].width = 40

# 表头
for col_idx, header in enumerate(headers, start=1):
    cell = ws_pim.cell(1, col_idx, header)
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal='center', vertical='center')

# PIM用例数据
pim_cases = [
    ['TC_PIM_001', 'P0', '正常场景', '新增员工-仅必填项', '已登录系统',
     '1. 进入PIM模块\n2. 点击"Add Employee"\n3. 输入员工姓名(First Name, Last Name)\n4. 点击Save',
     'First Name: John\nLast Name: Doe',
     '1. 新增成功\n2. 显示成功提示\n3. 员工列表中能搜索到该员工'],

    ['TC_PIM_002', 'P1', '正常场景', '新增员工-包含可选项', '已登录系统',
     '1. 进入PIM模块\n2. 点击"Add Employee"\n3. 输入姓名、Employee ID、照片\n4. 点击Save',
     'First Name: Jane\nLast Name: Smith\nEmployee ID: 12345',
     '1. 新增成功\n2. 员工详情页显示正确信息'],

    ['TC_PIM_003', 'P0', '正常场景', '搜索员工-按姓名搜索', '已登录,且系统中有员工数据',
     '1. 进入PIM模块\n2. 在搜索框输入员工姓名\n3. 点击Search',
     'Employee Name: John',
     '搜索结果中显示匹配的员工记录'],

    ['TC_PIM_004', 'P1', '正常场景', '编辑员工信息', '已登录,且已有员工记录',
     '1. 进入PIM模块\n2. 搜索并选择某员工\n3. 点击编辑按钮\n4. 修改员工信息\n5. 点击Save',
     '修改职位信息、联系方式等',
     '1. 修改成功\n2. 显示成功提示\n3. 刷新后数据已更新'],

    ['TC_PIM_005', 'P1', '正常场景', '删除员工', '已登录,且已有员工记录',
     '1. 进入PIM模块\n2. 搜索并选择某员工\n3. 勾选复选框\n4. 点击删除按钮\n5. 确认删除',
     '-',
     '1. 删除成功\n2. 员工列表中该员工不存在'],

    ['TC_PIM_006', 'P2', '边界场景', 'First Name为空', '已登录系统',
     '1. 进入PIM模块\n2. 点击"Add Employee"\n3. First Name不填,填写Last Name\n4. 点击Save',
     'First Name: (空)\nLast Name: Test',
     '显示"Required"提示,不允许保存'],

    ['TC_PIM_007', 'P2', '边界场景', 'Last Name为空', '已登录系统',
     '1. 进入PIM模块\n2. 点击"Add Employee"\n3. 填写First Name,Last Name不填\n4. 点击Save',
     'First Name: Test\nLast Name: (空)',
     '显示"Required"提示,不允许保存'],

    ['TC_PIM_008', 'P2', '异常场景', '搜索不存在的员工', '已登录系统',
     '1. 进入PIM模块\n2. 输入不存在的员工姓名\n3. 点击Search',
     'Employee Name: NotExistUser999',
     '显示"No Records Found"或搜索结果为空']
]

# 填充数据
for row_idx, case_data in enumerate(pim_cases, start=2):
    for col_idx, value in enumerate(case_data, start=1):
        cell = ws_pim.cell(row_idx, col_idx, value)
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)

        if col_idx == 2 and value == 'P0':
            cell.font = Font(bold=True, color='FF0000')

# 设置行高
for row in range(2, len(pim_cases) + 2):
    ws_pim.row_dimensions[row].height = 70

# 保存文件
wb.save('d:/测试开发/selenium_framework/OrangeHRM自动化测试用例.xlsx')
print('测试用例文档创建成功: OrangeHRM自动化测试用例.xlsx')
