from loguru import logger
import sys

# 移除默认的日志处理器
logger.remove()

# 添加自定义的日志处理器
logger.add(
    "logs/code_search_{time:YYYY-MM-DD}.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO",
    encoding="utf-8",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)

# 添加控制台输出
logger.add(
    sys.stderr,
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"
)

def get_logger():
    return logger