# -*- coding: utf-8 -*-
"""权限与越权用例：未认证访问、垂直越权、水平越权、正常权限"""
import uuid

import allure


@allure.epic("接口自动化测试平台")
@allure.feature("权限与越权")
class TestPermission:

    @allure.story("未认证访问")
    @allure.title("未携带token访问接口返回401")
    def test_no_token(self, no_auth_api):
        resp = no_auth_api.list_users()
        assert resp.status_code == 401

    @allure.story("未认证访问")
    @allure.title("携带无效token访问接口返回401")
    def test_invalid_token(self, no_auth_api):
        no_auth_api.http.set_token("invalid_token_123456")
        resp = no_auth_api.list_users()
        assert resp.status_code == 401

    @allure.story("垂直越权")
    @allure.title("普通用户创建用户被拒绝403")
    def test_normal_user_create_user(self, normal_user_api):
        resp = normal_user_api.create_user("hack_" + uuid.uuid4().hex[:8], "Hack@12345", "越权用户")
        assert resp.status_code == 403

    @allure.story("垂直越权")
    @allure.title("普通用户删除用户被拒绝403")
    def test_normal_user_delete_user(self, normal_user_api, temp_user):
        resp = normal_user_api.delete_user(temp_user["user_id"])
        assert resp.status_code == 403

    @allure.story("垂直越权")
    @allure.title("普通用户查询用户列表被拒绝403")
    def test_normal_user_list_users(self, normal_user_api):
        resp = normal_user_api.list_users()
        assert resp.status_code == 403

    @allure.story("垂直越权")
    @allure.title("普通用户尝试提升角色为管理员被拒绝403")
    def test_normal_user_escalate_role(self, normal_user_api, normal_user_id):
        resp = normal_user_api.update_user(normal_user_id, role="admin")
        assert resp.status_code == 403

    @allure.story("水平越权")
    @allure.title("普通用户查询他人信息被拒绝403")
    def test_normal_user_query_other(self, normal_user_api, temp_user):
        resp = normal_user_api.get_user(temp_user["user_id"])
        assert resp.status_code == 403

    @allure.story("水平越权")
    @allure.title("普通用户修改他人信息被拒绝403")
    def test_normal_user_update_other(self, normal_user_api, temp_user):
        resp = normal_user_api.update_user(temp_user["user_id"], nickname="越权修改")
        assert resp.status_code == 403

    @allure.story("正常权限")
    @allure.title("普通用户查询自己的信息成功")
    def test_normal_user_query_self(self, normal_user_api, normal_user_id):
        resp = normal_user_api.get_user(normal_user_id)
        assert resp.status_code == 200

    @allure.story("正常权限")
    @allure.title("管理员操作任意用户成功")
    def test_admin_operate_any_user(self, user_api, temp_user):
        resp = user_api.update_user(temp_user["user_id"], nickname="管理员修改")
        assert resp.status_code == 200
