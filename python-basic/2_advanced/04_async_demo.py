import asyncio
import time
import random

async def task1():
  print('task1 start')
  await asyncio.sleep(3)
  print('task1 done')

async def task2():
  print('task2 start')
  await asyncio.sleep(2)
  print('task2 done')

async def task3():
  print('task3 start')
  await asyncio.sleep(1)
  print('task3 done')

async def main():
  start_time = time.time()
  await asyncio.gather(task1(), task2(), task3())
  end_time = time.time()
  print(f'total time: {end_time - start_time} seconds')


async def downloadFile():
  print('downloadFile start')
  await asyncio.sleep(5)
  print('downloadFile done')

async def testCreateTask():
  asyncio.create_task(downloadFile())
  print('主程序进行中...')

  for i in range(10):
    print(f'主程序进行中...{i}')
    await asyncio.sleep(1)

# ------------------------------------------------------------
# 开始模拟监听设备
# 用户操作中有个计数变量，每秒计数加1，每一秒打印一次用户操作了主程序，设备监听任务每2秒监听一次设备状态
# ------------------------------------------------------------
async def listenDevice():
  while True:
    print('设备状态变更')
    await asyncio.sleep(2)

# 模拟用户操作
async def user_operation():
    actions = [
        "打开首页",
        "查看设备列表",
        "修改系统配置",
        "查看日志",
        "刷新页面",
    ]

    for i in range(10):
        action = random.choice(actions)

        print(f"[用户操作] {action}")

        await asyncio.sleep(1)

async def userOperateMain():
  task = await asyncio.create_task(listenDevice())
  await user_operation()
  print("主程序结束")
  task.cancel()
  try:
    await task
  except asyncio.CancelledError:
    print("监听设备任务取消")

asyncio.run(userOperateMain())