import logging
import os

from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn


class CommonKeywords:
    def __init__(self):
        logging.basicConfig(filename='robot_custom.log', level=logging.INFO, format='%(asctime)s %(message)s')
        self.builtin = BuiltIn()
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

    @keyword("Set Custom Screenshot Directory For Current Test")
    def set_custom_screenshot_directory_for_current_test(self):
        """Set SeleniumLibrary screenshot directory to match our custom folder structure."""
        output_dir = self.builtin.get_variable_value("${OUTPUT DIR}")
        test_name = self.builtin.get_variable_value("${TEST NAME}").strip()
        test_name_dir = os.path.join(output_dir, test_name)
        screenshot_dir = os.path.join(str(test_name_dir), "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)

        # Tell SeleniumLibrary to use this directory for automatic/failure screenshots
        self.selib.set_screenshot_directory(screenshot_dir)
        self.builtin.log_to_console(f"📁 Screenshot directory set to: {screenshot_dir}")
        return screenshot_dir

    @keyword("Capture Unique Screenshot")
    def capture_unique_screenshot(self, base_name="screenshot", full_page=False):
        """
        Capture a full-page screenshot, save it, and embed it inside a
        scrollable HTML container in the log.
        """


        if isinstance(full_page, str):
            full_page = full_page.lower() == 'true'


        # 1. --- Determine File Paths and Create Directories ---
        # output_dir = self.builtin.get_variable_value("${OUTPUT DIR}")
        # test_name = self.builtin.get_variable_value("${TEST NAME}").strip()
        # test_name_dir = os.path.join(output_dir, test_name)
        screenshot_dir = self.set_custom_screenshot_directory_for_current_test()
        # (
        #     self.set_custom_screenshot_directory_for_current_test())
        os.makedirs(screenshot_dir, exist_ok=True)

        driver = self.selib.driver

        # Handle unique file name... (rest of your file path logic)
        base, ext = os.path.splitext(base_name)
        if not ext:
            ext = ".png"

        file_name = f"{base}{ext}"
        index = 0
        while os.path.exists(os.path.join(screenshot_dir, file_name)):
            index += 1
            file_name = f"{base}{index}{ext}"

        file_path = os.path.join(screenshot_dir, file_name)

        # 2. --- Handle Full Page Capture & Save to Disk ---

        if full_page:
            total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
            total_width =  driver.execute_script("return window.innerWidth")
            driver.set_window_size(total_width, total_height)
            self.builtin.log_to_console(f"Set window size to: {total_width}x{total_height} for full page screenshot.")

        # Capture and save the screenshot to the determined file path
        driver.save_screenshot(file_path)


        # 3. --- EMBED Screenshot in Log (Scrollable Base64) ---
        # B. Get the screenshot data as Base64 string
        base64_data = driver.get_screenshot_as_base64()
        if full_page:
            # Restore original window size after full page capture
            driver.maximize_window()

        # C. Log the image data using a SCROLLABLE HTML DIV
        # The image is displayed at its actual size within the fixed-size container.
        log_message = (
            f'<p><a href="file:///{file_path}" target="_blank">Saved Screenshot: {file_name}</a></p>'
            # Container DIV: Fixed height and width, with a scrollbar
            # f'<div style="width: 75%; height: 100%; overflow: scroll; border: 1px solid #ccc;">'
            # Embedded Image: Displayed at full width (100% of the DIV's width)
            f'<img src="data:image/png;base64,{base64_data}" style="width: 100%; height: auto;" />'
            f'</div>'
        )
        #
        self.builtin.log(log_message, html=True)

        # 4. --- Log and Return ---
        self.builtin.log_to_console(f"📸 Saved and Embedded (Scrollable) screenshot: {file_path}")
        return file_path