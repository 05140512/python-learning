# 第 5 课 · 用 Alembic 重做「拆权限」迁移（手写 SQL vs 框架迁移）

> 对应《学习规划》主线 **B. 数据库工程化 → Alembic 迁移（init / upgrade / downgrade / 回滚 / 多环境）**。
> 承接 [lesson04](lesson04_数据迁移实战-AFIHS-24权限拆分.md)：那节读的是**手写 SQL** 上线脚本；这节用 **Alembic**（Python 的迁移框架）把同一个「拆权限」需求在你自己的 `python_learning` 库重做一遍，体会两者差别。

---

## 一、Alembic 是什么（前端类比）

**Alembic = 数据库结构/数据的版本控制，像 git，但管的是数据库。**

| Alembic | 类比 git | 类比前端 |
|---|---|---|
| 一个 migration 文件 | 一次 commit | 一次代码改动 |
| `upgrade()` / `downgrade()` | —— | redo / undo |
| `alembic upgrade head` | `git checkout 最新` | 应用到最新 |
| `alembic downgrade -1` | 回退一个 commit | 撤销上一步 |
| `alembic_version` 表 | `.git` 里的 HEAD | 记「当前到哪了」 |
| `alembic history` | `git log` | 改动历史 |

**核心差别 vs 手写 SQL**：手写脚本你得自己保证「别重复跑坏」（上节的 `ON CONFLICT` / 守卫）；Alembic 有一张 `alembic_version` 表记住**每个环境跑到哪个版本了**，同一个 migration **不会被跑第二遍**——幂等由框架兜底。

---

## 二、装 + 初始化

```bash
# 1. 装（顺手写进 requirements.txt）
venv\Scripts\pip install alembic
# 追加到 requirements.txt: alembic==1.13.*

# 2. 初始化（在项目根目录）。目录名用 database/migrations（你已有这个空目录）
venv\Scripts\alembic init database/migrations
```

`init` 会生成：

| 文件 | 作用 | 类比 |
|---|---|---|
| `alembic.ini` | 主配置（数据库连接串等） | `.gitconfig` |
| `database/migrations/env.py` | 每次迁移运行时的入口脚本 | 钩子/启动配置 |
| `database/migrations/versions/` | **一个个迁移文件放这里** | commits 目录 |
| `script.py.mako` | 迁移文件模板 | 脚手架模板 |

---

## 三、接上你的项目（改 2 处）

**① `alembic.ini`**：把写死的 url 删掉，改由 `env.py` 从你的 `core/config.py` 取（换库只改一处，符合你「任意库上手」原则）。

**② `database/migrations/env.py`**：让 Alembic 认识你的模型（autogenerate 要用），并接上连接串：

```python
# env.py 顶部加：
from core.config import DATABASE_URL
from database.base import Base
# 让所有模型注册到 Base.metadata（import 一次即可）
import models.permission, models.role, models.role_permission  # noqa

config.set_main_option("sqlalchemy.url", DATABASE_URL)
target_metadata = Base.metadata      # 原来是 None，改成这个
```

- `target_metadata = Base.metadata` 是让 **autogenerate**（自动对比模型和库、生成建表/加列迁移）能工作的关键。
- 我们这次是**纯数据迁移**（不改表结构），所以不用 autogenerate，手写 `upgrade/downgrade`。但接好它，下次改表结构就能用 `alembic revision --autogenerate`。

---

## 四、生成一个空迁移，手写内容

```bash
venv\Scripts\alembic revision -m "split client permission into fine-grained codes"
```

会在 `versions/` 生成一个 `xxxx_split_client_permission...py`，里面有空的 `upgrade()` / `downgrade()`。

### 关键设计：不硬编码 id，按 code 引用（对比 AFIHS-24！）

你的 `permissions.id` 是**自增**、`code` 是**唯一**。所以这次**根本不用像 AFIHS-24 那样写死 21210-21215**——那正是 lesson04 结尾说的「进阶最稳」写法：**新增让 id 自动分配，关联时按 `code` 子查询定位 id。** 于是 lesson04 里那个「id 被别人占了」的坑，在这种写法下**天然不存在**。

