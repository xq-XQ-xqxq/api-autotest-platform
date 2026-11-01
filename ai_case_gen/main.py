# -*- coding: utf-8 -*-
"""AI 用例生成 + 人工审核入库 主流程

用法（在项目根目录执行）:
    set LLM_API_KEY=你的key
    set LLM_BASE_URL=https://api.deepseek.com
    set LLM_MODEL=deepseek-chat
    python -m ai_case_gen.main ai_case_gen/api_doc_example.md
"""
import json
import os
import sys
import time

from ai_case_gen.case_generator import CaseGenerator
from ai_case_gen.coverage import compute_coverage, manual_coverage
from ai_case_gen.review_workflow import review_cases, save_cases

# 人工编写单条用例的估算耗时（5 分钟/条，可按实际团队情况调整）
ESTIMATED_MANUAL_MINUTES_PER_CASE = 5


def build_report(draft_cases, accepted, gen_seconds, review_seconds, review_stats=None):
    """构建三方对比报告：AI 草稿 / AI 采纳 / 人工编写"""
    stats = review_stats or {}
    draft_cov = compute_coverage(draft_cases)
    accepted_cov = compute_coverage(accepted)
    manual_cov = manual_coverage()

    manual_seconds_per_case = ESTIMATED_MANUAL_MINUTES_PER_CASE * 60
    # 草稿单条耗时：只算生成，反映 AI 的产出速度
    draft_seconds_per_case = round(gen_seconds / max(len(draft_cases), 1), 2)
    # 综合单条耗时：生成 + 人工审核后，每条被采纳用例的真实成本
    combined_seconds_per_case = round(
        (gen_seconds + review_seconds) / max(len(accepted), 1), 2
    )

    report = {
        "checklist_total": draft_cov["total"],
        "ai_draft": {
            "case_count": len(draft_cases),
            "generate_seconds": round(gen_seconds, 1),
            "seconds_per_case": draft_seconds_per_case,
            "coverage": draft_cov["coverage"],
            "miss_rate": draft_cov["miss_rate"],
            "missed_ids": draft_cov["missed_ids"],
        },
        "ai_accepted": {
            "case_count": len(accepted),
            "accepted_from_draft": stats.get("accepted_from_draft", len(accepted)),
            "added_by_human": stats.get("added", 0),
            "rejected": stats.get("rejected", 0),
            "reject_rate": round(stats.get("rejected", 0) / max(len(draft_cases), 1), 2),
            "review_seconds": round(review_seconds, 1),
            "review_seconds_estimated": stats.get("review_seconds_estimated", False),
            "seconds_per_case": combined_seconds_per_case,
            "coverage": accepted_cov["coverage"],
            "miss_rate": accepted_cov["miss_rate"],
            "missed": accepted_cov["missed"],
        },
        "manual_baseline": {
            "case_count": manual_cov["case_count"],
            "estimated_minutes_per_case": ESTIMATED_MANUAL_MINUTES_PER_CASE,
            "seconds_per_case": manual_seconds_per_case,
            "coverage": manual_cov["coverage"],
            "miss_rate": manual_cov["miss_rate"],
        },
        "efficiency": {
            "improvement_by_generation": round(
                manual_seconds_per_case / max(draft_seconds_per_case, 1), 1
            ),
            "improvement_by_combined": round(
                manual_seconds_per_case / max(combined_seconds_per_case, 1), 1
            ),
        },
    }
    return report, draft_cov, accepted_cov


def print_report(report, draft_cov, accepted_cov):
    """打印 AI 草稿 / AI 采纳 / 人工编写 三方对比"""
    ai_draft = report["ai_draft"]
    ai_acc = report["ai_accepted"]
    manual = report["manual_baseline"]

    print("\n" + "=" * 74)
    print("AI 生成 vs 人工编写 对比报告（场景覆盖率 / 遗漏率 / 单条耗时）")
    print("=" * 74)
    print(f"{'维度':<12}{'AI草稿':<22}{'AI采纳':<22}{'人工编写'}")
    print(f"{'用例数':<12}{ai_draft['case_count']:<22}{ai_acc['case_count']:<22}{manual['case_count']}")
    print(f"{'覆盖率':<12}{ai_draft['coverage']:<22}{ai_acc['coverage']:<22}{manual['coverage']}")
    print(f"{'遗漏率':<12}{ai_draft['miss_rate']:<22}{ai_acc['miss_rate']:<22}{manual['miss_rate']}")
    print(f"{'单条耗时(s)':<12}{str(ai_draft['seconds_per_case']) + '(生成)':<22}"
          f"{str(ai_acc['seconds_per_case']) + '(生成+审核)':<22}{manual['seconds_per_case']}(估算)")
    print(f"\nAI 草稿拒绝率: {ai_acc['reject_rate']}"
          f"（采纳草稿 {ai_acc['accepted_from_draft']} 条，拒绝 {ai_acc['rejected']} 条，"
          f"人工补充 {ai_acc['added_by_human']} 条）")
    print(f"效率提升（仅生成阶段）约 {report['efficiency']['improvement_by_generation']} 倍")
    print(f"效率提升（含人工审核综合）约 {report['efficiency']['improvement_by_combined']} 倍")

    if accepted_cov["missed"]:
        print(f"\n人工审核后仍遗漏的场景({len(accepted_cov['missed'])})：")
        for m in accepted_cov["missed"]:
            print(f"  - {m['id']}: {m['description']}")


def main():
    doc_file = sys.argv[1] if len(sys.argv) > 1 else "ai_case_gen/api_doc_example.md"
    with open(doc_file, encoding="utf-8") as f:
        api_doc = f.read()

    # 1. AI 生成用例草稿（记录耗时，用于效率对比）
    start = time.time()
    cases = CaseGenerator().generate(api_doc)
    ai_cost = time.time() - start
    print(f"\nAI 生成 {len(cases)} 条用例草稿，耗时 {ai_cost:.1f}s，进入人工审核...")

    # 2. 人工过滤补充后入库（记录审核耗时，用于综合效率对比）
    review_start = time.time()
    accepted, review_stats = review_cases(cases)
    review_cost = time.time() - review_start
    save_cases(accepted, "data/ai_generated_cases.yaml")

    # 3. 覆盖率、遗漏率与效率对比（AI草稿 / AI采纳 / 人工编写）
    report, draft_cov, accepted_cov = build_report(
        cases, accepted, ai_cost, review_cost, review_stats
    )

    os.makedirs("reports", exist_ok=True)
    with open("reports/ai_vs_manual_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print_report(report, draft_cov, accepted_cov)
    print("\n完整报告已写入 reports/ai_vs_manual_report.json")


if __name__ == "__main__":
    main()
