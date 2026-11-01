# 用户管理模块接口文档

## 1. 用户登录
- URL: POST /api/login
- 请求体(JSON):
  - username: string, 必填
  - password: string, 必填
- 响应:
  - 成功: 200 {"code": 0, "msg": "success", "data": {"token": "...", "user_id": "...", "role": "..."}}
  - 失败: 401 {"code": 401, "msg": "用户名或密码错误"}
  - 参数缺失: 400 {"code": 400, "msg": "用户名和密码不能为空"}

## 2. 创建用户（仅管理员）
- URL: POST /api/users
- 请求头: Authorization: Bearer {token}
- 请求体(JSON):
  - username: string, 必填, 4-20位字母数字下划线, 不可重复
  - password: string, 必填, 6-32位
  - nickname: string, 必填, 1-30位
- 响应:
  - 成功: 200 {"code": 0, "data": {"user_id": "..."}}
  - 未登录: 401 / 非管理员: 403 / 参数错误: 400 / 用户名重复: 409

## 3. 查询用户
- URL: GET /api/users/{user_id}
- 请求头: Authorization: Bearer {token}
- 权限: 管理员可查任意用户；普通用户仅可查自己
- 响应: 200 {"code": 0, "data": {"user_id","username","nickname","role"}} / 401 / 403 / 404

## 4. 修改用户
- URL: PUT /api/users/{user_id}
- 请求头: Authorization: Bearer {token}
- 请求体(JSON): nickname(可选,1-30位), password(可选,6-32位), role(仅管理员可改)
- 权限: 管理员可改任意用户；普通用户仅可改自己
- 响应: 200 {"code": 0} / 400 / 401 / 403 / 404

## 5. 删除用户（仅管理员）
- URL: DELETE /api/users/{user_id}
- 请求头: Authorization: Bearer {token}
- 响应: 200 {"code": 0} / 401 / 403 / 404
