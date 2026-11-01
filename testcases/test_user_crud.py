# -*- coding: utf-8 -*-
"""用户增删改查（CRUD）用例"""
import uuid

import allure


@allure.epic("接口自动化测试平台")
@allure.feature("用户管理")
class TestUserCrud:

    @allure.story("增删改查业务闭环")
    @allure.title("新增 -> 查询 -> 修改 -> 再查 -> 删除 完整业务流程")
    def test_user_business_flow(self, user_api):
        uname = "flow_" + uuid.uuid4().hex[:8]

        with allure.step("1. 新增用户"):
            resp = user_api.create_user(uname, "Flow@12345", "流程用户")
            assert resp.status_code == 200, resp.text
            user_id = resp.json()["data"]["user_id"]

        with allure.step("2. 查询用户，验证新增数据正确"):
            resp = user_api.get_user(user_id)
            assert resp.status_code == 200
            assert resp.json()["data"]["username"] == uname
            assert resp.json()["data"]["nickname"] == "流程用户"

        with allure.step("3. 修改用户昵称"):
            resp = user_api.update_user(user_id, nickname="流程用户-已修改")
            assert resp.status_code == 200

        with allure.step("4. 再次查询，验证修改生效"):
            resp = user_api.get_user(user_id)
            assert resp.json()["data"]["nickname"] == "流程用户-已修改"

        with allure.step("5. 删除用户"):
            resp = user_api.delete_user(user_id)
            assert resp.status_code == 200

        with allure.step("6. 查询已删除用户，应返回 404"):
            resp = user_api.get_user(user_id)
            assert resp.status_code == 404

    @allure.story("查询用户")
    @allure.title("查询存在的用户成功")
    def test_query_exist_user(self, user_api, temp_user):
        resp = user_api.get_user(temp_user["user_id"])
        assert resp.status_code == 200
        assert resp.json()["data"]["username"] == temp_user["username"]

    @allure.story("查询用户")
    @allure.title("查询不存在的用户返回404")
    def test_query_not_exist_user(self, user_api):
        resp = user_api.get_user("not_exist_user_id_000")
        assert resp.status_code == 404

    @allure.story("修改用户")
    @allure.title("修改存在的用户信息成功")
    def test_update_exist_user(self, user_api, temp_user):
        resp = user_api.update_user(temp_user["user_id"], nickname="新昵称")
        assert resp.status_code == 200
        resp = user_api.get_user(temp_user["user_id"])
        assert resp.json()["data"]["nickname"] == "新昵称"

    @allure.story("修改用户")
    @allure.title("修改不存在的用户返回404")
    def test_update_not_exist_user(self, user_api):
        resp = user_api.update_user("not_exist_user_id_000", nickname="新昵称")
        assert resp.status_code == 404

    @allure.story("删除用户")
    @allure.title("删除存在的用户成功")
    def test_delete_exist_user(self, user_api, temp_user):
        resp = user_api.delete_user(temp_user["user_id"])
        assert resp.status_code == 200
        resp = user_api.get_user(temp_user["user_id"])
        assert resp.status_code == 404

    @allure.story("删除用户")
    @allure.title("删除不存在的用户返回404")
    def test_delete_not_exist_user(self, user_api):
        resp = user_api.delete_user("not_exist_user_id_000")
        assert resp.status_code == 404

    @allure.story("用户列表")
    @allure.title("管理员查询用户列表成功")
    def test_list_users(self, user_api):
        resp = user_api.list_users()
        assert resp.status_code == 200
        assert isinstance(resp.json()["data"], list)
