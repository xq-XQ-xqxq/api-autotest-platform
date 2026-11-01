# -*- coding: utf-8 -*-
"""一键执行：跑 pytest 并生成 Allure 报告
用法:
    python run.py          # 执行测试并生成报告
    python run.py --open   # 执行后在浏览器打开报告
"""
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.abspath(__file__))
RESULT_DIR = os.path.join(ROOT, "reports", "allure-results")
REPORT_DIR = os.path.join(ROOT, "reports", "allure-report")


def main():
    code = pytest.main(["--alluredir", RESULT_DIR, "--clean-alluredir"])
    try:
        subprocess.run(["allure", "generate", RESULT_DIR, "-o", REPORT_DIR, "--clean"],
                       check=True, shell=True)
        print(f"\nAllure 报告已生成: {REPORT_DIR}")
        if "--open" in sys.argv:
            subprocess.run(["allure", "open", REPORT_DIR], shell=True)
    except FileNotFoundError:
        print("\n[提示] 未检测到 allure 命令行工具，仅生成原始结果数据。"
              "\n       安装方式: scoop install allure  或  https://allurereport.org/docs/install/")
    return code


if __name__ == "__main__":
    sys.exit(main())
