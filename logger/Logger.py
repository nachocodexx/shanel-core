import sys
import logging

def create_logger(**kwargs):
    name          = kwargs.get("name","default")
    LOG_PATH      = kwargs.get("LOG_PATH")
    LOG_FILENAME  = kwargs.get("LOG_FILENAME")
    add_error_log = kwargs.get("add_error_log",True)
    # 
    FORMAT      = '%(asctime)s,%(msecs)s,%(levelname)s,%(threadName)s,%(message)s'
    formatter   = logging.Formatter(FORMAT,"%Y-%m-%d,%H:%M:%S")
    # 
    filename      = "{}/{}.csv".format(LOG_PATH,LOG_FILENAME)
    errorFilename = "{}/{}-error.log".format(LOG_PATH,LOG_FILENAME)
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
    if(add_error_log):
        errorFilehandler = logging.FileHandler(filename=errorFilename)
        errorFilehandler.setFormatter(formatter)
        errorFilehandler.setLevel(logging.ERROR)
        errorFilehandler.addFilter(lambda record: record.levelno == logging.ERROR)
        logger.addHandler(errorFilehandler)
    # 
    logger.addHandler(filehandler)
    logger.addHandler(consolehanlder)
    # 
    logger.setLevel(logging.DEBUG)
    # 
    return logger