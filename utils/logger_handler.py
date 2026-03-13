import time
import logging
import os

from config.paths import BASE_DIR

class LoggerHandler:
    def __init__(self):

        daytime = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        path = BASE_DIR + '/log/'

        if not os.path.exists(path):
            os.mkdir(path)
        
        filename = path + f'/run_log_{daytime}.log'

        # 将路径保存为实例属性，以便 conftest.py 读取
        self.log_file_path = filename


        # 创建logger对象
        self.logger = logging.getLogger("log_name")

        # 设置logger全局级别
        # 如果这里不设置，下面Hander即便设置了也没有用，会被拦截
        self.logger.setLevel(logging.DEBUG)

        # 创建控制台处理器
        console_hander = logging.StreamHandler()
        # 设置控制台输出log级别
        console_hander.setLevel(logging.INFO)

        # 创建文件处理器
        file_hander = logging.FileHandler(filename)
        # 设置文件输出log级别
        file_hander.setLevel(logging.DEBUG)

        # 设置formatter - 定义输出格式
        file_format = logging.Formatter(
            fmt= '%(levelname)s | [%(asctime)s] | %(filename)s[line:%(lineno)d] | %(funcName)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        console_format = logging.Formatter(
            fmt= '%(levelname)s | [%(asctime)s] | %(filename)s[line:%(lineno)d] | %(funcName)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_hander.setFormatter(console_format)
        file_hander.setFormatter(file_format)

        # 防止日志重复打印
        # 因为 logging.getLogger 是单例的，每初始化一次会多打印一行，如果不小心初始化多次，会导致同样的信息打印多行
        if not self.logger.handlers:
            # 挂载处理器
            self.logger.addHandler(console_hander)
            self.logger.addHandler(file_hander)
    
    # 封装方法，使得外部能够直接调用info / debug等
    def info(self,msg):
        self.logger.info(msg)
    
    def debug(self,msg):
        self.logger.debug(msg)
    
    def error(self,msg):
        self.logger.error(msg)

    def warning(self,msg):
        self.logger.warning(msg)

# 单例实例化
logger = LoggerHandler()