# -*- coding: utf-8 -*-
"""覆盖率与遗漏率计算：对比 AI 生成用例与人工用例对场景基线的覆盖情况"""
import os
import re
import subprocess
import sys

import yaml

# 项目根目录
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKLIST_PATH = os.path.join(ROOT, "data", "scenario_checklist.yaml")
TESTCASES_DIR = os.path.join(ROOT, "testcases")
DATA_DIR = os.path.join(ROOT, "data")


def load_checklist():
    with open(CHECKLIST_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f).get("checklist", [])


def _normalize(text):
    return str(text or "").lower()


def _match(item, text):
    return any(kw.lower() in text for kw in item.get("keywords", []))


def _case_text(case):
    return " ".join(_normalize(case.get(k, "")) for k in ("title", "precondition", "steps", "expected"))


def compute_coverage(cases):
    """计算一组用例对场景基线的覆盖率，返回覆盖率、遗漏率、覆盖项、遗漏项"""
    checklist = load_checklist()
    texts = [_case_text(c) for c in cases]
    covered = [it for it in checklist if any(_match(it, t) for t in texts)]
    missed = [it for it in checklist if it not in covered]
    total = len(checklist)
    covered_n = len(covered)
    coverage = round(covered_n / total, 4) if total else 0
    miss_rate = round(1 - coverage, 4)
    return {
        "total": total,
        "covered": covered_n,
        "coverage": coverage,
        "miss_rate": miss_rate,
        "covered_ids": [it["id"] for it in covered],
        "missed_ids": [it["id"] for it in missed],
        "missed": [{"id": it["id"], "description": it["description"]} for it in missed],
    }


def collect_manual_titles():
    """收集人工编写用例的标题（解析 testcases 下的 .py 和 data 下的 .yaml）

    注意：AI 生成的用例（ai_generated_cases.yaml）不计入人工基线，
    否则会让「人工 vs AI」的对比失真。
    """
    titles = []
    # 解析 .py 中的 @allure.title
    for root, _, files in os.walk(TESTCASES_DIR):
        for fn in files:
            if not fn.endswith(".py"):
                continue
            with open(os.path.join(root, fn), encoding="utf-8") as f:
                content = f.read()
            titles += re.findall(r'@allure\.title\("([^"]+)"\)', content)
    # 解析 data 下 YAML 的 title（排除场景基线文件和 AI 生成用例）
    excluded = {"scenario_checklist.yaml", "ai_generated_cases.yaml"}
    for fn in os.listdir(DATA_DIR):
        if fn.endswith((".yaml", ".yml")) and fn not in excluded:
            try:
                with open(os.path.join(DATA_DIR, fn), encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                for k, v in (data or {}).items():
                    if isinstance(v, list):
                        for c in v:
                            if isinstance(c, dict) and "title" in c:
                                titles.append(c["title"])
            except Exception:
                pass
    return titles


def count_pytest_cases():
    """用 pytest 收集器统计真实用例数（避免人工基线与参数化数据重复计数）"""
    try:
        out = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            cwd=ROOT, capture_output=True, text=True, timeout=60,
        )
        m = re.search(r"(\d+) tests? collected", out.stdout)
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return None


def manual_coverage():
    """以项目中人工编写的用例（testcases + 人工维护的 data）作为人工基线计算覆盖率"""
    titles = collect_manual_titles()
    text = " ".join(_normalize(t) for t in titles)
    checklist = load_checklist()
    covered = [it for it in checklist if _match(it, text)]
    total = len(checklist)
    covered_n = len(covered)
    coverage = round(covered_n / total, 4) if total else 0
    return {
        "case_count": count_pytest_cases() or len(titles),
        "total": total,
        "covered": covered_n,
        "coverage": coverage,
        "miss_rate": round(1 - coverage, 4),
    }
