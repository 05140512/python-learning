# 第 4 课 · 数据迁移实战：读一份真实上线脚本（AFIHS-24 权限拆分）

> 对应《学习规划》主线 **B. 数据库工程化 → 迁移**。
> 目标不是背 PostgreSQL 语法，而是学会**「安全地改一个已经上线、带着真实数据的库」**——这份功力任意数据库通用。
> 教材是一份**真实生产迁移脚本**：OneForma 后端 `CommonServiceUserAPI/sql/feature/AFIHS-24/AFIHS-24_client_permission_split.sql`。

---

## 一、这节课要拿走的 8 个概念

真正做迁移，靠的就是这 8 个（都能在下面的脚本里指出对应行）：

1. **事务（Transaction）**——要么全成功，要么全回滚
2. **匿名过程块 `DO $$`**——PostgreSQL 里跑一段带逻辑的 SQL（⚠️ 方言）
3. **幂等（Idempotent）**——同一脚本重复跑，结果一样、不炸
4. **冲突守卫（Fail-loud）**——分清「自己重跑」和「别人占了我的坑」
5. **old → new 数据迁移**——把已存在的数据搬到新结构
6. **软删除 vs 物理删除**——上线数据一般软删留痕
7. **回滚脚本（down）**——每个 up 都配一个 down
8. **id 分配 / 环境漂移**——硬编码主键在多环境下的坑

---

## 二、背景：这次迁移在干嘛（一句话）

原来「客户端设置」只有一套粗权限 `um:client-setting` / `:read` / `:write`；
现在要**按能力拆细**成 6 个，挂到一个新菜单节点下：

| 旧（要退休） | 新（要上线） |
|---|---|
| `um:client-setting`（菜单，id 21200） | `um:client_task_platform`（菜单，21210） |
| `um:client-setting:read`（21201） | `:read`(21211)、`domain_blacklist:read`(21214) |
| `um:client-setting:write`（21202） | `:add`(21212)、`:manage`(21213)、`domain_blacklist:write`(21215) |

难点在于：**QA / prestg 环境已经上线过旧的那套（库里有 21200-21202 的数据），但 dev 库没有。** 同一个脚本要在两种起始状态下都跑对。这正是「上线迁移」比「写查询」难的地方。

---

## 三、逐行反推「为什么这么写」

### 3.1 最外层：`BEGIN; … COMMIT;` —— 事务（✅ 通用，所有库都有）

```sql
BEGIN;
    -- ... 一堆增删改 ...
COMMIT;
```

**为什么**：迁移会改很多行，中途要是断电/报错，绝不能「改了一半」。事务保证**原子性**：要么整段成功 `COMMIT`，要么整段撤销。这是所有关系库的通用能力（ACID 的 A）。

### 3.2 `DO $$ … $$` + `DECLARE / EXCEPTION` —— 匿名过程块（⚠️ PostgreSQL 方言）

```sql
DO $$
    DECLARE
        error_message TEXT;
    BEGIN
        -- 逻辑
    EXCEPTION
        WHEN OTHERS THEN
            GET STACKED DIAGNOSTICS error_message = MESSAGE_TEXT;
            RAISE INFO 'transaction failed: %', error_message;
            ROLLBACK;
            RAISE;
    END $$;
```

- `DO` = 跑一段**匿名代码块**（不建存储过程，一次性执行）。
- `$$ … $$` = **美元引用**，PostgreSQL 特有的字符串定界法，好处是块内写单引号不用转义。
- `DECLARE / EXCEPTION WHEN OTHERS / RAISE` = PL/pgSQL 过程式语法。
- **为什么要套它**：主要图 `EXCEPTION` 能**捕获异常 → 打日志 → 回滚**。其实这次迁移全是普通增删改，不套也能跑；这里是沿用团队模板。
- 📌 小知识：PL/pgSQL 里 `EXCEPTION` 块本身有个特性——块内报错时 PostgreSQL **自动回滚**该块的改动，再执行你的处理逻辑。所以真正保命的是「自动回滚 + 外层事务」，那句显式 `ROLLBACK` 更多是求心安。

> **换库怎么写**：MySQL 没有 `DO $$`，要写存储过程 + `DELIMITER`；SQL Server 直接写批处理 + `TRY...CATCH`；Oracle 是 `BEGIN … END; /`。**概念都是「带异常处理的过程块」，只是语法不同。**

### 3.3 Section 0：冲突守卫 —— 幂等 ≠ 无脑跳过

