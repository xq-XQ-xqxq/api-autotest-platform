# -*- coding: utf-8 -*-
"""登录模块用例（数据驱动）"""
import allure
import pytest

from api.base_api import load_data
from api.login_api import LoginApi

cases = load_data("login_data.yaml")["login_cases"]


@allure.epic("接口自动化测试平台")
@allure.feature("登录模块")
class TestLogin:

    @allure.story("登录接口")
    @pytest.mark.parametrize("case", cases, ids=[c["title"] for c in cases])
    def test_login(self, case):
        resp = LoginApi().login(case["username"], case["password"])
        assert resp.status_code == case["expected_status"], f"响应: {resp.text}"
        body = resp.json()
        assert body["code"] == case["expected_code"]
        assert case["expected_msg"] in body["msg"]
        if resp.status_code == 200:
            assert body["data"]["token"], "登录成功应返回 token"
