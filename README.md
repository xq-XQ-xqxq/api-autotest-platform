# 接口自动化测试平台 + AI 用例生成

基于 **pytest + requests** 的分层接口自动化测试框架，接入 **Allure** 可视化报告与 **Jenkins** 持续集成，并用**大模型 API** 生成测试用例草稿，人工审核后入库，量化对比 AI 与人工编写的**覆盖率、遗漏率与效率**。

## 功能特性

- **分层框架**：配置 / 接口 / 用例 / 数据 / 工具 五层解耦，接口变更只需改 `api/` 层
- **36 条用例**：覆盖登录、增删改查（CRUD）、参数校验（等价类/边界值）、权限越权（垂直/水平）
- **数据驱动**：测试数据放 YAML，加用例 = 加数据，零代码改动
- **Allure 报告**：每条用例带步骤、请求/响应原文附件，失败可定位到具体请求
- **环境自举**：`pytest` 一跑自动拉起被测服务，跑完自动关闭，无需人工干预
- **CI 集成**：Jenkinsfile 定时回归 + 提交触发 + 钉钉构建后通知
- **AI 用例生成**：大模型按接口文档生成草稿 → 人工审核（接受/拒绝/编辑/补充）→ 入库 → 输出覆盖率/遗漏率/效率三方对比报告

## 环境要求

| 依赖 | 版本 | 说明 |
|---|---|---|
| Python | >= 3.10 | 必需 |
| Allure 命令行 | >= 2.x | 可选，仅生成网页报告需要 |
| 大模型 API Key | - | 可选，仅 AI 用例生成需要（DeepSeek / OpenAI 兼容协议均可） |

## 快速开始（5 分钟跑起来）

```bash
# 1. 克隆项目
git clone <仓库地址>
cd <项目目录>

# 2. 安装依赖
pip install -r requirements.txt

# 3. 跑全部用例（被测服务会自动拉起，无需手动启动）
python -m pytest
```

看到 `36 passed` 就说明框架跑通了。

### 生成并查看 Allure 报告

```bash
python run.py --open
```

跑完测试后自动生成 HTML 报告并在浏览器打开。若提示未安装 allure 命令行工具：

```bash
# 方式一：npm（推荐，跨平台）
npm install -g allure-commandline

# 方式二：scoop（Windows）
scoop install allure
```

也可以手动两步：

```bash
python -m pytest                      # 生成原始数据到 reports/allure-results
allure serve reports/allure-results   # 直接起本地服务看报告
```

## AI 用例生成（可选）

```bash
# Windows PowerShell
$env:LLM_API_KEY="你的key"
$env:LLM_BASE_URL="https://api.deepseek.com"
$env:LLM_MODEL="deepseek-chat"
python -m ai_case_gen.main
```

流程：读取 `ai_case_gen/api_doc_example.md` → 大模型生成用例草稿 → 终端逐条审核（`y` 接受 / `n` 拒绝 / `e` 编辑 / `a` 新增 / `s` 跳过）→ 入库 `data/ai_generated_cases.yaml` → 打印 **AI 草稿 / AI 采纳 / 人工编写** 三方对比表并写入 `reports/ai_vs_manual_report.json`。

> Key 只走环境变量，不会写入任何文件，请放心使用；也不要把 key 提交到仓库。

## 目录结构

```
├── config/config.yaml        # 【配置层】环境地址、测试账号
├── api/                      # 【接口层】每个接口封装成一个方法
│   ├── base_api.py           #   基类：加载配置、持有请求句柄
│   ├── login_api.py          #   登录接口
│   └── user_api.py           #   用户增删改查
├── testcases/                # 【用例层】36 条 pytest 用例
│   ├── test_login.py         #   登录（含 SQL 注入）
│   ├── test_user_crud.py     #   增删改查（含业务闭环）
│   ├── test_param_validate.py#   参数校验（数据驱动）
│   └── test_permission.py    #   权限越权（垂直/水平）
├── data/                     # 【数据层】YAML 测试数据 + 场景基线
├── common/                   # 工具层：请求封装、日志、YAML 读取
├── ai_case_gen/              # AI 用例生成模块
│   ├── case_generator.py     #   调用大模型生成草稿
│   ├── review_workflow.py    #   人工审核入库（y/n/e/a/s）
│   ├── coverage.py           #   覆盖率/遗漏率计算
│   └── main.py               #   主流程 + 三方对比报告
├── sut/app.py                # 被测系统（Flask 演示服务，练习用）
├── conftest.py               # fixture：自动拉起服务、token、数据清理
├── ci_notify.py              # 构建后钉钉通知（Jenkins 调用）
├── Jenkinsfile               # CI 流水线：定时回归 + 通知
├── run.py                    # 一键执行 + 生成 Allure 报告
└── pytest.ini                # pytest 配置（用例发现规则、报告输出）
```

## 如何扩展用例（数据驱动示例）

新增场景不需要写 Python，直接在 `data/` 的 YAML 里加一段：

```yaml
# data/login_data.yaml
login_cases:
  - title: 新场景：超长用户名登录
    username: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    password: "Admin@123"
    expected_status: 401
    expected_code: 401
    expected_msg: "用户名或密码错误"
```

保存后重跑 `python -m pytest`，用例数自动 +1。

## 持续集成（Jenkins）

`Jenkinsfile` 已配置好声明式流水线：

- `triggers`：每天凌晨定时执行 + 每 10 分钟轮询代码变更（提交即回归）
- `stages`：安装依赖 → 执行 pytest
- `post`：生成 Allure 报告（allure 插件）→ success/failure 调用 `python ci_notify.py` 发钉钉通知

钉钉机器人地址通过 Jenkins 环境变量 `DINGTALK_WEBHOOK` 注入；未配置时脚本优雅跳过，不阻塞构建。

## 被测系统说明

`sut/app.py` 是一个 Flask 演示服务（内存数据库，重启即重置），提供登录 + 用户管理接口，用于练习。**接入真实被测系统时**，只需修改 `config/config.yaml` 的 `base_url` 和账号，框架代码零改动。

## 常见问题

**Q: 跑 pytest 报错端口被占用？**
A: 说明已有服务占用 5000 端口。要么关掉它，要么改 `config/config.yaml` 的 `base_url` 指向其他端口。

**Q: Allure 报告打不开？**
A: 原始数据在 `reports/allure-results`，执行 `allure serve reports/allure-results` 起本地服务查看。

**Q: AI 生成报错 401？**
A: 检查 `LLM_API_KEY` 是否有效、`LLM_BASE_URL` 是否带 `https://`。
