# -*- coding: utf-8 -*-
"""登录接口封装"""
from api.base_api import BaseApi


class LoginApi(BaseApi):

    def login(self, username, password):
        """登录，返回响应对象"""
        payload = {"username": username, "password": password}
        return self.http.post("/api/login", json=payload)

    def login_and_get_token(self, username, password):
        """登录并提取 token（供 fixture 使用）"""
        resp = self.login(username, password)
        assert resp.status_code == 200, f"登录失败: {resp.text}"
        return resp.json()["data"]["token"]