准备：先假设库里有旧数据（可先手动插 3 条）：

```sql
-- 在 pgAdmin 先造旧数据（模拟"已上线"）
INSERT INTO permissions (name, code, sort, is_deleted) VALUES
  ('Client Setting', 'setting', 0, false),
  ('View', 'setting:read', 1, false),
  ('Edit', 'setting:write', 2, false);
-- 再给某个角色(假设 role id=1)发上旧权限
INSERT INTO role_permissions (role_id, permission_id, is_deleted)
SELECT 1, id, false FROM permissions WHERE code IN ('setting','setting:read','setting:write');
```

### `upgrade()` —— 迁移逻辑（放进生成的迁移文件）

```python
from alembic import op

def upgrade() -> None:
    # 1. 插新权限（不写 id，让自增分配；父节点 parent_id 用 code 子查询回填）
    op.execute("""
        INSERT INTO permissions (name, code, parent_id, sort, is_deleted)
        VALUES ('Client Task Platform', 'task_platform', NULL, 0, false)
    """)
    op.execute("""
        INSERT INTO permissions (name, code, parent_id, sort, is_deleted)
        SELECT v.name, v.code,
               (SELECT id FROM permissions WHERE code = 'task_platform'),  -- 父节点
               v.sort, false
        FROM (VALUES
            ('Read',   'task_platform:read',    1),
            ('Add',    'task_platform:add',     2),
            ('Manage', 'task_platform:manage',  3),
            ('BL Read','domain_blacklist:read', 4),
            ('BL Write','domain_blacklist:write',5)
        ) AS v(name, code, sort)
    """)

    # 2. 迁移授权：持有旧 read 的角色 -> 两个新 read；持有旧 write -> add/manage/write
    op.execute("""
        INSERT INTO role_permissions (role_id, permission_id, is_deleted)
        SELECT rp.role_id, p.id, false
        FROM role_permissions rp
        JOIN permissions old ON old.id = rp.permission_id AND old.code = 'setting:read'
        JOIN permissions p   ON p.code IN ('task_platform:read','domain_blacklist:read')
        WHERE rp.is_deleted = false
    """)
    op.execute("""
        INSERT INTO role_permissions (role_id, permission_id, is_deleted)
        SELECT rp.role_id, p.id, false
        FROM role_permissions rp
        JOIN permissions old ON old.id = rp.permission_id AND old.code = 'setting:write'
        JOIN permissions p   ON p.code IN ('task_platform:add','task_platform:manage','domain_blacklist:write')
        WHERE rp.is_deleted = false
    """)

    # 3. 退休旧的：删旧授权 + 软删旧权限
    op.execute("""
        DELETE FROM role_permissions
        WHERE permission_id IN (SELECT id FROM permissions WHERE code IN ('setting','setting:read','setting:write'))
    """)
    op.execute("""
        UPDATE permissions SET is_deleted = true, deleted_at = now()
        WHERE code IN ('setting','setting:read','setting:write')
    """)
```

### `downgrade()` —— 反向（Alembic 强制你想清楚怎么退）

```python
def downgrade() -> None:
    # 1. 恢复旧权限
    op.execute("UPDATE permissions SET is_deleted = false, deleted_at = NULL WHERE code IN ('setting','setting:read','setting:write')")
    # 2. 从新授权反推恢复旧授权
    op.execute("""
        INSERT INTO role_permissions (role_id, permission_id, is_deleted)
        SELECT DISTINCT rp.role_id, (SELECT id FROM permissions WHERE code='setting:read'), false
        FROM role_permissions rp JOIN permissions p ON p.id=rp.permission_id
        WHERE p.code IN ('task_platform:read','domain_blacklist:read')
    """)
    op.execute("""
        INSERT INTO role_permissions (role_id, permission_id, is_deleted)
        SELECT DISTINCT rp.role_id, (SELECT id FROM permissions WHERE code='setting:write'), false
        FROM role_permissions rp JOIN permissions p ON p.id=rp.permission_id
        WHERE p.code IN ('task_platform:add','task_platform:manage','domain_blacklist:write')
    """)
    # 3. 删掉新的
    op.execute("DELETE FROM role_permissions WHERE permission_id IN (SELECT id FROM permissions WHERE code LIKE 'task_platform%' OR code LIKE 'domain_blacklist%')")
    op.execute("DELETE FROM permissions WHERE code LIKE 'task_platform%' OR code LIKE 'domain_blacklist%'")
```

