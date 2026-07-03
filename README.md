# Python Learning

Python 学习与标准项目结构参考仓库。本文档介绍**通用 Python 项目架构**中各目录的职责，以及本仓库标准目录的用途与启动方式。

> 说明：`1_basics/`、`2_advanced/`、`practice/` 为个人练习目录，不在本文档范围内。

---

## 一、典型项目目录结构

中大型 Python 项目通常按**职责分层**，把「入口、配置、数据、业务、工具、测试」拆开，便于维护与协作。

```
project_root/
├── main.py                 # 应用入口（CLI / 脚本启动点）
├── requirements.txt        # 生产依赖(pip freeze > requirements.txt 这个命令生成----约等于package-lock.json)
├── requirements-dev/advanced.txt    # 开发 / 测试依赖（可选，约等于package.json dependencies）
├── .env                    # 本地环境变量（不提交 Git）
├── .gitignore
├── README.md
│
├── config/                 # 配置
├── models/                 # 数据模型 / 实体类
├── schemas/                # 请求 / 响应 DTO（Web 项目常见）
├── services/               # 业务逻辑层
├── repositories/           # 数据访问层（可选，ORM / SQL 封装）
├── api/ 或 routers/        # HTTP 路由（FastAPI / Flask 等）
├── utils/                  # 通用工具函数
├── middleware/             # 中间件（Web 项目）
├── tests/                  # 单元测试 / 集成测试
├── scripts/                # 一次性脚本、迁移、定时任务
├── migrations/             # 数据库迁移（Alembic 等）
├── static/                 # 静态资源
├── templates/              # 模板文件（Flask / Jinja2）
└── logs/                   # 运行日志（也可只写路径到配置）
```

Web 项目（FastAPI / Django / Flask）会在上述基础上增加 `api/`、`routers/`、`middleware/` 等；纯脚本或 CLI 项目可以没有这些目录。

---

## 二、各目录职责说明

