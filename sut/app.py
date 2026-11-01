# -*- coding: utf-8 -*-
"""
被测系统（SUT）：用户管理演示服务
提供登录鉴权、用户增删改查、参数校验、权限控制（管理员/普通用户）。
"""
import re
import uuid

from flask import Flask, jsonify, request

app = Flask(__name__)

# ---------- 模拟数据库（内存存储） ----------
users_db = {}   # user_id -> 用户信息
tokens_db = {}  # token   -> user_id

PRESET_ACCOUNTS = [
    {"username": "admin",   "password": "Admin@123", "role": "admin", "nickname": "管理员"},
    {"username": "test001", "password": "Test@123",  "role": "user",  "nickname": "普通用户"},
]


def _init_db():
    for acc in PRESET_ACCOUNTS:
        uid = str(uuid.uuid4())
        users_db[uid] = {"user_id": uid, **acc}


_init_db()


# ---------- 工具函数 ----------
def _resp(code, msg, data=None, http_status=200):
    """统一响应格式：{"code": 业务码, "msg": 描述, "data": 数据}"""
    return jsonify({"code": code, "msg": msg, "data": data}), http_status


def _find_by_username(username):
    for uid, u in users_db.items():
        if u["username"] == username:
            return uid, u
    return None, None


def _current_user():
    """从请求头 Authorization: Bearer {token} 解析当前登录用户"""
    auth = request.headers.get("Authorization", "")
    token = auth.replace("Bearer ", "").strip()
    uid = tokens_db.get(token)
    return (uid, users_db[uid]) if uid else (None, None)


def _public(u):
    """对外返回的用户信息（不暴露密码）"""
    return {"user_id": u["user_id"], "username": u["username"],
            "nickname": u["nickname"], "role": u["role"]}


def _validate_create(data):
    """创建用户参数校验，返回错误信息或 None"""
    if not isinstance(data, dict):
        return "请求体必须为 JSON 对象"
    for field in ("username", "password", "nickname"):
        if field not in data or data[field] in (None, ""):
            return f"缺少必填字段: {field}"
    if not isinstance(data["username"], str) or not re.fullmatch(r"[a-zA-Z0-9_]{4,20}", data["username"]):
        return "username 需为 4-20 位字母、数字或下划线"
    if not isinstance(data["password"], str) or not 6 <= len(data["password"]) <= 32:
        return "password 长度需为 6-32 位"
    if not isinstance(data["nickname"], str) or not 1 <= len(data["nickname"]) <= 30:
        return "nickname 长度需为 1-30 位"
    return None


# ---------- 接口 ----------
@app.route("/api/ping", methods=["GET"])
def ping():
    """健康检查（测试框架用它确认服务可用）"""
    return _resp(0, "pong")


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username, password = data.get("username"), data.get("password")
    if not username or not password:
        return _resp(400, "用户名和密码不能为空", http_status=400)
    uid, user = _find_by_username(username)
    if not user or user["password"] != password:
        return _resp(401, "用户名或密码错误", http_status=401)
    token = uuid.uuid4().hex
    tokens_db[token] = uid
    return _resp(0, "success", {"token": token, "user_id": uid, "role": user["role"]})


@app.route("/api/users", methods=["POST"])
def create_user():
    _, current = _current_user()
    if not current:
        return _resp(401, "未登录或 token 无效", http_status=401)
    if current["role"] != "admin":
        return _resp(403, "无权限执行该操作", http_status=403)
    data = request.get_json(silent=True)
    err = _validate_create(data)
    if err:
        return _resp(400, err, http_status=400)
    if _find_by_username(data["username"])[0]:
        return _resp(409, "用户名已存在", http_status=409)
    uid = str(uuid.uuid4())
    users_db[uid] = {"user_id": uid, "username": data["username"], "password": data["password"],
                     "nickname": data["nickname"], "role": data.get("role", "user")}
    return _resp(0, "success", {"user_id": uid})


@app.route("/api/users", methods=["GET"])
def list_users():
    _, current = _current_user()
    if not current:
        return _resp(401, "未登录或 token 无效", http_status=401)
    if current["role"] != "admin":
        return _resp(403, "无权限执行该操作", http_status=403)
    return _resp(0, "success", [_public(u) for u in users_db.values()])


@app.route("/api/users/<user_id>", methods=["GET"])
def get_user(user_id):
    uid, current = _current_user()
    if not current:
        return _resp(401, "未登录或 token 无效", http_status=401)
    if current["role"] != "admin" and uid != user_id:
        return _resp(403, "无权限查看其他用户", http_status=403)
    target = users_db.get(user_id)
    if not target:
        return _resp(404, "用户不存在", http_status=404)
    return _resp(0, "success", _public(target))


@app.route("/api/users/<user_id>", methods=["PUT"])
def update_user(user_id):
    uid, current = _current_user()
    if not current:
        return _resp(401, "未登录或 token 无效", http_status=401)
    if current["role"] != "admin" and uid != user_id:
        return _resp(403, "无权限修改其他用户", http_status=403)
    target = users_db.get(user_id)
    if not target:
        return _resp(404, "用户不存在", http_status=404)
    data = request.get_json(silent=True) or {}
    if "role" in data and current["role"] != "admin":
        return _resp(403, "无权限修改角色", http_status=403)
    if "nickname" in data:
        if not isinstance(data["nickname"], str) or not 1 <= len(data["nickname"]) <= 30:
            return _resp(400, "nickname 长度需为 1-30 位", http_status=400)
        target["nickname"] = data["nickname"]
    if "password" in data:
        if not isinstance(data["password"], str) or not 6 <= len(data["password"]) <= 32:
            return _resp(400, "password 长度需为 6-32 位", http_status=400)
        target["password"] = data["password"]
    if "role" in data and data["role"] in ("admin", "user"):
        target["role"] = data["role"]
    return _resp(0, "success", _public(target))


@app.route("/api/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    uid, current = _current_user()
    if not current:
        return _resp(401, "未登录或 token 无效", http_status=401)
    if current["role"] != "admin":
        return _resp(403, "无权限执行该操作", http_status=403)
    if user_id not in users_db:
        return _resp(404, "用户不存在", http_status=404)
    if user_id == uid:
        return _resp(400, "不能删除当前登录的管理员账号", http_status=400)
    del users_db[user_id]
    for t, u in list(tokens_db.items()):  # 清理该用户的登录态
        if u == user_id:
            del tokens_db[t]
    return _resp(0, "success")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
