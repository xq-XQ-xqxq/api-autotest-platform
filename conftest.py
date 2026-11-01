# -*- coding: utf-8 -*-
"""pytest 全局配置：被测系统保障、登录态 fixture、数据清理 fixture"""
import os
import subprocess
import sys
import time
import uuid

import pytest
import requests

from api.base_api import ROOT_DIR, get_config
from api.login_api import LoginApi
from api.user_api import UserApi


# ---------- 被测系统保障 ----------
def _is_alive(base_url):
    try:
        return requests.get(base_url + "/api/ping", timeout=1).status_code == 200
    except requests.RequestException:
        return False


@pytest.fixture(scope="session", autouse=True)
def ensure_sut_running():
    """确认被测系统可用；若本地演示系统未启动则自动拉起，会话结束自动关闭"""
    config = get_config()
    base_url = config[config.get("env", "test")]["base_url"]
    if _is_alive(base_url):
        yield
        return
    proc = subprocess.Popen(
        [sys.executable, os.path.join(ROOT_DIR, "sut", "app.py")],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(50):
        if _is_alive(base_url):
            break
        time.sleep(0.2)
    else:
        proc.terminate()
        raise RuntimeError("被测系统启动失败，请手动执行: python sut/app.py")
    yield
    proc.terminate()


# ---------- 登录态 ----------
@pytest.fixture(scope="session")
def admin_token(ensure_sut_running):
    """管理员 token（整个测试会话只登录一次）"""
    acc = get_config()["account"]["admin"]
    return LoginApi().login_and_get_token(acc["username"], acc["password"])


@pytest.fixture(scope="session")
def normal_token(ensure_sut_running):
    """普通用户 token"""
    acc = get_config()["account"]["normal"]
    return LoginApi().login_and_get_token(acc["username"], acc["password"])


@pytest.fixture(scope="session")
def normal_user_id(ensure_sut_running):
    """普通用户的 user_id（登录响应中获取）"""
    acc = get_config()["account"]["normal"]
    resp = LoginApi().login(acc["username"], acc["password"])
    return resp.json()["data"]["user_id"]


# ---------- 接口句柄 ----------
@pytest.fixture()
def user_api(admin_token):
    """携带管理员 token 的用户接口"""
    return UserApi().use_token(admin_token)


@pytest.fixture()
def normal_user_api(normal_token):
    """携带普通用户 token 的用户接口"""
    return UserApi().use_token(normal_token)


@pytest.fixture()
def no_auth_api():
    """未携带 token 的用户接口"""
    return UserApi()


# ---------- 数据准备与清理 ----------
@pytest.fixture()
def temp_user(user_api):
    """临时用户：测试前创建，测试后删除，保证环境干净"""
    uname = "tmp_" + uuid.uuid4().hex[:8]
    resp = user_api.create_user(uname, "Tmp@123456", "临时用户")
    assert resp.status_code == 200, f"临时用户创建失败: {resp.text}"
    user_id = resp.json()["data"]["user_id"]
    yield {"user_id": user_id, "username": uname, "password": "Tmp@123456"}
    user_api.delete_user(user_id)  # 若用例中已删除则返回 404，不影响结果
