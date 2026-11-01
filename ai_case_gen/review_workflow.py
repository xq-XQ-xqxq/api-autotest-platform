# -*- coding: utf-8 -*-
"""人工审核入库：逐条确认 AI 用例草稿，支持接受/拒绝/编辑/新增，通过的写入 data/ 目录"""
import os

import yaml


def _ask(field, current):
    val = input(f"  {field}（留空保持「{current}」）: ").strip()
    return val or current


def edit_case(case):
    """编辑当前用例的关键字段"""
    print("  -- 编辑用例（留空表示保持原值）--")
    case["title"] = _ask("title", case.get("title", ""))
    case["priority"] = _ask("priority", case.get("priority", "P1"))
    case["precondition"] = _ask("precondition", case.get("precondition", ""))
    case["steps"] = _ask("steps", case.get("steps", ""))
    case["expected"] = _ask("expected", case.get("expected", ""))
    return case


def add_case():
    """人工新增一条用例"""
    print("  -- 新增用例 --")
    return {
        "title": _ask("title", ""),
        "priority": _ask("priority", "P1"),
        "precondition": _ask("precondition", ""),
        "steps": _ask("steps", ""),
        "expected": _ask("expected", ""),
    }


def review_cases(cases: list):
    """命令行交互式审核：y 接受 / n 拒绝 / e 编辑 / a 新增一条 / s 跳过剩余

    返回 (采纳用例列表, 审核统计)
    """
    accepted = []
    accepted_from_draft = 0
    added = 0
    rejected = 0
    skipped_rest = 0

    for i, case in enumerate(cases, 1):
        while True:
            print(f"\n[{i}/{len(cases)}] {case.get('title')}  (优先级: {case.get('priority')})")
            print(f"  前置条件: {case.get('precondition')}")
            print(f"  测试步骤: {case.get('steps')}")
            print(f"  预期结果: {case.get('expected')}")
            choice = input("  操作? [y接受/n拒绝/e编辑/a新增一条/s跳过剩余]: ").strip().lower()
            if choice == "y":
                accepted.append(case)
                accepted_from_draft += 1
                break
            elif choice == "n":
                rejected += 1
                break
            elif choice == "s":
                skipped_rest = len(cases) - i
                return accepted, _stats(len(cases), accepted_from_draft, added, rejected, skipped_rest)
            elif choice == "e":
                case = edit_case(case)
            elif choice == "a":
                accepted.append(add_case())
                added += 1

    # 全部审完后可继续追加人工补充的用例
    while input("\n是否再新增用例? [y/n]: ").strip().lower() == "y":
        accepted.append(add_case())
        added += 1

    return accepted, _stats(len(cases), accepted_from_draft, added, rejected, skipped_rest)


def _stats(draft_count, accepted_from_draft, added, rejected, skipped_rest):
    return {
        "draft_count": draft_count,
        "accepted_from_draft": accepted_from_draft,
        "added": added,
        "rejected": rejected,
        "skipped_rest": skipped_rest,
    }


def save_cases(cases: list, out_file: str):
    """审核通过的用例写入 YAML 入库"""
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        yaml.safe_dump({"cases": cases}, f, allow_unicode=True, sort_keys=False)
    print(f"\n已入库 {len(cases)} 条用例 -> {out_file}")
