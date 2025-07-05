import time
import json
from logging import getLogger
import atexit

logger = getLogger(__name__)

class TimeStampLogger:
    def __init__(self):
        self.log_id = 0
        self.log_dict = {}
        atexit.register(self.export_log)

    def logdecorator(self, func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            logger.info(f"{elapsed_time:.2f}s: {func.__name__}")
            self.log_id += 1
            self.log_dict[f"{func.__name__}_{self.log_id}"] = elapsed_time
            return result
        return wrapper
    
    def log_context(self, name):
        return _SyncTimerContext(self, name)
    
    def async_log_context(self, name):
        return _AsyncTimerContext(self, name)

    def export_log(self):
        with open("log.json", "w") as f:
            json.dump(self.log_dict, f, indent=4)
        return self.log_dict

class _SyncTimerContext:
    def __init__(self, parent_logger:TimeStampLogger, name):
        self.parent = parent_logger
        self.name = name

    def __enter__(self):
        self.start = time.time()
        self.parent.log_id += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start
        logger.info(f"{elapsed:.2f}s: {self.name}")
        self.parent.log_dict[f"{self.name}_{self.parent.log_id}"] = round(elapsed, 5)
    
class _AsyncTimerContext:
    def __init__(self, parent_logger:TimeStampLogger, name):
        self.parent = parent_logger
        self.name = name

    async def __aenter__(self):
        self.start = time.time()
        self.parent.log_id += 1
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start
        logger.info(f"{elapsed:.2f}s: {self.name}")
        self.parent.log_dict[f"{self.name}_{self.parent.log_id}"] = round(elapsed, 5)


timestamp_logger = TimeStampLogger()