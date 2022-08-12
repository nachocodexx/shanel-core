import sys
import logging

def create_logger(**kwargs):
    name        = kwargs.get("name","default")
    LOG_PATH    = kwargs.get("LOG_PATH")
    NODE_ID     = kwargs.get("NODE_ID")
    # 
    FORMAT      = '%(asctime)s,%(msecs)s,%(levelname)s,%(threadName)s,%(message)s'
    formatter   = logging.Formatter(FORMAT,"%Y-%m-%d,%H:%M:%S")
    # 
    filename      = "{}/{}.csv".format(LOG_PATH,NODE_ID)
    errorFilename = "{}/{}-error.log".format(LOG_PATH,NODE_ID)
    # 
    # 
    logger      = logging.getLogger(name)
    # ___________________________________
    consolehanlder =logging.StreamHandler(sys.stdout)
    consolehanlder.setLevel(logging.DEBUG)
    consolehanlder.setFormatter(formatter)
    # 
    filehandler = logging.FileHandler(filename= filename)
    filehandler.setFormatter(formatter)
    filehandler.setLevel(logging.INFO)
    filehandler.addFilter(lambda record: record.levelno == logging.INFO)
    # 
    errorFilehandler = logging.FileHandler(filename=errorFilename)
    errorFilehandler.setFormatter(formatter)
    errorFilehandler.setLevel(logging.ERROR)
    errorFilehandler.addFilter(lambda record: record.levelno == logging.ERROR)
    # 
    logger.addHandler(filehandler)
    logger.addHandler(consolehanlder)
    logger.addHandler(errorFilehandler)
    # 
    logger.setLevel(logging.DEBUG)
    # 
    return logger