| 目录 / 文件 | 作用 | 典型内容 |
|-------------|------|----------|
| **main.py** | 程序入口 | 初始化配置、启动服务或执行主流程 |
| **config/** | 配置管理 | 数据库连接、密钥、环境区分（dev / prod） |
| **models/** | 数据模型层 | 实体类、ORM Model（如 SQLAlchemy）、领域对象 |
| **schemas/** | 数据结构定义 | Pydantic 模型：API 入参、出参、校验规则 |
| **services/** | 业务逻辑层 | 核心业务：注册、下单、权限判断等，**不直接处理 HTTP** |
| **repositories/** | 数据访问层 | 封装 CRUD、SQL 查询，供 services 调用 |
| **api/ / routers/** | 接口层 | 路由定义：解析请求 → 调 service → 返回响应 |
| **utils/** | 工具层 | 日期格式化、加密、文件读写等无业务耦合的函数 |
| **middleware/** | 中间件 | 鉴权、日志、跨域、异常统一处理 |
| **tests/** | 测试 | `pytest` 用例，目录结构建议与源码对应 |
| **scripts/** | 脚本 | 数据导入、批处理、部署辅助脚本 |
| **requirements.txt** | 依赖清单 | `pip install -r requirements.txt` 安装 |
| **venv/** | 虚拟环境 | 隔离项目依赖，**一般不提交 Git** |

### 分层调用关系（推荐）

```
请求 → api/routers → services → repositories → 数据库
                         ↓
                      models / schemas（数据结构在各层传递）
                         ↓
                      utils（各层按需调用）
```

原则：

- **models**：描述「是什么」（User、Order 等数据结构）。
- **services**：描述「怎么做」（创建用户、计算订单金额）。
- **api/routers**：描述「对外暴露什么接口」（URL、HTTP 方法、状态码）。
- **utils**：与具体业务无关、可复用的纯函数。

---

## 三、本仓库标准目录

本仓库除练习目录外，预留了接近生产项目的骨架：

```
python-learning/
├── main.py                 # 当前入口脚本
├── README.md
├── requirements-advanced.txt   # 进阶示例依赖（FastAPI / Flask 等）
├── venv/                   # 本地虚拟环境
│
├── config/                 # 配置（环境变量、常量）
├── models/                 # 实体类 / ORM 模型
├── services/               # 业务逻辑
├── utils/                  # 通用工具
└── fileCenter/             # 本地文件存储（JSON、文本等读写示例数据）
```

| 本仓库目录 | 规划用途 |
|------------|----------|
| `config/` | 读取 `.env`、数据库 URL、日志级别等 |
| `models/` | 如 `User`、`Device` 等实体类或 ORM 定义 |
| `services/` | 如 `UserService.create_user()` 等业务方法 |
| `utils/` | 公共 helper，如 JSON 读写、时间处理 |
| `fileCenter/` | 存放运行时产生的本地文件（非代码） |

后续可按业务在 `models/`、`services/` 中补充代码，并在 `main.py` 或 Web 入口中组装调用。

---

## 四、环境准备

**运行环境：** Windows + Python 3.10+（建议 3.11 / 3.12）

### 1. 创建并激活虚拟环境

**Windows PowerShell（项目根目录）：**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

若执行策略限制脚本运行，可先执行：

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 2. 安装依赖

基础运行 `main.py` 暂无额外依赖。若需要 Web 相关能力，可安装进阶依赖：

```powershell
pip install -r requirements-advanced.txt
```

`requirements-advanced.txt` 当前包含：`fastapi`、`uvicorn`、`flask`。

---

## 五、如何启动

### 方式一：运行主入口（当前默认）

**Windows PowerShell（项目根目录，已激活 venv）：**

```powershell
python main.py
```

`main.py` 为项目启动脚本，负责组装并执行业务流程。

### 方式二：以模块方式运行（项目变大后推荐）

当包结构完善、存在 `__init__.py` 后，可从项目根目录：

```powershell
python -m main
```

或 Web 项目常见写法：

```powershell
# FastAPI + uvicorn 示例（假设入口为 app.main:app）
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

```powershell
# Flask 示例
$env:FLASK_APP = "app.main"
flask run
```

---

## 六、扩展建议

按标准架构演进时，可参考以下顺序：

1. 在 `models/` 定义实体，在 `schemas/`（可选）定义 API 数据结构。
2. 在 `services/` 实现业务，保持函数/类**不依赖** FastAPI Request 等框架对象。
3. 新增 `api/` 或 `routers/`，只做参数解析与响应封装。
4. 在 `config/` 集中管理配置，敏感信息放 `.env`。
5. 在 `tests/` 为 `services/` 编写单元测试。

这样练习代码与「可上线的项目结构」可以并行存在：练习放练习目录，正式代码走 `models` → `services` → `main` / `api` 分层。

---

## 七、常用命令速查

| 操作 | 命令（PowerShell，项目根目录） |
|------|--------------------------------|
| 激活虚拟环境 | `.\venv\Scripts\Activate.ps1` |
| 安装依赖 | `pip install -r requirements-advanced.txt` |
| 运行入口 | `python main.py` |
| 导出依赖 | `pip freeze > requirements.txt` |
| 运行测试 | `pytest`（需先 `pip install pytest` 并编写 `tests/`） |

## 八、python项目常用依赖、核心 API 与 Router 清单

### 1）核心依赖及作用（本项目）

| 依赖 | 主要作用 | 项目内高频 API |
|------|----------|----------------|
| `fastapi` | 提供 Web API 框架与路由机制 | `FastAPI()`、`APIRouter()`、`@router.get()`、`@router.post()`、`@router.put()`、`Depends()` |
| `pydantic` | 请求参数校验、响应结构约束、ORM 对象转响应模型 | `BaseModel`、`ConfigDict(from_attributes=True)`、`model_validate()`、`model_dump(exclude_unset=True)` |
| `sqlalchemy` | ORM 查询与事务管理 | `Session`、`db.query()`、`filter()`、`first()`、`all()`、`commit()`、`refresh()`、`rollback()`、`joinedload()` |
| `uvicorn` | FastAPI ASGI 服务启动（开发常用） | `uvicorn app:app --reload`（命令行启动） |

### 2）Router 常用 API（FastAPI）

- 路由对象：`APIRouter(prefix=..., tags=[...])`
- 依赖注入：`Depends(get_db)`、`Depends(oauth2_scheme)`
- 路由装饰器：`@router.get()`、`@router.post()`、`@router.put()`
- 响应模型：`response_model=UserResponse`、`response_model=list[UserResponse]`
- 路径参数：`"/{user_id}"` + 函数参数 `user_id: int`

### 3）当前项目 Router 接口清单

| 文件 | 接口 | 方法 | 说明 |
|------|------|------|------|
| `routers/user_router.py` | `/users/list` | GET | 查询用户列表 |
| `routers/user_router.py` | `/users/create` | POST | 创建用户 |
| `routers/user_router.py` | `/users/{user_id}` | GET | 按 ID 查询用户 |
| `routers/user_router.py` | `/users/{user_id}` | PUT | 按 ID 更新用户 |
| `routers/auth_router.py` | `/auth/token-test` | GET | 验证并返回 token |# python-learning
