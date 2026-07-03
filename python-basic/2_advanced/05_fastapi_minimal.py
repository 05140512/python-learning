"""
FastAPI 最小业务示例：对比 04_async_demo.py 的「裸 asyncio」写法。

业务场景（模拟）：
  GET /users/{user_id} 需要同时查「数据库用户」和「外部资料接口」，再合并返回。

与 04 的区别：
  - 不需要手写 asyncio.run / gather 搭全家桶；路由里 await 即可，并发用 asyncio.gather。
  - 事件循环、HTTP 解析、异常转 JSON 由 uvicorn + FastAPI 负责。

安装依赖（Windows PowerShell，在项目根目录）：
  .\\venv\\Scripts\\Activate.ps1
  pip install -r requirements-advanced.txt

启动（在 2_advanced 目录下）：
  python 05_fastapi_minimal.py

访问：
  http://127.0.0.1:8000/users/1
  http://127.0.0.1:8000/docs   （自动生成的接口文档）
"""
import asyncio
import time
from typing import Any

from fastapi import FastAPI, HTTPException

# ---------------------------------------------------------------------------
# 模拟数据层（真实项目会换成 asyncpg / SQLAlchemy async / httpx 等）
# ---------------------------------------------------------------------------

FAKE_USERS: dict[int, dict[str, Any]] = {
  1: {'id': 1, 'name': '张三', 'role': 'admin'},
  2: {'id': 2, 'name': '李四', 'role': 'user'},
}

FAKE_PROFILES: dict[int, dict[str, Any]] = {
  1: {'user_id': 1, 'avatar': 'https://example.com/a.png', 'bio': '后端学习者'},
  2: {'user_id': 2, 'avatar': 'https://example.com/b.png', 'bio': 'Python 爱好者'},
}


async def fetch_user_from_db(user_id: int) -> dict[str, Any]:
  """模拟异步数据库查询（真实环境：await session.execute(...)）。"""
  await asyncio.sleep(0.15)
  user = FAKE_USERS.get(user_id)
  if user is None:
    raise HTTPException(status_code=404, detail=f'用户 {user_id} 不存在')
  return user


async def fetch_profile_from_api(user_id: int) -> dict[str, Any]:
  """模拟异步 HTTP 调用外部服务（真实环境：async with httpx.AsyncClient()）。"""
  await asyncio.sleep(0.1)
  profile = FAKE_PROFILES.get(user_id)
  if profile is None:
    raise HTTPException(status_code=404, detail=f'用户 {user_id} 的资料不存在')
  return profile


# ---------------------------------------------------------------------------
# Web 层：框架接管请求生命周期
# ---------------------------------------------------------------------------

app = FastAPI(title='Python 学习 - FastAPI 异步示例')


@app.get('/users/{user_id}')
async def get_user_detail(user_id: int) -> dict[str, Any]:
  """
  业务路由：只写「要做什么」，并发 IO 用 gather，不自己 run 事件循环。
  """
  start = time.perf_counter()

  # 两个 IO 同时进行，总耗时约 max(0.15, 0.1) 秒，而不是相加
  user, profile = await asyncio.gather(
    fetch_user_from_db(user_id),
    fetch_profile_from_api(user_id),
  )

  elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
  return {
    'user': user,
    'profile': profile,
    'meta': {
      'mode': 'async (FastAPI + asyncio.gather)',
      'elapsed_ms': elapsed_ms,
    },
  }


if __name__ == '__main__':
  import uvicorn

  uvicorn.run(app, host='127.0.0.1', port=8000)
