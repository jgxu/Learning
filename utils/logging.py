import logging
import os
import sys
from datetime import datetime

# 确保日志目录存在
LOG_DIR = "./logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 创建日志记录器
logger = logging.getLogger("language_learning")
logger.setLevel(logging.DEBUG)  # 设置为DEBUG级别，捕获所有日志
logger.propagate = False  # 防止日志传递到父记录器

# 清空现有的处理器（避免重复添加）
if logger.handlers:
    logger.handlers.clear()

# 创建控制台处理器
console_handler = logging.StreamHandler(sys.stdout)  # 明确指定输出到stdout
console_handler.setLevel(logging.INFO)

# 创建文件处理器
log_file = os.path.join(LOG_DIR, f"app_{datetime.now().strftime('%Y%m%d')}.log")
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

# 定义日志格式
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 添加处理器到记录器
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# 设置root logger的级别
logging.root.setLevel(logging.INFO)

# 导出日志记录器供其他模块使用
app_logger = logger

# 测试日志
app_logger.info("日志系统初始化完成")