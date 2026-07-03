-- ============================================================
-- 第 2 课:索引深入
-- 运行方式:pgAdmin 左侧右键 python_learning → Query Tool,
--          一段一段(按 -- Section 分隔)选中执行,观察输出。
-- 标 [👉 你来写] 的地方,先自己写,写完再翻到文件最底部「参考答案」核对。
-- ============================================================


-- ===== Section 1:造一张测试表 + 10 万行数据(样板,直接运行) =====
DROP TABLE IF EXISTS orders;

CREATE TABLE orders (
    id          BIGSERIAL PRIMARY KEY,          -- 自增主键(自动带主键索引)
    user_id     INTEGER       NOT NULL,         -- 下单用户
    status      VARCHAR(20)   NOT NULL,         -- 订单状态
    amount      NUMERIC(10,2) NOT NULL,         -- 金额
    created_at  TIMESTAMP     NOT NULL          -- 下单时间
);

-- generate_series(1, 100000): PostgreSQL 内置,生成 1~10万 序列,每个产生一行
INSERT INTO orders (user_id, status, amount, created_at)
SELECT
    (random() * 9999)::int + 1,
    (ARRAY['pending','paid','shipped','done','cancelled'])[(random()*4)::int + 1],
    (random() * 1000)::numeric(10,2),
    now() - ((random() * 365)::int || ' days')::interval
FROM generate_series(1, 100000);

SELECT count(*) FROM orders;   -- 应返回 100000


-- ===== Section 2:没有索引时按 user_id 查 =====
-- [👉 你来写 #1]
-- 任务:用 EXPLAIN ANALYZE 查询 user_id 等于 5000 的所有订单。
-- 提示:EXPLAIN ANALYZE <你的SELECT语句>;
-- 写在下面,执行后看输出里是 Seq Scan 还是 Index Scan,记下 actual time 的数字。




-- ===== Section 3:给 user_id 建索引 =====
-- [👉 你来写 #2]
-- 任务:在 orders 表的 user_id 列上创建一个普通索引,命名 idx_orders_user_id。
-- 提示:CREATE INDEX 索引名 ON 表名(列名);
-- 写在下面并执行。




-- ===== Section 4:加索引后再查一次,对比 =====
-- 重新执行你在 #1 写的那条 EXPLAIN ANALYZE。
-- 对比:扫描方式从 Seq Scan 变成了什么?actual time 变化多少倍?




-- ===== Section 5:组合索引 与「最左匹配原则」(本课重点) =====
-- 业务场景:经常按「状态 + 时间」查订单,例如查"已支付且最近下单的"。
--
-- [👉 你来写 #3]
-- 任务:创建一个组合索引,命名 idx_orders_status_created,
--      列顺序为 (status, created_at) —— 注意顺序很关键。
-- 提示:CREATE INDEX 索引名 ON 表名(列1, 列2);




-- [👉 你来写 #4] 验证最左匹配:下面 3 种查询,哪些能用上 idx_orders_status_created?
-- 分别写出 EXPLAIN ANALYZE,执行后观察是否出现 Index Scan / Bitmap Index Scan。
--
--   (a) 只按 status 查:           WHERE status = 'paid'
--   (b) 只按 created_at 查:       WHERE created_at > now() - interval '7 days'
--   (c) 同时按 status + created_at: WHERE status = 'paid' AND created_at > now() - interval '7 days'
--
-- 先猜哪个走索引、哪个不走,再用 EXPLAIN 验证你的猜测。写在下面:




-- ============================================================
-- 参考答案(写完再看 ↓↓↓)
-- ============================================================
--
-- #1:
--   EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 5000;
--   → 没索引时是 Seq Scan(全表扫描),actual time 较大。
--
-- #2:
--   CREATE INDEX idx_orders_user_id ON orders(user_id);
--
-- #4 再查:变成 Index Scan / Bitmap Index Scan,actual time 大幅下降(常见几十~几百倍)。
--
-- #3:
--   CREATE INDEX idx_orders_status_created ON orders(status, created_at);
--
-- #4 最左匹配结论(看 Bitmap Index Scan 的 cost,不是看"能不能用"):
--   (a) WHERE status='paid'                   → 用索引,index cost≈281   (命中最左列,高效)
--   (b) WHERE created_at > ...                → PostgreSQL 仍会用索引,但 cost≈1114(最贵!)
--                                               因为跳过了最左列,只能把"整棵索引"扫一遍再过滤
--   (c) WHERE status='paid' AND created_at>.. → 用索引,index cost≈9.6   (从最左列连续命中,最优)
--
--   关键纠正:最左匹配不是"给不给最左列就能不能查出结果"(结果永远对),
--   而是"能不能【高效】用上索引"。
--   组合索引 (A, B) 像电话簿按"姓+名"排序:
--     - 给"姓"或"姓+名" → 直接翻到那一页(高效,cost 低)
--     - 只给"名"        → 只能从头翻到尾(低效)。MySQL 此时多半直接放弃索引走全表;
--                          PostgreSQL 可能仍扫整棵索引(全索引扫描),但代价同样很高。
--   面试一句话答:组合索引只有包含最左列才能高效使用;只给非最左列用不上(或退化为低效扫描)。
