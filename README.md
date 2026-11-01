# 接口自动化测试平台 + AI 用例生成

个人独立完成的测试开发项目：基于 pytest + requests 的分层接口自动化测试框架，集成 Allure 可视化报告与 Jenkins 持续集成，并通过大模型 API 生成测试用例草稿，人工审核入库后量化对比 AI 与人工编写的覆盖率、遗漏率与效率。

框架按五层设计：配置 / 接口 / 用例 / 数据 / 工具。核心目标是解耦——接口变更只改 `api/` 层，新增场景只改 YAML 数据，测试代码保持稳定。当前共 36 条用例，覆盖登录、增删改查（CRUD）、参数校验（等价类划分 + 边界值分析）、权限越权（垂直越权与水平越权）。仓库内置一个 Flask 编写的被测系统（`sut/app.py`），执行 pytest 时由 `conftest.py` 自动拉起，测试结束自动回收，无需人工启停服务。

## 环境要求

Python 3.10+ 即可。Allure 命令行工具和大模型 API Key 均为可选，分别对应报告生成和 AI 用例生成两个增强功能。

## 快速开始

```bash
git clone https://github.com/xq-XQ-xqxq/api-autotest-platform.git
cd api-autotest-platform
pip install -r requirements.txt
python -m pytest
```

输出 `36 passed` 即框架运行正常。

### 生成 Allure 报告

```bash
python run.py --open
```

未安装 allure 命令行工具时，可用 `npm install -g allure-commandline`（跨平台）或 `scoop install allure`（Windows）。报告中每条用例附带测试步骤及请求/响应原文附件，失败用例可直接定位到具体请求。

### AI 用例生成（可选）

```powershell
$env:LLM_API_KEY="你的key"
$env:LLM_BASE_URL="https://api.deepseek.com"
$env:LLM_MODEL="deepseek-chat"
python -m ai_case_gen.main
```

流程：读取接口文档 → 大模型生成用例草稿 → 终端逐条人工审核（`y` 接受 / `n` 拒绝 / `e` 编辑 / `a` 补充 / `s` 跳过剩余）→ 入库 → 输出 AI 草稿、AI 采纳、人工编写三方的覆盖率、遗漏率、单条耗时对比报告。

实测结论：AI 草稿的场景覆盖面较广，边界值设计甚至优于人工初稿，但部分用例的预期结果与接口真实行为不一致（例如将越权应返回的 403 误写为 200），属于典型的模型幻觉，因此人工审核是必要的质量关卡。API Key 仅通过环境变量读取，不写入任何文件。

## 目录结构

```
├── config/           配置层：环境地址、测试账号
├── api/              接口层：登录、用户管理的接口封装
├── testcases/        用例层：登录、CRUD、参数校验、权限越权
├── data/             数据层：YAML 测试数据 + 场景覆盖基线
├── common/           工具层：requests 二次封装、日志、YAML 解析
├── ai_case_gen/      AI 模块：用例生成、人工审核、覆盖率统计
├── sut/app.py        被测系统（Flask 演示服务）
├── conftest.py       pytest fixture：服务自举、token 注入、数据清理
├── ci_notify.py      构建后钉钉通知脚本
├── Jenkinsfile       声明式流水线：定时回归 + 提交触发
└── run.py            一键执行测试并生成报告
```

## 数据驱动：加用例不改代码

测试数据与测试代码分离，新增场景只需在 YAML 中追加数据。例如在 `data/login_data.yaml` 中：

```yaml
  - title: 超长用户名登录
    username: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    password: "Admin@123"
    expected_status: 401
    expected_code: 401
    expected_msg: "用户名或密码错误"
```

重跑 pytest 即自动新增一条参数化用例。

## 持续集成

`Jenkinsfile` 配置了声明式流水线：每天凌晨定时执行回归，同时每 10 分钟轮询代码变更（提交即回归）。构建完成后生成 Allure 报告，并调用 `ci_notify.py` 发送钉钉通知。Webhook 地址通过 Jenkins 环境变量 `DINGTALK_WEBHOOK` 注入，未配置时脚本自动跳过，不阻塞构建。

## 对接真实被测系统

`sut/` 仅是演示靶子。接入实际项目时，修改 `config/config.yaml` 中的 `base_url` 和账号即可，框架代码零改动。接口信息可先用 Charles 抓包整理，参考 `docs/charles_capture_notes.md`。

## 常见问题

- **端口占用**：5000 端口被占用时，关闭占用进程或修改 `config/config.yaml` 中的 `base_url`
- **报告无法打开**：原始数据在 `reports/allure-results`，执行 `allure serve reports/allure-results` 本地查看
- **AI 调用 401**：检查 `LLM_API_KEY` 有效性及 `LLM_BASE_URL` 是否包含 `https://`
