# -*- coding: utf-8 -*-
"""requests 二次封装：统一 token 管理、日志记录、Allure 报告步骤"""
import json

import allure
import requests

from common.logger import logger


class RequestHandler:
    def __init__(self, base_url, timeout=10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def set_token(self, token):
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        return self

    def clear_token(self):
        self.session.headers.pop("Authorization", None)
        return self

    def request(self, method, path, **kwargs):
        url = self.base_url + path
        kwargs.setdefault("timeout", self.timeout)
        logger.info(f"请求: {method} {url} | 参数: {_fmt(kwargs)}")
        with allure.step(f"{method} {path}"):
            allure.attach(_fmt(kwargs), name="请求参数", attachment_type=allure.attachment_type.TEXT)
            resp = self.session.request(method, url, **kwargs)
            allure.attach(resp.text, name="响应内容", attachment_type=allure.attachment_type.TEXT)
        logger.info(f"响应: {resp.status_code} | {resp.text}")
        return resp

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)


def _fmt(kwargs):
    """提取请求参数用于日志/报告展示"""
    parts = {k: v for k, v in kwargs.items() if k in ("json", "params", "data")}
    try:
        return json.dumps(parts, ensure_ascii=False, default=str)
    except TypeError:
        return str(parts)
