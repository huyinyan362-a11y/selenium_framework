# 从 testcase_data.py 生成《OrangeHRM自动化测试用例.xlsx》和《测试用例文档.md》
# 两份文档同一个数据源，改用例只改 testcase_data.py，再运行本脚本
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from testcase_data import MODULES

INFO = [
    ("项目名称", "OrangeHRM Web自动化测试"),
    ("测试环境", "https://opensource-demo.orangehrmlive.com/"),
    ("测试账号", "Admin / admin123"),
    ("编写人", "胡艳艳"),
    ("更新日期", "2026-09-28"),
    ("框架技术栈", "Python + Selenium + Pytest + POM + YAML数据驱动 + Allure"),
    ("优先级标准", "P0：坏了系统没法用；P1：影响使用但有替代路径；P2：边界、校验与体验"),
    ("设计方法", "等价类划分、边界值分析、场景法、判定表、错误推测"),
]
HEADERS = ["用例ID", "优先级", "用例类型", "设计方法", "测试场景", "前置条件",
           "测试步骤", "测试数据", "预期结果", "自动化状态", "备注"]
WIDTHS = [16, 8, 10, 10, 30, 16, 36, 22, 36, 11, 30]
KEYS = ["id", "priority", "type", "method", "title", "pre", "steps", "data", "expected", "status", "note"]
PRI_ORDER = {"P0": 0, "P1": 1, "P2": 2}


def code_text():
    """testcases/ 和 data/ 下所有代码和YAML的内容，用来检查用例ID是否已经写进代码"""
    import glob
    texts = []
    for pattern in ("testcases/*.py", "data/*.yaml"):
        for path in glob.glob(pattern):
            with open(path, encoding="utf-8") as f:
                texts.append(f.read())
    return "\n".join(texts)


def numbered_modules():
    """每个模块内按P0→P1→P2排序后编号：TC_PIM_001
    自动化状态不手填：用例ID出现在代码里就是"已实现"，文档和代码永远对得上"""
    code = code_text()
    result = []
    for mod, name, file, cases in MODULES:
        ordered = sorted(cases, key=lambda c: PRI_ORDER[c["priority"]])
        for i, case in enumerate(ordered, start=1):
            case["id"] = f"TC_{mod}_{i:03d}"
            case["status"] = "已实现" if case["id"] in code else "待实现"
        result.append((mod, name, file, ordered))
    return result


def summary_rows(modules):
    rows = []
    for code, name, file, cases in modules:
        count = lambda k, v: sum(1 for c in cases if c[k] == v)
        rows.append([name, len(cases), count("priority", "P0"), count("priority", "P1"),
                     count("priority", "P2"), count("status", "已实现"), count("status", "待实现"), file])
    total = ["合计"] + [sum(r[i] for r in rows) for i in range(1, 7)] + [""]
    return rows, total


# ==================== Excel ====================
THIN = Side(style="thin", color="999999")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HEAD_FILL = PatternFill("solid", fgColor="4472C4")
PRI_FILL = {"P0": "F8CBAD", "P1": "FFE699", "P2": "E2EFDA"}


def write_header(ws, headers, widths):
    for col, (h, w) in enumerate(zip(headers, widths), start=1):
        cell = ws.cell(1, col, h)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = HEAD_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = BORDER
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = w
    ws.freeze_panes = "A2"


def build_excel(modules, path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "项目信息"
    ws.column_dimensions["A"].width = 14
    ws.column_dimensions["B"].width = 80
    for r, (k, v) in enumerate(INFO, start=1):
        ws.cell(r, 1, k).font = Font(bold=True)
        ws.cell(r, 2, v)

    ws = wb.create_sheet("用例汇总")
    heads = ["模块", "用例数", "P0", "P1", "P2", "已实现", "待实现", "代码文件"]
    write_header(ws, heads, [18, 9, 7, 7, 7, 9, 9, 22])
    rows, total = summary_rows(modules)
    for r, row in enumerate(rows + [total], start=2):
        for c, v in enumerate(row, start=1):
            cell = ws.cell(r, c, v)
            cell.border = BORDER
            cell.font = Font(bold=(row is total))

    for code, name, file, cases in modules:
        ws = wb.create_sheet(name[:31])
        write_header(ws, HEADERS, WIDTHS)
        for r, case in enumerate(cases, start=2):
            for c, key in enumerate(KEYS, start=1):
                cell = ws.cell(r, c, case[key])
                cell.alignment = Alignment(wrap_text=True, vertical="top")
                cell.border = BORDER
            ws.cell(r, 2).fill = PatternFill("solid", fgColor=PRI_FILL[case["priority"]])
            if case["status"] == "待实现":
                ws.cell(r, 10).font = Font(color="C00000")
    wb.save(path)


# ==================== Markdown ====================
def md_cell(text):
    return str(text).replace("|", "\\|").replace("\n", "<br>")


def build_markdown(modules, path):
    lines = ["# OrangeHRM 自动化测试用例文档", "", "## 项目信息", ""]
    lines += [f"- **{k}**：{v}" for k, v in INFO]
    rows, total = summary_rows(modules)
    lines += ["", "## 用例汇总", "", "| 模块 | 用例数 | P0 | P1 | P2 | 已实现 | 待实现 | 代码文件 |",
              "|---|---|---|---|---|---|---|---|"]
    for row in rows + [total]:
        lines.append("| " + " | ".join(md_cell(v) for v in row) + " |")
    for idx, (code, name, file, cases) in enumerate(modules, start=1):
        lines += ["", f"## {idx}. {name}（{len(cases)}条，代码：testcases/{file}）", "",
                  "| " + " | ".join(HEADERS) + " |", "|" + "---|" * len(HEADERS)]
        for case in cases:
            lines.append("| " + " | ".join(md_cell(case[k]) for k in KEYS) + " |")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    mods = numbered_modules()
    build_excel(mods, "OrangeHRM自动化测试用例.xlsx")
    build_markdown(mods, "测试用例文档.md")
    rows, total = summary_rows(mods)
    print(f"已生成：共{total[1]}条  P0={total[2]} P1={total[3]} P2={total[4]}  已实现={total[5]} 待实现={total[6]}")
