# Charles 抓包与接口整理记录

> 本项目用 Charles 抓取被测系统（`sut/app.py`，地址 `http://127.0.0.1:5000`）的真实请求/响应，
> 并据此整理出接口文档 `ai_case_gen/api_doc_example.md`，作为 AI 用例生成的输入。
> 真实企业项目中，被测系统通常不是自己写的，Charles 是获取接口的主要手段。

## 1. Charles 基本设置

1. **安装与信任证书**：安装 Charles 根证书并在系统/浏览器中信任，才能解密 HTTPS。
2. **Proxy → Proxy Settings**：开启 HTTP Proxy，默认端口 8888。
3. **Proxy → SSL Proxying Settings**：把被测域名加入 SSL Proxying（本项目是 HTTP，可省略）。
4. **浏览器/系统代理**：指向 `127.0.0.1:8888`。

## 2. 本机 Flask 服务抓包要点

`127.0.0.1` / `localhost` 的请求浏览器默认不经过系统代理，Charles 可能抓不到。
解决方法任选其一：
- 用 `localhost.charlesproxy.com` 代替 `localhost` 访问接口；
- 或在 Chrome 启动参数加 `--proxy-server=127.0.0.1:8888`；
- 或用 Postman/requests 时显式设置代理 `proxies={"http": "http://127.0.0.1:8888"}`。

## 3. 抓到的接口清单（与 `sut/app.py` 对应）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET  | `/api/ping` | 健康检查 |
| POST | `/api/login` | 登录，返回 token |
| POST | `/api/users` | 管理员创建用户 |
| GET  | `/api/users` | 管理员查询用户列表 |
| GET  | `/api/users/{id}` | 查询单个用户 |
| PUT  | `/api/users/{id}` | 修改用户 |
| DELETE | `/api/users/{id}` | 删除用户 |

## 4. 抓包结果如何用

1. 用 Charles 抓到每个接口的 **URL、Method、请求头、请求体、响应体**；
2. 把这些信息整理成接口文档，写入 `ai_case_gen/api_doc_example.md`；
3. 运行 `python -m ai_case_gen.main`，AI 依据该文档生成用例草稿；
4. 人工过滤补充后入库到 `data/ai_generated_cases.yaml`。

## 5. 常见抓包场景

- **鉴权**：在 Charles 的请求头里观察 `Authorization: Bearer xxx`，确认登录接口返回的 token 是否被后续请求带上。
- **越权**：用管理员 token 抓一个删除请求，再用普通用户 token 重放（Compose），观察是否返回 403。
- **参数校验**：用 Charles 的 Edit 请求功能改字段（如删掉 username），观察 400 错误信息。
