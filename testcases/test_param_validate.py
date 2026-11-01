# -*- coding: utf-8 -*-
"""参数校验用例（数据驱动）"""
import uuid

import allure
import pytest

from api.base_api import load_data

cases = load_data("user_data.yaml")["create_user_cases"]


@allure.epic("接口自动化测试平台")
@allure.feature("参数校验")
class TestParamValidate:

    @allure.story("创建用户参数校验")
    @pytest.mark.parametrize("case", cases, ids=[c["title"] for c in cases])
    def test_create_user_validate(self, user_api, case):
        payload = dict(case["payload"])
        if payload.get("username") == "<random>":
            payload["username"] = "auto_" + uuid.uuid4().hex[:8]

        resp = user_api.create_user_raw(payload)
        assert resp.status_code == case["expected_status"], f"响应: {resp.text}"
        body = resp.json()
        assert body["code"] == case["expected_code"]
        if case.get("expected_msg"):
            assert case["expected_msg"] in body["msg"]

        # 数据清理：创建成功的用户用完即删
        if resp.status_code == 200:
            user_api.delete_user(body["data"]["user_id"])

    @allure.story("修改用户参数校验")
    @allure.title("修改昵称超长被拦截")
    def test_update_nickname_too_long(self, user_api, temp_user):
        resp = user_api.update_user(temp_user["user_id"], nickname="x" * 31)
        assert resp.status_code == 400
