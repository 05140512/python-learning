-- ============================================================
-- 第 2 课(收尾):覆盖索引 / Index Only Scan
-- 前置:先在终端跑 `venv\Scripts\python.exe -m scripts.seed_telemetry`
--       把 device_telemetry 灌到 30 万行(已含组合索引
--       idx_device_telemetry_device_id_metric_recorded_at)。
-- 运行方式:pgAdmin → python_learning → Query Tool,按 -- Section 逐段执行。
-- 标 [👉 你来写] 的先自己写,写完翻到文件底部「参考答案」核对。
-- ============================================================


-- ===== Section 0:先 VACUUM,后面才看得到 Index Only Scan(直接运行) =====
-- Index Only Scan 依赖「可见性图谱(visibility map)」判断某数据页里的行是否
-- 全部可见;只有可见,才敢「只读索引、不回表」。刚灌完数据没 VACUUM 时,
-- 图谱是空的,Heap Fetches 会很大,Index Only Scan 名存实亡。
VACUUM ANALYZE device_telemetry;


-- ===== Section 1:概念(读一遍,不用执行) =====
-- 回表(Heap Fetch):索引的叶子节点只存「索引列 + 指向数据行的指针」。
--   如果 SELECT 要的列不在索引里(比如 value),数据库得拿着指针再去
--   「表(堆 heap)」里把整行捞出来 —— 这一步就叫回表。行越多、越分散,越贵。
--
-- Index Only Scan(只走索引):如果一条查询「要的所有列」(SELECT + WHERE
--   + ORDER BY 用到的列)都能在索引里找到,数据库就不用回表,直接从索引
--   返回结果 —— 这就是「覆盖索引(covering index)」覆盖了这条查询。


-- ===== Section 2:回表长什么样 =====
-- [👉 你来写 #1]
-- 任务:用 EXPLAIN (ANALYZE, BUFFERS) 查 7 号设备 temperature 最近 30 天的 value,
--      按 recorded_at 排序。
-- 模板:
--   EXPLAIN (ANALYZE, BUFFERS)
--   SELECT value FROM device_telemetry
--   WHERE device_id = 7 AND metric = 'temperature'
--     AND recorded_at BETWEEN now() - interval '30 days' AND now()
--   ORDER BY recorded_at;
-- 执行后找这几个关键词:Bitmap Heap Scan、Heap Blocks=、Buffers: shared hit=、
--      最顶上是不是还有一个独立的 Sort 节点?记下 Buffers 的数字。




-- ===== Section 3:Index Only Scan 长什么样 =====
-- [👉 你来写 #2]
-- 任务:把上面那条 SQL 的 SELECT value 改成 SELECT recorded_at(只查索引里有的列),
--      其它不变,再跑一次 EXPLAIN (ANALYZE, BUFFERS)。
-- 对比:扫描方式变成了什么?有没有 "Heap Fetches: 0"?Buffers 的数字小了多少倍?
--      顶上那个独立 Sort 节点还在吗?(想想为什么)




-- ===== Section 4:用 INCLUDE 造覆盖索引,让回表的查询也免回表 =====
-- [👉 你来写 #3]
-- 任务:建一个「覆盖索引」,在原来 (device_id, metric, recorded_at) 的基础上,
--      用 INCLUDE 把 value 也塞进索引叶子。然后重跑 Section 2 那条 SELECT value。
-- 提示:
--   CREATE INDEX idx_dt_covering ON device_telemetry
--       (device_id, metric, recorded_at) INCLUDE (value);
-- 再跑一次 Section 2 的查询,观察:现在 SELECT value 是不是也变成 Index Only Scan、
--      Heap Fetches: 0 了?
--
-- 想一想:value 为什么放 INCLUDE,而不是写进索引键 (..., recorded_at, value)?




-- ===== Section 5:覆盖不了的情况 =====
-- [👉 你来写 #4]
-- 任务:把查询改成 SELECT *(要 created_at / is_deleted 等一堆列),再跑 EXPLAIN。
-- 猜一猜:还能走 Index Only Scan 吗?为什么?执行验证。




-- ============================================================
-- 参考答案(写完再看 ↓↓↓)
-- ============================================================
--
-- #1  SELECT value(value 不在索引里 → 回表):
--   EXPLAIN (ANALYZE, BUFFERS)
--   SELECT value FROM device_telemetry
--   WHERE device_id=7 AND metric='temperature'
--     AND recorded_at BETWEEN now()-interval '30 days' AND now()
--   ORDER BY recorded_at;
--   实测要点:
--     Bitmap Heap Scan ... Heap Blocks: exact=218
--     Buffers: shared hit=225          ← 碰了 225 个数据页
--     顶上还有一个独立的 Sort 节点      ← 见下方说明
--     cost ≈ 811
--
-- #2  SELECT recorded_at(列全在索引里 → Index Only Scan):
--   ...同上,只把 SELECT value 改成 SELECT recorded_at。
--   实测要点:
--     Index Only Scan using idx_device_telemetry_device_id_metric_recorded_at
--     Heap Fetches: 0                  ← 一次回表都没有
--     Buffers: shared hit=5            ← 从 225 页降到 5 页(~45 倍)
--     没有独立 Sort 节点               ← 索引本身按 recorded_at 有序,排序白送
--     cost ≈ 14.7(811 → 14.7,~55 倍)
--
-- #3  覆盖索引:
--   CREATE INDEX idx_dt_covering ON device_telemetry
--       (device_id, metric, recorded_at) INCLUDE (value);
--   VACUUM ANALYZE device_telemetry;   -- 新索引也要可见性图谱
--   再跑 #1 的 SELECT value:
--     Index Only Scan using idx_dt_covering
--     Heap Fetches: 0,Buffers ≈ 6,cost ≈ 14.5
--   → 原本要回表的 SELECT value,现在也不回表了。
--
--   为什么 value 放 INCLUDE 而不是写进键?
--     - 键列 (device_id, metric, recorded_at) 负责「定位 + 排序 + 最左匹配」。
--     - value 只是想「顺便带出来免回表」,它不参与查找和排序。
--     - 放进键会让索引更大、维护更贵,还可能影响排序语义;
--       INCLUDE 只在叶子附带存一份,职责清晰、代价更小。这就是 INCLUDE 的用途。
--
-- #4  SELECT *:
--   退回 Bitmap Heap Scan + 回表(和 #1 一样,cost ≈ 791)。
--   因为 SELECT * 要 created_at / updated_at / is_deleted... 这些列索引里没有,
--   覆盖不了 → 必须回表。
--   工程结论:别动不动 SELECT *;只取需要的列,才有机会吃到覆盖索引。
--
-- ★ 一个容易被忽略的红利:为什么 #1/#4 顶上有 Sort,而 #2/#3 没有?
--   #1/#4 走的是 Bitmap Heap Scan —— 它按「数据页物理顺序」捞行,丢了索引的有序性,
--   所以要 ORDER BY recorded_at 就得额外排一次序(那个独立 Sort 节点)。
--   Index Only Scan 是顺着索引 B-tree 走的,天然按 recorded_at 有序,
--   ORDER BY 直接满足,省掉 Sort。
--   → 覆盖索引省的不只是「回表的页」,有时还省掉「额外的排序」,双重收益。
