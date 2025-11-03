import logging

from numpy.distutils.lib2def import output_def
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn
import os


class CommonKeywords:
    def __init__(self):
        logging.basicConfig(filename='robot_custom.log', level=logging.INFO, format='%(asctime)s %(message)s')
        self.selib = BuiltIn().get_library_instance("SeleniumLibrary")

    @keyword("Format Arguments")
    def format(self, arg1, arg2):
        """An example keyword that takes two arguments."""
        return arg1.format(arg2)

    @keyword("Log Message")
    def log_message(self, *message):
        logging.info(*message)  # Logs to file
        BuiltIn().log_to_console(*message)

    @keyword("Round")
    def round_number(self, number, digits=0):
        """Rounds a number to the specified number of digits."""
        return round(float(number), int(digits))


    @keyword("Capture Unique Screenshot")
    def capture_unique_screenshot(self, base_name="screenshot", full_page=True):
        """
        Capture a screenshot with correct window size.
        - Creates per-test folders.
        - Adds '.png' only if not present.
        - Optionally captures the full page (not just viewport).
        """
        builtin = BuiltIn()
        output_dir = builtin.get_variable_value("${OUTPUT DIR}")
        test_name = builtin.get_variable_value("${TEST NAME}").strip()
        testname_dir = os.path.join(output_dir, test_name)
        os.makedirs(testname_dir, exist_ok=True)
        screenshot_dir = os.path.join(str(testname_dir), "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        driver = self.selib.driver


        # Handle extension
        base, ext = os.path.splitext(base_name)
        if not ext:
            ext = ".png"

        file_path = os.path.join(screenshot_dir, f"{base}{ext}")
        index = 0
        while os.path.exists(file_path):
            index += 1
            file_path = os.path.join(screenshot_dir, f"{base}{index}{ext}")

        # ✅ Maximize or resize browser before capturing
        try:
            driver.maximize_window()
        except Exception:
            driver.set_window_size(1920, 1080)

        # ✅ Optionally capture full page
        if full_page:
            total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
            driver.set_window_size(1920, total_height)
            driver.save_screenshot(file_path)
        else:
            driver.save_screenshot(file_path)

        # builtin.log_to_console(f"📸 Saved screenshot: {file_path}")
        self.selib.capture_page_screenshot(file_path)
        return file_path
