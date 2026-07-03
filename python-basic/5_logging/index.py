import logging

logger = logging.getLogger(__name__) # 使用name，获取当前模块的logger，输出会自带当前模块名

logger.debug('这是调试信息')
logger.info('这是普通信息')
logger.warning('这是警告信息')
logger.error('这是错误信息')
logger.critical('这是严重错误信息')