import logging

logger = logging.getLogger(__name__) # 使用name，获取当前模块的logger，输出会自带当前模块名

class DeviceManager:
    def connect(self, device):
        try:
            device.online = True
            logger.info(f"{device.name} connected")
        except Exception as e:
            logger.error(f"连接失败: {e}")