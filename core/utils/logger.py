from datetime import datetime
from enum import Enum

class LogLevel(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3

    @classmethod
    def from_string(cls, level: str) -> LogLevel:
        try:
            return cls[level.upper()]
        except KeyError as e:
            Logger.error(f"[Logger] Invalid log level: {level}")
            raise e 

class Logger:
    _log_level: LogLevel = LogLevel.INFO

    @classmethod
    def log(cls, message: str, level: LogLevel = LogLevel.DEBUG):
        if level.value >= cls._log_level.value:
            timestamp = datetime.now().strftime("%Y.%m.%d %H:%M:%S")
            print(f"[{timestamp}] [{level.name}] {message}")
    
    @classmethod
    def info(cls, message: str):
        cls.log(message, LogLevel.INFO)

    @classmethod
    def warning(cls, message: str):
        cls.log(message, LogLevel.WARNING)
    
    @classmethod
    def error(cls, message: str):
        cls.log(message, LogLevel.ERROR)