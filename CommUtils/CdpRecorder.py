import os
import base64
import subprocess
from selenium.webdriver.remote.webdriver import WebDriver


# --- Setup for Robot Framework ---
class CdpRecorder:
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self):
        self.driver = None
        self.frame_dir = None
        self.is_recording = False
        self.frame_counter = 0

    def start_cdp_screencast(self, output_dir, test_name):
        """Starts the CDP screencast and prepares to capture frames."""
        self.driver = self._get_selenium_driver()

        # 1. Create a temporary folder for raw frames
        self.frame_dir = os.path.join(output_dir, f"{test_name}_frames")
        os.makedirs(self.frame_dir, exist_ok=True)
        self.frame_counter = 0

        # 2. Define the callback function to handle incoming frames
        def frame_handler(event):
            if 'data' in event:
                frame_data = event['data']
                img_data = base64.b64decode(frame_data)

                # Save the frame as a sequential file (e.g., frame_00000.jpeg)
                frame_path = os.path.join(self.frame_dir, f"frame_{self.frame_counter:05d}.jpeg")
                with open(frame_path, 'wb') as f:
                    f.write(img_data)
                self.frame_counter += 1

                # Acknowledge the frame to continue receiving the next one
                self.driver.execute_cdp_cmd('Page.screencastFrameAck', {'sessionId': event['sessionId']})

        # 3. Add the listener and send the CDP command to start screencast
        self.driver.add_cdp_listener('Page.screencastFrame', frame_handler)
        self.driver.execute_cdp_cmd('Page.startScreencast', {'format': 'jpeg', 'quality': 75, 'everyNthFrame': 1})
        self.is_recording = True

    def stop_cdp_screencast_and_stitch_video(self, final_video_path):
        """Stops screencast, stitches frames, and cleans up."""
        if not self.is_recording:
            return

        # 1. Stop the CDP screencast command
        self.driver.execute_cdp_cmd('Page.stopScreencast', {})
        self.is_recording = False

        # 2. Use FFmpeg to stitch the frames into a video
        # NOTE: This command assumes sequential JPEG files and 15 FPS
        # You need to adjust the FPS based on your startScreencast settings
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',
            '-framerate', '15',
            '-i', os.path.join(self.frame_dir, 'frame_%05d.jpeg'),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2',  # Ensure dimensions are divisible by 2
            final_video_path
        ]

        try:
            subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg failed: {e.stderr.decode()}")

        # 3. Clean up the temporary frame directory
        # import shutil; shutil.rmtree(self.frame_dir)

        print(f"Video saved to: {final_video_path}")

    def _get_selenium_driver(self) -> WebDriver:
        # Helper to get the current driver instance from SeleniumLibrary
        try:
            from robot.libraries.BuiltIn import BuiltIn
            seleniumlib = BuiltIn().get_library_instance('SeleniumLibrary')
            return seleniumlib.driver
        except Exception as e:
            raise Exception(f"Could not get SeleniumLibrary driver instance: {e}")