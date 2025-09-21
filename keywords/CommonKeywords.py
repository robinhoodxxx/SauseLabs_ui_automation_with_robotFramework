import logging

from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn


class CommonKeywords:
    def __init__(self):
        logging.basicConfig(filename='robot_custom.log', level=logging.INFO, format='%(asctime)s %(message)s')

    @keyword("Format Arguments")
    def format(self, arg1, arg2):
        """An example keyword that takes two arguments."""
        return arg1.format(arg2)

    @keyword("Log Message")
    def log_message(self, *message):
        logging.info(*message)  # Logs to file
        BuiltIn().log_to_console(*message)