```sql
IF EXISTS (
    SELECT 1 FROM um_permission
    WHERE id IN (21210, …, 21215)
      AND permission_code NOT IN ('um:client_task_platform', …)  -- 不是我们的 code
) THEN
    RAISE EXCEPTION 'AFIHS-24 aborted: id range 21210-21215 is used by other codes …';
END IF;
```

**为什么这么写**（本课重点）：主键 id 是硬编码的（21210…）。dev 分支多人并行合并，万一**别的功能抢先用了 21210** 做了另一个权限，如果我们只写 `INSERT … ON CONFLICT (id) DO NOTHING`，就会**静默跳过**——我们的权限没建成，但授权行还指向 21210（现在是别人的），结果**授错权、且没有任何报错**。

所以要**区分两种冲突**：
- id 存在 **且 code 相同** → 我自己重跑 → 放过（幂等，正常）
- id 存在 **但 code 不同** → 被别人占了 → `RAISE EXCEPTION` **中止部署**，让人来换 id

一句话：**「静默的坏功能」远比「响亮的部署失败」危险。** 守卫把前者变成后者。

### 3.4 Section 1：插入新权限 —— `ON CONFLICT (id) DO NOTHING`（幂等插入）

```sql
INSERT INTO um_permission (id, permission_code, …, parent_id, parent_permission_code)
VALUES
    (21210, 'um:client_task_platform', …, 20000, NULL),
    (21211, 'um:client_task_platform:read', …, 21210, NULL),
    (21212, 'um:client_task_platform:add', …, 21210, 'um:client_task_platform:read'),
    …
ON CONFLICT ("id") DO NOTHING;
```

- `ON CONFLICT (id) DO NOTHING` = **PostgreSQL 的 upsert**：主键撞了就跳过，不报错。这让脚本**能重复跑**（配合上面的守卫，重跑安全、撞车报错）。
- 顺带认识两种「父」：`parent_id` = 树结构（谁挂谁下面）；`parent_permission_code` = 依赖（勾 `:add` 自动带 `:read`）。**是两套语义，别混。**

> **换库**：MySQL 用 `INSERT … ON DUPLICATE KEY UPDATE`；SQL Server 用 `MERGE`。概念都叫 **upsert**。

### 3.5 Section 3/4：old → new 授权迁移（迁移的灵魂）

已经发给各角色的旧权限，要**平移到新权限**。手法很典型：

```sql
-- 旧 write(21202) 的角色 → 补 add/manage/write 三个新权限
INSERT INTO um_system_role_permission (permission_id, system_role_id)
SELECT p.new_id, r.system_role_id
FROM um_system_role_permission r
CROSS JOIN (VALUES (21212), (21213), (21215)) AS p(new_id)
WHERE r.permission_id = 21202
ON CONFLICT DO NOTHING;
```

拆开读：
- `WHERE r.permission_id = 21202` → 找出所有**拥有旧 write** 的角色。
- `CROSS JOIN (VALUES …)` → 让每个这样的角色**乘上** 3 个新权限 id（一变三）。
- `INSERT … SELECT` → 把结果批量插进授权表。
- **关键**：全程用 `SELECT` 从现有数据推导，而**不假设有多少角色**。所以：
  - QA/prestg（有旧数据）→ 真的搬一批过去 ✅
  - dev（没旧数据）→ `WHERE` 匹配 0 行 → 什么都不插（无害空转）✅

**一份脚本能通吃两种环境，靠的就是「以现有数据为条件」而不是写死。** 这是迁移最值得学的思路。

### 3.6 Section 5：删旧授权 + 软删旧权限

```sql
DELETE FROM um_system_role_permission WHERE permission_id IN (21200, 21201, 21202);
UPDATE um_permission
SET is_deleted = 1, deleted_time = CURRENT_TIMESTAMP, deleted_by = 'admin'
WHERE id IN (21200, 21201, 21202);
```

- 授权是关联数据，直接 `DELETE`。
- 旧权限本身**不物理删**，而是 `is_deleted = 1` **软删**——上线数据一般保留痕迹（可追溯、可回滚）。这也是 OneForma 全站约定（`is_deleted` 列）。

### 3.7 rollback 脚本 —— 每个 up 配 down

`AFIHS-24_client_permission_split_rollback.sql` 把上面反着做：恢复旧权限（`is_deleted=0`）、从新授权反推恢复旧授权、删掉新的。**没有 down 的迁移不敢上生产**——出事没法退。

---

## 四、跨数据库对照（呼应你的「任意库都能上手」）

