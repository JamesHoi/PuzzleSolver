import sys
import logging,datetime,traceback

## @detail 创建记录异常的信息
class ExceptHookHandler():
    def __init__(self):
        #self.__Logger = self.__BuildLogger()
        # 重定向异常捕获
        sys.excepthook = self.__HandleException

    ## @detail 创建logger类
    @classmethod
    def __BuildLogger(cls):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.FileHandler("log/"+cls.__name__+".txt"))
        return logger

    ## @detail 捕获及输出异常类
    #  @param excType: 异常类型
    #  @param excValue: 异常对象
    #  @param tb: 异常的trace back
    def __HandleException(self, excType, excValue, tb):
        # first logger
        '''
        try:
            currentTime = datetime.datetime.now()
            self.__Logger.info('Timestamp: %s' % (currentTime.strftime("%Y-%m-%d %H:%M:%S")))
            self.__Logger.error("Uncaught exception：", exc_info=(excType, excValue, tb))
            self.__Logger.info('\n')
        except:
            pass
        '''
        # then call the default handler
        sys.__excepthook__(excType, excValue, tb)

        err_msg = ''.join(traceback.format_exception(excType, excValue, tb))
        print(err_msg)