"""异常处理与主动抛错练习示例。"""
# 使用场景有：

# 参数校验：用户名、手机号、金额、ID 不能为空或格式错误时主动抛错。
# 业务规则校验：余额不足、库存不足、无权限、订单状态不允许操作。
# 接口调用失败：第三方接口返回失败码时，主动抛出异常交给上层统一处理。
# 数据异常：数据库查不到关键数据，继续执行会导致更严重问题时主动中断。
# 封装工具函数：让调用方知道“这里失败了”，而不是返回一个模糊的 None。
def testTryExcept():
  """练习 try/except/finally 的基础流程。"""
  try:
    file = open('test.txt', 'r')
    print('1', file.read())
    file.close()
  except FileNotFoundError:
    print('File not found')
  except Exception as e:
    print('2', e)
  finally:
    print('3', 'finally')

def testError():
    """练习使用 raise 主动抛出业务异常。"""
    content = ''
    try:
      with open('test.txt', 'r') as file:
          content = file.read()
          if not content:
            raise Exception('练习：文件内容为空，主动触发 raise')
          print(content)
    except Exception as e:
      print('2', e)
    finally:
      print('3', 'finally')

testError()