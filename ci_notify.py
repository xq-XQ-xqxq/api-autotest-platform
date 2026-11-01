# -*- coding: utf-8 -*-
"""构建后通知脚本（钉钉机器人），供 Jenkins 在 success/failure 阶段调用

用法:
    python ci_notify.py success
    python ci_notify.py failure

环境变量:
    DINGTALK_WEBHOOK  钉钉机器人 Webhook 地址（未设置则跳过通知）
    JOB_NAME / BUILD_NUMBER / BUILD_URL  由 Jenkins 自动注入
"""
import os
import sys

import requests

WEBHOOK = os.getenv("DINGTALK_WEBHOOK", "")
JOB_NAME = os.getenv("JOB_NAME", "接口自动化回归")
BUILD_NO = os.getenv("BUILD_NUMBER", "")
BUILD_URL = os.getenv("BUILD_URL", "")


def notify(result: str):
    if not WEBHOOK:
        print("[ci_notify] 未设置 DINGTALK_WEBHOOK 环境变量，跳过钉钉通知。")
        return 0

    icon = "✅ 通过" if result == "success" else "❌ 失败"
    text = (
        f"【{JOB_NAME}】构建结果: {icon}\n"
        f"构建编号: #{BUILD_NO}\n"
        f"构建地址: {BUILD_URL}\n"
        f"Allure 报告: {BUILD_URL}allure/"
    )
    payload = {"msgtype": "text", "text": {"content": text}}
    try:
        resp = requests.post(WEBHOOK, json=payload, timeout=5)
        print(f"[ci_notify] 钉钉通知响应: {resp.status_code} {resp.text[:200]}")
        return 0 if resp.status_code == 200 else 1
    except requests.RequestException as e:
        print(f"[ci_notify] 通知发送异常: {e}")
        return 1


if __name__ == "__main__":
    result = sys.argv[1] if len(sys.argv) > 1 else "success"
    sys.exit(notify(result))
