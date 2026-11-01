# -*- coding: utf-8 -*-
"""用户管理接口封装（增删改查）"""
from api.base_api import BaseApi


class UserApi(BaseApi):

    def use_token(self, token):
        """携带登录 token"""
        self.http.set_token(token)
        return self

    def create_user(self, username, password, nickname, role=None):
        """创建用户（常规传参方式）"""
        payload = {"username": username, "password": password, "nickname": nickname}
        if role:
            payload["role"] = role
        return self.http.post("/api/users", json=payload)

    def create_user_raw(self, payload):
        """以原始请求体创建用户（参数校验类用例使用，可传缺字段/非法字段）"""
        return self.http.post("/api/users", json=payload)

    def get_user(self, user_id):
        """查询单个用户"""
        return self.http.get(f"/api/users/{user_id}")

    def list_users(self):
        """查询用户列表"""
        return self.http.get("/api/users")

    def update_user(self, user_id, **fields):
        """修改用户，fields 支持 nickname/password/role"""
        return self.http.put(f"/api/users/{user_id}", json=fields)

    def delete_user(self, user_id):
        """删除用户"""
        return self.http.delete(f"/api/users/{user_id}")
