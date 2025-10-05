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

    @keyword("Remove String")
    def remove_string(self, original, to_remove):
        """Removes a substring from the original string."""
        return original.replace(to_remove, "")

    @keyword("Round")
    def round_number(self, number, digits=0):
        """Rounds a number to the specified number of digits."""
        return round(float(number), int(digits))

