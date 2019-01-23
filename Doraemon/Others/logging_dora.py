import logging


class Logger:
    def __init__(self, path, clevel=logging.DEBUG, Flevel=logging.DEBUG):
        self.path = path

        self.logger = logging.getLogger(path)
        self.logger.setLevel(logging.DEBUG)
        fmt = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
        # 设置CMD日志
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        sh.setLevel(clevel)  # 设置cmd记录的起始等级
        # 设置文件日志
        fh = logging.FileHandler(path, encoding="UTF-8")
        fh.setFormatter(fmt)
        fh.setLevel(Flevel)  # 设置文件记录的起始等级
        self.logger.addHandler(sh)
        self.logger.addHandler(fh)

    def debug(self, message):
        self.logger.debug("->%s; debug: %s" % (self.path, message))

    def info(self, message):
        self.logger.info("->%s; info: %s" % (self.path, message))

    def warning(self, message):
        self.logger.warning("->%s; warning: %s" % (self.path, message))

    def error(self, message):
        self.logger.error("->%s; error: %s" % (self.path, message))

    def critical(self, message):
        self.logger.critical("->%s; critical: %s" % (self.path, message))


if __name__ == '__main__':
    logyyx = Logger('sofa.log', logging.DEBUG, logging.DEBUG)
    logyyx.debug(u'一个debug信息')
    logyyx.info(u'一个info信息')
    logyyx.warning(u'一个warning信息')
    logyyx.error(u'一个error信息')
    logyyx.critical(u'一个致命critical信息')