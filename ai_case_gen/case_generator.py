# -*- coding: utf-8 -*-
"""调用大模型 API，根据接口文档生成测试用例草稿

通过环境变量配置（兼容 OpenAI / DeepSeek / 通义千问 / 豆包等 OpenAI 协议接口）:
    LLM_API_KEY   - 大模型 API Key
    LLM_BASE_URL  - 接口地址，如 https://api.deepseek.com
    LLM_MODEL     - 模型名称，如 deepseek-chat
"""
import os

import yaml
from openai import OpenAI

from ai_case_gen.prompt_template import CASE_GEN_PROMPT


class CaseGenerator:
    def __init__(self, api_key=None, base_url=None, model=None):
        self.client = OpenAI(
            api_key=api_key or os.getenv("LLM_API_KEY"),
            base_url=base_url or os.getenv("LLM_BASE_URL"),
        )
        self.model = model or os.getenv("LLM_MODEL", "deepseek-chat")

    def generate(self, api_doc: str) -> list:
        """生成用例草稿并解析为 Python 列表"""
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": CASE_GEN_PROMPT.format(api_doc=api_doc)}],
            temperature=0.3,  # 低温让输出更稳定，便于解析
        )
        content = resp.choices[0].message.content
        return self._parse_yaml(content)

    @staticmethod
    def _parse_yaml(content: str) -> list:
        """解析模型输出，兼容被 ```yaml 代码块包裹的情况"""
        text = content.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("yaml"):
                text = text[4:]
        data = yaml.safe_load(text)
        return data.get("cases", []) if data else []
