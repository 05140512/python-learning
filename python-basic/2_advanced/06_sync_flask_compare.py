"""
同步 Flask 对比示例：与 05_fastapi_minimal.py 相同的业务，写法不同。

对比要点：
  - 路由是普通 def，IO 用 time.sleep 模拟「阻塞等待」。
  - 默认顺序执行两次 IO，总耗时约为两次相加（约 0.25s）。
  - 若也要并发 IO，同步世界常用线程池（见 get_user_detail_parallel）。

安装与 05 相同：pip install -r requirements-advanced.txt

启动（在 2_advanced 目录下）：
  python 06_sync_flask_compare.py

访问：
  http://127.0.0.1:5000/users/1
  http://127.0.0.1:5000/users/1/parallel
"""
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from flask import Flask, jsonify

# ---------------------------------------------------------------------------
# 模拟数据层（与 05 保持一致，便于对比）
# ---------------------------------------------------------------------------

FAKE_USERS: dict[int, dict[str, Any]] = {
  1: {'id': 1, 'name': '张三', 'role': 'admin'},
  2: {'id': 2, 'name': '李四', 'role': 'user'},
}

FAKE_PROFILES: dict[int, dict[str, Any]] = {
  1: {'user_id': 1, 'avatar': 'https://example.com/a.png', 'bio': '后端学习者'},
  2: {'user_id': 2, 'avatar': 'https://example.com/b.png', 'bio': 'Python 爱好者'},
}


def fetch_user_from_db(user_id: int) -> dict[str, Any]:
  """模拟同步数据库查询（阻塞当前工作线程）。"""
  time.sleep(0.15)
  user = FAKE_USERS.get(user_id)
  if user is None:
    raise ValueError(f'用户 {user_id} 不存在')
  return user


def fetch_profile_from_api(user_id: int) -> dict[str, Any]:
  """模拟同步 HTTP 调用（阻塞当前工作线程）。"""
  time.sleep(0.1)
  profile = FAKE_PROFILES.get(user_id)
  if profile is None:
    raise ValueError(f'用户 {user_id} 的资料不存在')
  return profile


def _error_response(message: str, status: int = 400):
  """将业务异常转为 HTTP 响应。"""
  return jsonify({'detail': message}), status


# ---------------------------------------------------------------------------
# Web 层
# ---------------------------------------------------------------------------

app = Flask(__name__)


@app.get('/users/<int:user_id>')
def get_user_detail(user_id: int):
  """
  顺序执行：简单直观，但两次 IO 等待会累加。
  生产环境常通过多 worker / 多线程进程扛并发，而不是单线程 async。
  """
  start = time.perf_counter()
  try:
    user = fetch_user_from_db(user_id)
    profile = fetch_profile_from_api(user_id)
  except ValueError as e:
    return _error_response(str(e), 404)

  elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
  return jsonify({
    'user': user,
    'profile': profile,
    'meta': {
      'mode': 'sync sequential (Flask)',
      'elapsed_ms': elapsed_ms,
    },
  })


@app.get('/users/<int:user_id>/parallel')
def get_user_detail_parallel(user_id: int):
  """
  同步世界里常见的 IO 并发手段：线程池。
  耗时接近 max(两次 IO)，但线程开销、调试复杂度高于单线程 async。
  """
  start = time.perf_counter()
  try:
    with ThreadPoolExecutor(max_workers=2) as pool:
      user_future = pool.submit(fetch_user_from_db, user_id)
      profile_future = pool.submit(fetch_profile_from_api, user_id)
      user = user_future.result()
      profile = profile_future.result()
  except ValueError as e:
    return _error_response(str(e), 404)

  elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
  return jsonify({
    'user': user,
    'profile': profile,
    'meta': {
      'mode': 'sync + ThreadPoolExecutor',
      'elapsed_ms': elapsed_ms,
    },
  })


if __name__ == '__main__':
  # debug=True 仅用于本地学习，生产请关闭
  app.run(host='127.0.0.1', port=5000, debug=True)
