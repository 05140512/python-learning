import os

# 项目根目录（当前文件在 2_advanced 下，所以向上一级就是项目根）
projectRoot = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fileBasePath = os.path.join(projectRoot, 'fileCenter')

if not os.path.exists(fileBasePath):
  os.makedirs(fileBasePath)

def getFilePath(fileName):
  """根据文件名拼接 fileCenter 内的完整路径。"""
  return os.path.join(fileBasePath, fileName)

def createFile(fileName, content):
  """创建文件并写入内容（覆盖写入）。"""
  filePath = getFilePath(fileName)
  with open(filePath, 'w', encoding='utf-8') as file: # 打开文件，w表示写入模式
    file.write(content) # 写入文件

def appendFileContent(fileName, content):
  """向已有文件末尾追加内容。"""
  filePath = getFilePath(fileName)
  with open(filePath, 'a', encoding='utf-8') as file: # 打开文件，a表示追加模式
    file.write(content) # 写入文件

def readFile(fileName):
  """读取并返回文件全部内容。"""
  filePath = getFilePath(fileName)
  with open(filePath, 'r', encoding='utf-8') as file: # 打开文件，r表示读取模式
    content = file.read() # 读取文件
    return content

def deleteFile(fileName, filePath):
  """删除指定路径下的指定文件。"""
  targetFilePath = os.path.join(filePath, fileName)
  if not os.path.exists(targetFilePath):
    raise FileNotFoundError(f'文件不存在：{targetFilePath}')
  os.remove(targetFilePath)

# createFile('test.txt', 'Hello, World!')
# print(readFile('test.txt'))

appendFileContent('test.txt', '追加内容\n')
print(readFile('test.txt'))

# deleteFile('test.txt', './')

def practiseReadPrintFile(fileName):
  content = readFile(fileName)
  print(content)

practiseReadPrintFile('test.txt')