| 概念 | PostgreSQL | MySQL | SQL Server |
|---|---|---|---|
| 事务 | `BEGIN…COMMIT` | 同（或 `START TRANSACTION`） | `BEGIN TRAN…COMMIT` |
| 过程块 | `DO $$…$$` | 存储过程 + `DELIMITER` | 批处理 + `TRY/CATCH` |
| upsert | `ON CONFLICT DO NOTHING/UPDATE` | `ON DUPLICATE KEY UPDATE` | `MERGE` |
| 自增主键 | `SERIAL` / `IDENTITY` | `AUTO_INCREMENT` | `IDENTITY` |
| 主动报错 | `RAISE EXCEPTION` | `SIGNAL SQLSTATE` | `THROW` / `RAISERROR` |
| 字符串拼接 | `\|\|` | `CONCAT()` | `+` |

**~80% 通用（事务/约束/索引/CRUD/JOIN），~20% 方言。** 概念学一次，方言当查手册。

---

## 五、👉 你来写（在本地 `python_learning` 库亲手复现）

在 pgAdmin → `python_learning` → Query Tool，按段执行。用一张玩具表复现整套迁移套路。

```sql
-- ===== 准备：建一张玩具权限表 =====
DROP TABLE IF EXISTS play_permission;
CREATE TABLE play_permission (
    id            int PRIMARY KEY,
    code          varchar(64) UNIQUE NOT NULL,
    is_deleted    int NOT NULL DEFAULT 0
);
INSERT INTO play_permission (id, code) VALUES
    (100, 'setting'), (101, 'setting:read'), (102, 'setting:write');
```

**任务 #1（幂等）**：写一条 `INSERT`，插入 `(110, 'task:read')`，要求**再跑第二遍不报错**。
（提示：`ON CONFLICT`）

**任务 #2（冲突守卫）**：先手动插入一个「捣乱」行 `(110, 'someone_else')`，再写一个 `DO $$ … IF EXISTS … RAISE EXCEPTION … $$`，要求：当 id=110 被**别的 code** 占用时**报错中止**。跑通后把捣乱行删掉再验证守卫会放过。

**任务 #3（old→new 迁移）**：把「拥有 `setting:write`(102) 的规则」平移——用 `INSERT … SELECT … CROSS JOIN (VALUES …)` 的写法，给一张 `play_role_perm(role_id, perm_id)` 里所有持有 102 的角色补上新权限 112、113。
（先自己造几行 `play_role_perm` 数据）

**任务 #4（软删）**：把旧的 100/101/102 用 `UPDATE … SET is_deleted=1` 软删，而不是 `DELETE`。

---

## 六、检验你听懂了（做完回答我）

1. 为什么 `INSERT … SELECT … WHERE permission_id = 21202` 这种写法，能让**同一个脚本**在「有旧数据的 QA」和「没旧数据的 dev」上都跑对？
2. `ON CONFLICT (id) DO NOTHING` 已经能防重复插了，为什么还要额外写 Section 0 的守卫？两者防的是**同一种**冲突吗？
3. 这次迁移改的是**数据**还是**表结构**？（DML 还是 DDL？）如果要改表结构、又不想让新旧代码在切换期炸，应该用什么策略？（提示：expand-contract）

<details>
<summary>参考答案（先自己想）</summary>

1. 因为每步都以 `SELECT`/`WHERE` **从现有数据推导**，不写死角色数量。有旧数据就搬，没有就匹配 0 行空转——环境自适应。
2. **不是同一种**。`ON CONFLICT DO NOTHING` 防的是「我自己重跑，id+code 都一样」；Section 0 守卫防的是「id 被**别的 code** 占了」——后者若只靠 DO NOTHING 会静默跳过、授错权。一个是幂等，一个是保护。
3. 改的是**数据（DML）**，不动表结构。改表结构要用 **expand-contract**：先加新列/新表（expand）、新旧并存双写、代码切到新的、最后再删旧（contract），避免切换期新旧代码互相踩。

</details>

---

## 七、下一步（衔接学习规划）

- 这节是**手写 SQL 迁移**。规划里 B 段还有 **Alembic**（Python 的迁移框架，`upgrade`/`downgrade`/`autogenerate`）——下一课可以拿这次的「拆权限」需求，用 Alembic 在你的 `python_learning` 库重做一遍，对比「手写 SQL」和「框架迁移」的差别。
- Docker / Nginx 按你的规划放到**主线收尾**再学，不影响现在。
