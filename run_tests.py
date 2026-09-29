# 一键运行：跑用例 → 保留历史 → 生成Allure报告
# 用法：python run_tests.py            全量
#       python run_tests.py -m p0      只跑P0（其他pytest参数同理）
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(ROOT, "reports", "allure-results")
REPORT = os.path.join(ROOT, "reports", "allure-report")

# 1. 跑用例（pytest.ini里已配置 --alluredir 和 --clean-alluredir）
code = subprocess.call([sys.executable, "-m", "pytest", *sys.argv[1:]], cwd=ROOT)

# 2. 把上一次报告的history拷进这次的结果目录——Allure趋势图全靠它
#    不拷的话每次都当成第一次运行，没有趋势
old_history = os.path.join(REPORT, "history")
if os.path.isdir(old_history):
    shutil.copytree(old_history, os.path.join(RESULTS, "history"), dirs_exist_ok=True)

# 3. 生成HTML报告
allure = shutil.which("allure")
if allure:
    subprocess.call([allure, "generate", RESULTS, "-o", REPORT, "--clean"])
    print(f"报告已生成：{os.path.join(REPORT, 'index.html')}（用 allure open reports/allure-report 打开）")
else:
    print("没找到allure命令，跳过生成报告")

sys.exit(code)
