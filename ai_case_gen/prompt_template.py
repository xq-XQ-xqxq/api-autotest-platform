# -*- coding: utf-8 -*-
"""AI 用例生成 Prompt 模板"""

CASE_GEN_PROMPT = """你是一名资深测试开发工程师。请根据以下接口文档，为该接口设计测试用例草稿。

【接口文档】
{api_doc}

【设计要求】
1. 覆盖正常场景、参数校验（缺失/类型错误/边界值/特殊字符）、鉴权与越权、业务异常场景
2. 每条用例包含: title(标题), priority(优先级 P0/P1/P2), precondition(前置条件), steps(测试步骤), expected(预期结果)
3. 只输出 YAML，不要输出任何额外解释，格式如下:

cases:
  - title: 正确账号密码登录成功
    priority: P0
    precondition: 用户已注册
    steps: 调用 POST /api/login，传入正确用户名和密码
    expected: 返回 200，code 为 0，data 中包含 token
"""