---

## 五、跑起来

```bash
venv\Scripts\alembic upgrade head      # 应用：跑 upgrade()
venv\Scripts\alembic downgrade -1      # 回滚一版：跑 downgrade()
venv\Scripts\alembic current           # 看当前在哪个版本
venv\Scripts\alembic history           # 看历史
```

跑完去 pgAdmin 看两样东西：
1. `permissions` / `role_permissions` 表数据变了没。
2. 多出一张 **`alembic_version`** 表，里面存着当前版本号——这就是「每个环境知道自己跑到哪」的秘密。

---

## 六、手写 SQL（AFIHS-24） vs Alembic —— 本课的题眼

| 维度 | 手写 SQL（lesson04） | Alembic（本课） |
|---|---|---|
| **幂等/防重复** | 自己写 `ON CONFLICT` + 守卫 | 框架用 `alembic_version` 记录，**同版本不重跑** |
| **id 分配** | 硬编码 21210…，有撞车风险，要守卫 | 自增 + 按 `code` 引用，**天然免疫**撞车 |
| **多环境（dev/qa 起点不同）** | 靠「以现有数据为条件」的 SQL 自适应 | 每个环境自己的 `alembic_version` 记进度，天然隔离 |
| **回滚** | 手写一个独立 rollback 脚本 | `downgrade()` 和 `upgrade()` 写在同一文件，`downgrade -1` 即回退 |
| **改表结构** | 手写 DDL | `--autogenerate` 对比模型自动生成 |
| **适合场景** | DBA 直接在库上跑、跨团队协作的上线脚本 | 应用自带、随代码版本走的迁移 |

一句话：**两者不是谁取代谁**。企业里常见「应用内用 Alembic 管版本，重大上线由 DBA 审手写 SQL」。你两种都会，就通了。

---

## 七、👉 你来写

1. 按第二~四节，在 `python_learning` 库把 Alembic 装好、init、接上 `env.py`，生成这个迁移。
2. 造旧数据 → `alembic upgrade head` → 去表里确认：旧的软删了、新的建好了、role 1 的授权平移了。
3. `alembic downgrade -1` → 确认全恢复原状。
4. **进阶**：改一次模型（比如给 `Permission` 加个 `remark` 列），用 `alembic revision --autogenerate -m "add remark"` 看它**自动**生成的 `op.add_column`——体会 autogenerate 和手写数据迁移的分工。

## 八、检验你听懂了

1. 手写脚本要写 `ON CONFLICT DO NOTHING` 防重复跑，Alembic 为什么不用？它靠什么防？
2. 为什么这次迁移**不需要**像 AFIHS-24 那样写死 id、也不需要「id 撞车守卫」？（提示：自增 + 按 code 引用）
3. `upgrade()` 和 `downgrade()` 必须成对写，这跟 lesson04 里「每个 up 配 down」是不是一回事？Alembic 在这件事上帮你强制了什么？

<details>
<summary>参考答案</summary>

1. Alembic 有 `alembic_version` 表记录「这个库跑到哪个版本」，同一版本不会执行第二次，所以框架层面就不会重复跑，无需 `ON CONFLICT`。（但**数据迁移逻辑本身**仍要写得安全，因为 downgrade 后再 upgrade 会重跑一次。）
2. 因为 `permissions.id` 自增、`code` 唯一：新增让库自己分配 id，关联时按 `code` 子查询定位——不同环境 id 不同也没关系。AFIHS-24 硬编码 id 是为贴合 OneForma 既有约定，代价就是要防撞车。
3. 是同一回事（可回滚）。Alembic 把 `up/down` 放同一文件、并强制你实现 `downgrade()`，从工程上**逼你在写迁移时就想好怎么退**，比手写两个独立脚本更不容易漏掉 down。

</details>
