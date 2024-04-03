import logging
from postgresql_integration_test.exceptions import InvalidLogLevel

COLOR_OKBLUE = "\033[94m"
COLOR_OKGREEN = "\033[92m"
COLOR_FAIL = "\033[91m"
COLOR_ENDC = "\033[0m"


class _Log:
    def __init__(self):
        logging.debug("magic")
        self.logger = logging.getLogger("postgresql-integration-test")
        self.logger.setLevel(logging.ERROR)

    def debug(self, msg):
        if self.logger:
            self.logger.debug(msg)

    def info(self, msg):
        if self.logger:
            self.logger.info(_colored(msg, COLOR_OKBLUE))

    def error(self, msg):
        if self.logger:
            self.logger.error(_colored(msg, COLOR_FAIL))

    def success(self, msg):
        if self.logger:
            self.logger.info(_colored(msg, COLOR_OKGREEN))

    def setlevel(self, log_level):
        if log_level == "INFO":
            self.logger.setLevel(logging.INFO)
        elif log_level == "DEBUG":
            self.logger.setLevel(logging.DEBUG)
        elif log_level == "ERROR":
            self.logger.setLevel(logging.ERROR)
        elif log_level == "WARN":
            self.logger.setLevel(logging.WARN)
        else:
            raise InvalidLogLevel


def _colored(msg, color):
    return f"{color}{msg}{COLOR_ENDC}"


logger = _Log()
