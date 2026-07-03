# Python + FastAPI + 数据库 + 工业软件职业转型学习上下文（持续版）

我是一个有 8 年经验的前端开发工程师。

当前技术栈：

* Vue3
* TypeScript
* Vite

职业转型目标：

```txt
前端开发
    ↓
全栈开发
    ↓
工业软件开发
    ↓
工业数据采集平台
    ↓
AI Agent 平台开发
```

最终目标不是成为传统 Java 后端工程师，而是成为：

```txt
工业软件工程师
+
AI工业平台工程师
```

未来规划路线：

```txt
Vue3
    ↓
Electron
    ↓
Python
    ↓
FastAPI
    ↓
SQLAlchemy
    ↓
SQLite/PostgreSQL
    ↓
数据库设计
    ↓
工业协议(Modbus TCP / MQTT / OPC UA)
    ↓
工业数据采集平台
    ↓
工业监控平台
    ↓
AI Agent平台
```

---

# 学习要求（必须遵守）

教学必须满足：

1. 使用真实企业项目结构
2. 说明代码放在哪个目录哪个文件
3. 说明 import 来源
4. 解释代码作用
5. 给完整代码
6. 不允许跳步骤
7. 不允许突然引入新概念
8. 必须保证上下文连续
9. 必须符合企业开发习惯

默认技术栈：

* FastAPI
* SQLAlchemy
* Pydantic
* SQLite

---

# 当前项目结构

```txt
project/

├── models
├── schemas
├── repositories
├── services
├── routers
├── dependencies
├── database
├── core
├── scripts
└── main.py
```

---

# 已掌握内容

## Python

已掌握：

```txt
基础语法
class
import
logging
try/except
模块化
包结构
```

---

## SQLite

已掌握：

```txt
CRUD

WHERE

LIKE

LEFT JOIN

GROUP BY

ORDER BY

COUNT

事务

索引基础概念

数据库设计
```

最近新增掌握：

```txt
IN

BETWEEN

HAVING

LIMIT

OFFSET
```

尚未深入：

```txt
EXPLAIN

执行计划

索引优化

联合索引

覆盖索引

回表

最左匹配原则
```

---

## SQLAlchemy

已掌握：

```txt
DeclarativeBase

Base.metadata.create_all

SessionLocal

relationship

ForeignKey

joinedload

CRUD

Repository模式
```

已掌握：

```txt
Repository返回ORM对象

Service返回ORM对象

Dependency返回ORM对象

Router负责response_model转换

Schema只用于请求响应
```

禁止：

```python
return UserResponse.model_validate(...)
```

出现在 Service 中。

---

## Pydantic

已掌握：

```txt
Create Schema

Update Schema

Response Schema

model_validate

model_dump

ConfigDict(from_attributes=True)
```

---

## FastAPI

已掌握：

```txt
Router

Depends

Dependency Injection

Service层

Repository层
```

---

## JWT认证

已掌握：

```txt
bcrypt

JWT

access_token

get_current_user
```

并且已解决：

```txt
JWT Subject must be a string
```

问题。

当前JWT实现正常。

---

# RBAC学习进度

已完成模型：

```txt
User

Role

Permission

UserRole

RolePermission
```

关系：

```txt
User
↓
UserRole
↓
Role
↓
RolePermission
↓
Permission
```

---

Permission支持树结构：

```txt
parent_id

parent

children
```

已理解：

```txt
remote_side
```

作用。

---

已完成：

```txt
RBAC初始化脚本

权限数据初始化

角色权限绑定

用户角色绑定
```

---

已完成：

```python
get_user_permissions_service()
```

权限获取链路：

```txt
User
↓
UserRole
↓
Role
↓
RolePermission
↓
Permission
↓
permission.code
```

---

已完成接口：

```http
GET /auth/permissions
```

返回：

```json
{
  "permissions": [
    "user:view",
    "user:create"
  ]
}
```

---

已完成：

```python
PermissionChecker
```

并且已经实现：

```txt
AND权限校验
```

接口级权限控制。

---

# 中间表CRUD学习进度

已完成：

## UserRole

```txt
用户绑定角色

用户解绑角色

恢复角色关系

软删除
```

已实现：

```python
assign_role_to_user()

remove_role_from_user()
```

---

## RolePermission

已完成：

```txt
角色绑定权限

角色解除权限

恢复权限关系

软删除
```

已实现：

```python
bind_role_permission()

unbind_role_permission()

restore_role_permission()
```

---

# 当前能力评估

已经能够：

```txt
看懂Repository

看懂Service

理解ORM关系

理解RBAC设计
```

但仍然不擅长：

```txt
从零独立手写业务CRUD
```

这是正常现象。

当前不需要大量练习CRUD。

因为：

```txt
CRUD会在项目实践中自然熟练

AI也可以辅助生成
```

---

# 当前学习重点（非常重要）

当前学习重心：

```txt
数据库能力
+
SQL能力
```

而不是：

```txt
业务CRUD
```

原因：

未来职业方向：

```txt
工业软件

工业数据平台

AI Agent平台
```

真正核心能力：

```txt
数据库设计

SQL优化

系统设计
```

而不是：

```txt
菜单权限

按钮权限

各种业务CRUD
```

---

# 当前数据库学习进度

已完成：

```txt
SELECT

INSERT

UPDATE

DELETE

WHERE

LIKE

IN

BETWEEN

ORDER BY

LEFT JOIN

GROUP BY

COUNT

HAVING

LIMIT

OFFSET
```

---

刚开始学习：

```txt
EXPLAIN
```

已经理解：

```txt
SCAN
=
全表扫描

USING INDEX
=
使用索引
```

---

# 接下来学习顺序（必须按顺序）

下一阶段重点：

```txt
EXPLAIN
    ↓
索引基础
    ↓
主键索引
    ↓
唯一索引
    ↓
普通索引
    ↓
SQLAlchemy创建索引
    ↓
联合索引
    ↓
执行计划分析
    ↓
真实SQL优化案例
```

---

然后：

```txt
Alembic
```

学习：

```txt
数据库迁移

升级

回滚

企业项目迁移流程
```

---

之后进入：

```txt
SQLAlchemy高级查询
```

包括：

```txt
INNER JOIN

子查询

exists

func

聚合统计

复杂查询
```

---

然后进入：

```txt
Electron
```

学习：

```txt
桌面客户端

本地数据库

文件系统

本地服务
```

---

然后进入：

```txt
MQTT

Modbus TCP

OPC UA
```

工业通信协议。

---

然后：

```txt
工业数据采集平台
```

---

最后：

```txt
AI Agent平台
```

---

# 教学原则

不要让我陷入：

```txt
业务CRUD细节

菜单权限细节

按钮权限细节
```

太久。

保持：

```txt
业务够用即可
```

优先投入时间：

```txt
数据库

SQL

索引

性能优化

Alembic

系统设计
```

因为这是未来工业软件和AI平台开发的长期核心能力。
