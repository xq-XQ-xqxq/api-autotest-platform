# 接口自动化测试平台 + AI 用例生成

自己做的一个测试开发练习项目。用 pytest + requests 搭了一套接口自动化框架，挂了 Allure 报告和 Jenkins，后面又加了个大模型生成用例的功能，顺便对比了一下 AI 写用例和人写用例的效率差距。

框架分了五层：配置、接口、用例、数据、工具。主要想法是接口变了只改 api 那一层，加用例只改 YAML 数据，不用动代码。目前有 36 条用例，覆盖登录、增删改查、参数校验和越权（垂直越权和水平越权都有）。项目里自带一个 Flask 写的被测系统（sut/app.py），跑 pytest 会自动拉起来，不用手动启服务。

## 怎么跑起来

环境：Python 3.10 以上就行。看报告需要额外装 allure 命令行，AI 功能需要一个大模型的 key，这两个都是可选的。

```bash
git clone https://github.com/xq-XQ-xqxq/api-autotest-platform.git
cd api-autotest-platform
pip install -r requirements.txt
python -m pytest
```

看到 36 passed 就跑通了。

### 看 Allure 报告

```bash
python run.py --open
```

没装 allure 的话先装一下（有 npm 的话 `npm install -g allure-commandline` 最省事，Windows 也可以 `scoop install allure`）。报告里能看到每条用例的请求和响应原文，失败的时候排查很方便。

### AI 生成用例（可选）

```powershell
$env:LLM_API_KEY="你的key"
$env:LLM_BASE_URL="https://api.deepseek.com"
$env:LLM_MODEL="deepseek-chat"
python -m ai_case_gen.main
```

跑起来之后它会读接口文档，让大模型生成一批用例草稿，然后在终端里一条条让你审（y 接受，n 拒绝，e 编辑，a 自己补一条，s 跳过后面的）。审完会打印一个对比表：AI 草稿、AI 采纳、人工编写三方的覆盖率、遗漏率和单条耗时。

用下来感觉 AI 想得挺全的，边界值覆盖比我自己写的还细，但预期结果经常写错（比如该 403 的它写 200），所以人工过一遍是必须的。key 只从环境变量读，不会写进任何文件。

## 目录结构

```
├── config/           配置：环境地址、账号
├── api/              接口封装：login_api、user_api
├── testcases/        用例：登录、CRUD、参数校验、越权
├── data/             测试数据（YAML）和场景基线
├── common/           请求封装、日志、读 YAML
├── ai_case_gen/      AI 用例生成 + 审核 + 覆盖率对比
├── sut/app.py        被测系统（Flask，练习用）
├── conftest.py       fixture：启服务、登录拿 token、数据清理
├── ci_notify.py      Jenkins 构建后发钉钉通知
├── Jenkinsfile       流水线：定时跑 + 提交触发
└── run.py            跑测试 + 出报告
```

## 加用例不用写代码

测试数据都在 `data/` 下的 YAML 里，比如要加一个登录场景，在 `data/login_data.yaml` 里补一段就行：

```yaml
  - title: 超长用户名登录
    username: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    password: "Admin@123"
    expected_status: 401
    expected_code: 401
    expected_msg: "用户名或密码错误"
```

重跑 pytest 用例数就 +1 了。

## Jenkins

Jenkinsfile 里配了每天凌晨定时跑，同时每 10 分钟轮询代码有没有新提交，有就自动回归。跑完生成 Allure 报告，成功失败都会调 `ci_notify.py` 发钉钉通知（webhook 地址走 Jenkins 的环境变量 `DINGTALK_WEBHOOK`，不配就跳过，不会卡住构建）。

## 接真实项目

sut 只是个练习靶子。真要用到自己项目上，改 `config/config.yaml` 里的 `base_url` 和账号就行，其他代码不用动。接口整理过程我是用 Charles 抓包做的，记录在 `docs/charles_capture_notes.md`。

## 踩过的坑

- 端口被占用：5000 被别的程序占了，关掉或者改 config 里的地址
- allure 报告打不开：数据在 reports/allure-results，跑 `allure serve reports/allure-results`
- AI 调不通：先确认 key 没过期，base_url 别漏了 https://
