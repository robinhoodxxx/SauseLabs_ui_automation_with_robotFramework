import os
import re
import sys
import shutil
import argparse
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime

from Configs.application import OUTPUT_DIR

from pathlib import Path

def get_project_root(markers="robot.options"):
    current = Path(__file__).resolve()
    for parent in current.parents:
        if any((parent / marker).exists() for marker in markers):
            return parent
    # fallback if nothing found
    return current.anchor  # e.g., C:\ or /



# -----------------------------
# 🕒 Utility: Create timestamp folder
# -----------------------------
def create_report_dir(base="Reports")->str:
    root = get_project_root()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(root / base, exist_ok=True)
    timestamp_dir = os.path.join(base, timestamp)
    return os.path.abspath(timestamp_dir)


# -----------------------------
# 🧩 Collect test names via dry run
# -----------------------------
def collect_test_names(args, timestamp_dir):
    print("🧩 Collecting test names via dry run (no actual execution)...")

    os.makedirs(timestamp_dir, exist_ok=True)
    dryrun_output = os.path.join(timestamp_dir, "dryrun_output.xml")

    cmd = [
         "robot",
        "-A", "robot.options",
        "--outputdir", timestamp_dir,
        "--output", dryrun_output,
        "--dryrun",
    ]

    if args.i:
        cmd += ["--include", args.i]
    cmd.append(args.tests)
    print(cmd)
    subprocess.run(cmd, check=True)
    if not os.path.exists(dryrun_output):
        raise FileNotFoundError(f"Dry run output not found at: {dryrun_output}")

    test_names = []
    tree = ET.parse(dryrun_output)
    root = tree.getroot()
    for test in root.iter("test"):
        name = test.get("name")
        if name:
            test_names.append(name)

    print(f"✅ Found {len(test_names)} test cases.")
    return test_names

# -----------------------------
# 🧱 Run tests serially
# -----------------------------
def run_tests_serial(args, timestamp_dir, test_names)->bool:
    print("🧱 Running tests serially...")

    # Iterate through each test
    for test_name in test_names:
        """Run a single test case and save results in its own folder."""
        print(f"▶️ Running test Started: {test_name}")

        # Prepare output directory
        test_out_dir = os.path.join(timestamp_dir, test_name.strip())

        # Construct the command
        cmd = [
            "robot",
            "-A", "robot.options",
            "--outputdir", test_out_dir,
            "--variable", f"OUTPUT DIR:{timestamp_dir}",
            "--test", test_name, args.tests
        ]

        print(f"▶️ Running test: {test_name}")
        print(cmd)

        # Execute the command and capture the result
        # We set check=False so that an exception is not raised on non-zero exit code.
        # We rely on the 'returncode' attribute instead.
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        # Check the return code
        if result.returncode != 0:
            print(f"❌ Test Failed: {test_name}")
            print(f"Robot output (stdout):\n{result.stdout}")
            print(f"Robot error (stderr):\n{result.stderr}")
            # If any test fails, immediately return False
            return False

    # If all tests completed successfully (loop finished)
    print("✅ All tests passed.")
    return True


# -----------------------------
# ⚡ Run tests in parallel (with pabot)
# -----------------------------
# ⚡ Run tests in parallel (with pabot)
# -----------------------------
def run_tests_parallel(args, timestamp_dir:str) -> bool:
    print(f"⚡ Running tests in parallel with {args.parallel} workers using pabot...")

    # --- Build pabot command ---
    cmd = [
        sys.executable, "-m", "pabot.pabot",
        "--processes", str(args.parallel),
        "--outputdir", timestamp_dir,
        "-A", "robot.options",
        "--testlevelsplit",
        "--artifactsinsubfolders",
        "--variable", f"OUTPUT DIR:{timestamp_dir}",
        "--verbose"
    ]

    # Include tag if user passed one
    if args.i:
        cmd += ["--include", args.i]

    # ✅ Add the test folder LAST (datasource)
    cmd.append(args.tests)
    print("Command to be executed:")
    print(cmd)

    # *** MODIFICATION START ***
    # Run the command, capturing stdout and stderr
    result = subprocess.run(
        cmd,
        capture_output=True,  # This captures stdout and stderr
        text=True  # Decodes output as text
    )

    # Move pabot contents to named folders
    move_pabot_contents_to_named_folders(timestamp_dir)


    # Check the return code and print the error if it failed
    if result.returncode not in (0, 1):
        print("\n❌ Pabot Execution Failed (Exit Code != 0 or 1)")
        print("--- Pabot STDOUT ---")
        print(result.stdout)
        print("--- Pabot STDERR ---")
        print(result.stderr)
        print("--------------------")
        raise subprocess.CalledProcessError(result.returncode, cmd, output=result.stdout, stderr=result.stderr)

    # Print normal output if successful for debugging
    if result.stdout:
        print("\n--- Pabot Output Summary ---")
        print(result.stdout)
        print("----------------------------")

    if result.returncode == 1:
        print("⚠️ Tests completed but some tests failed (Exit Code 1).")


    print_final_summary_from_xml(timestamp_dir)


    return result.returncode == 0



# -----------------------------
# 📊 Combine all outputs into single overall report
# -----------------------------
def combine_reports(timestamp_dir:str):
    print("\n📊 Combining all test outputs into a single overall report...")
    tests_dir = os.path.join(timestamp_dir, "tests")
    combined_output = os.path.join(timestamp_dir, "output.xml")

    # Collect individual test outputs
    output_files = []
    for root, _, files in os.walk(tests_dir):
        for f in files:
            if f == "output.xml":
                output_files.append(os.path.join(root, f))

    if not output_files:
        print("⚠️ No individual outputs found to combine.")
        return

    cmd = [
        sys.executable, "-m", "robot.rebot",
        "--outputdir", timestamp_dir,
        "--name", "Combined Report",
        "--output", combined_output,
    ] + output_files

    subprocess.run(cmd, check=True)
    print(f"✅ Combined report generated: {combined_output}")

# -----------------------------
# 📦 Copy latest + zip reports
# -----------------------------
def finalize_reports(timestamp_dir, reports_dir="Reports"):
    latest_dir = os.path.join(reports_dir, "latest")

    # remove unwanted duplicate folders (if any)
    for folder in ["screenshots"]:
        unwanted = os.path.join(timestamp_dir, folder)
        if os.path.exists(unwanted):
            shutil.rmtree(unwanted, ignore_errors=True)

    if os.path.exists(latest_dir):
        shutil.rmtree(latest_dir)
    shutil.copytree(timestamp_dir, latest_dir)

    zip_path = os.path.join(reports_dir, "report.zip")
    if os.path.exists(zip_path):
        os.remove(zip_path)
    shutil.make_archive(zip_path.replace(".zip", ""), 'zip', timestamp_dir)

    print(f"📁 Copied latest report: {latest_dir}")
    print(f"📦 Zipped report archive: {zip_path}")

# -----------------------------
# 🚀 Main entry point
# -----------------------------


def get_test_name_from_output(xml_path):
    try:
        tree = ET.parse(xml_path)
        # Finds the first <test> tag in the XML
        test_element = tree.getroot().find(".//test")
        if test_element is not None:
            # Gets the name attribute from the <test> tag
            raw_name = test_element.get("name", "Unknown_Test")

            # Sanitizes the name to be safe for a folder name (removes illegal chars)
            return raw_name.strip()
    except Exception as e:
        # Error handling if the XML is corrupt or not found
        return None


def  report_single_test(path):
    # xml_path= "Reports/20251103_182108/pabot_results/0/output.xml"
    output_dir = os.path.dirname(path)
    print(output_dir)
    cmd = [
        sys.executable, "-m", "robot.rebot",
        "--outputdir", output_dir,  # <-- Explicitly sets the output to the XML's directory
        path
    ]
    subprocess.run(cmd, check=False)


# Assuming get_test_name_from_output is defined and correctly imports ET
# ...

# -----------------------------
# 🔄 Move Pabot Contents to Pre-Created Test Name Folders
# -----------------------------
def move_pabot_contents_to_named_folders(timestamp_dir):
    print("\n🔄 Moving pabot artifacts to pre-created Test Case Name folders...")

    # Path where pabot stores intermediate results
    pabot_results_path = os.path.join(timestamp_dir, 'pabot_results')
    # Path to the parent folder where the named folders exist (e.g., 'testEvidences')
    target_parent_dir = os.path.dirname(pabot_results_path)

    if not os.path.isdir(pabot_results_path):
        print("⚠️ pabot_results directory not found. Skipping move.")
        return

    # Iterate through folders 0, 1, 2, etc.
    for folder_name in os.listdir(pabot_results_path):
        source_path = os.path.join(pabot_results_path, folder_name)

        if os.path.isdir(source_path) and folder_name.isdigit():  # Process only the numbered folders
            output_xml_path = os.path.join(source_path, "output.xml")


            if os.path.exists(output_xml_path):
                # 1. Get the sanitized test name
                test_name = get_test_name_from_output(output_xml_path)
                report_single_test(output_xml_path)

                if test_name and test_name != "Unknown_Test":
                    # 2. Define the destination path (the pre-created folder)
                    destination_path = os.path.join(target_parent_dir, test_name)

                    if os.path.isdir(destination_path):
                        print(f"   -> Moving contents of {folder_name} into {test_name}...")

                        try:
                            # 3. Iterate through every item in the numbered folder and move it
                            for item in os.listdir(source_path):
                                source_item = os.path.join(source_path, item)
                                destination_item = os.path.join(destination_path, item)

                                # Use shutil.move to move the file/folder
                                shutil.move(source_item, destination_item)

                            print(f"   -> Successfully moved contents to {test_name}.")

                            # 4. Clean up the now empty numbered folder
                            os.rmdir(source_path)

                        except Exception as e:
                            print(f"   -> ERROR moving contents to {test_name}: {e}")

                    else:
                        print(f"   -> Destination folder '{test_name}' not found at {destination_path}. Skipping.")
                else:
                    print(f"   -> Could not find valid test name in {folder_name}/output.xml. Skipping.")

    # Clean up the now empty pabot_results folder
    if os.path.exists(pabot_results_path):
        try:
            os.rmdir(pabot_results_path)  # Use rmdir for empty directory
            print(f"✅ Removed empty parent folder: {pabot_results_path}")
        except Exception as e:
            # If the folder is not empty (e.g., due to a failed move), use rmtree
            shutil.rmtree(pabot_results_path, ignore_errors=True)
            print(f"✅ Cleaned up pabot_results folder.")


def rerun_failed_tests(args, rerun_dir,robot_args=None) -> None:
    if robot_args is None:
        robot_args = []
    print("\n🔄 Rerunning failed tests...")


    output_xml_path = os.path.abspath(args.rerun_xml_path)
    # --- 1. DETERMINE SOURCE XML PATH (The Fix) ---

    # Check if the required XML file exists before proceeding
    if not os.path.exists(output_xml_path):
        print(f"\n❌ ERROR: Rerun XML file not found at: {output_xml_path}")
        print("   Please run a full suite first or check the path passed to -r.")
        return

    # --- 2. DEFINE OUTPUT DIRECTORY FOR RERUN RESULTS ---
    # rerun_dir = os.path.join(create_report_dir(OUTPUT_DIR) + "_rerun_failed")

    # --- 3. CONSTRUCT COMMAND ---

    is_parallel = hasattr(args, 'parallel') and args.parallel is not None and args.parallel > 1

    if is_parallel:
        runner_base = [sys.executable, "-m", "pabot.pabot"]
        runner_options = [
            "--processes", str(args.parallel),
            "--testlevelsplit",
            "--artifactsinsubfolders"
        ]
    else:
        runner_base = ["robot"]
        runner_options = []

    # Build the command list
    cmd = runner_base + runner_options

    cmd += [
        "-A", "robot.options",
        "--outputdir", rerun_dir,
        "--variable", f"OUTPUT DIR:{rerun_dir}",
        # Use the determined path for rerunfailed
        "--rerunfailed", output_xml_path
    ]

    # Add extra robot arguments
    cmd.extend(robot_args)

    # Add optional include tag
    if args.i:
        cmd += ["--include", args.i]

    # Add the test source path LAST (required by robot/pabot)
    cmd.append(str(args.tests))

    print("Rerun command:", [str(c) for c in cmd])

    # Execute the command
    subprocess.run(cmd, check=False)
    if is_parallel:
        move_pabot_contents_to_named_folders(rerun_dir)


    merge_rerun_results(output_xml_path, rerun_dir)



def merge_rerun_results(original_xml_path, rerun_dir):
    # 1. Define paths
    rerun_xml_path = os.path.join(rerun_dir, "output.xml")
    # merged_output_xml = "output.xml"

    # 2. Construct the rebot command
    merge_cmd = [
        "rebot",
        "--merge",
        "--outputdir", rerun_dir,
        original_xml_path,  # The original file with all results (Pass/Fail)
        rerun_xml_path,  # The rerun file with new results for Failures
    ]

    print("\n🔗 Merging original and rerun results...")
    print("Executing command:", " ".join(merge_cmd))

    # 3. Execute the merge
    try:
        subprocess.run(merge_cmd, check=False)
        print(f"✅ Results merged successfully! Report available in {rerun_dir}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during merging results: {e}")

    # return os.path.join(rerun_dir, merged_output_xml)


def print_final_summary_from_xml(timestamp_dir: str) -> None:
    """
    Parses the final output.xml file to print the overall execution summary
    (total, passed, failed counts) and a detailed list of all failed test cases
    with their exception messages.

    Args:
        :param timestamp_dir:
    """
    output_xml_path = os.path.join(timestamp_dir, "output.xml")
    if not os.path.exists(output_xml_path):
        print(f"❌ Error: Output file not found at: {output_xml_path}")
        return

    try:
        # 1. Parse the XML file
        tree = ET.parse(output_xml_path)
        root = tree.getroot()

        failed_tests = []
        total_count = 0
        passed_count = 0
        failed_count = 0

        # --- Extract Counts from Statistics (Reliable) ---
        # Find the statistics element that sums all tests (usually type="all")
        stats_element = root.find(".//statistics/total")
        if stats_element:
            for stat in stats_element.findall('stat'):
                if stat.attrib.get('type') == 'all':
                    # The content of the tag is often the descriptive text.
                    # We rely on the <stat> tags within <total> which *should* hold the final counts
                    # However, a robust approach is to iterate tests for 100% accuracy.
                    pass  # We will rely on iterating through test tags below for exact counts.

        # --- Extract Counts and Failures by Iterating Test Tags ---
        # Find all <test> elements
        for test_element in root.findall('.//test'):
            total_count += 1

            # Find the status child element
            status = test_element.find('status')

            if status is not None:
                status_value = status.get('status')
                test_name = test_element.get('name')

                if status_value == 'PASS':
                    passed_count += 1
                elif status_value == 'FAIL':
                    failed_count += 1

                    # Get the failure message (text content of the status tag)
                    message = status.text.strip() if status.text else "No error message provided."

                    failed_tests.append({
                        "name": test_name,
                        "message": message
                    })

        # --- Print Consolidated Summary in an '=' BOX with Semicolons ---

        # 1. Format the data string using semicolons
        data_line = f"Total Tests: {total_count}; Passed: {passed_count}; Failed: {failed_count}"
        title_line = " FINAL EXECUTION STATUS "

        print("\n==========================================================")
        print(title_line)
        print("==========================================================")
        print(f"📊 TEST SUMMARY: {data_line}")
        print("==========================================================")



        # --- Print Detailed Failure Report ---
        if failed_count > 0:
            print("\n⚠️ DETAILED FAILURE REPORT:")
            for failure in failed_tests:
                print("\n==============================")
                print(f"TEST_NAME:  {failure['name']}")

                # Show only the first 4 lines of the exception for console readability
                exception_snippet = '\n'.join(failure['message'].splitlines())

                print(f"Exception:{exception_snippet}")
        else:
            print("\n✅ All tests passed.")

        print("==============================\n")


    except ET.ParseError as e:
        print(f"\n❌ Error: Failed to parse output.xml. File may be corrupted or incomplete: {e}")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred during parsing: {e}")


def Runner(robot_args=""):
    parser = argparse.ArgumentParser(
        description="Robot Framework Test Runner with automatic mode detection (Rerun, Parallel, or Serial)."
    )

    # --- Defined Arguments ---
    parser.add_argument("--i", help="Tag to include (i.e., --include)", default=None)
    parser.add_argument("--tests", help="Tests directory or file path", default="Testcases")

    # Parallel Argument (for detection)
    parser.add_argument(

        "--parallel","--p",
        dest='parallel',
        type=int,
        const=4,  # Default 4 if -p is provided without a number
        nargs='?',  # Argument is optional
        default=None,  # Default None means serial mode is active
        help="Run tests in parallel (e.g., -p 4). Defaults to 4 workers."
    )

    # Rerun Argument (for detection)
    parser.add_argument(
        "--r",
        dest='rerun_xml_path',
        nargs="?",  # Makes the value optional
        const=os.path.join(OUTPUT_DIR, "latest", "output.xml"),  # If user types '--r' without a path, use this default path
        default=None,  # If user omits '--r' entirely, attribute is None
        help=f"Trigger rerun mode. Pass optional path to output.xml. Defaults to '."
    )    # --- Parse Known Arguments to capture extra Robot options ---
    # This allows us to capture arguments like --variable browser:chrome
    args,unknown_args = parser.parse_known_args()

    # Consolidate unknown arguments for passing directly to robot/pabot
    robot_args = unknown_args
    if robot_args:
        print(f"Detected extra Robot Framework arguments: {robot_args}")

    # --- Setup and Mode Detection ---
    reports_dir = OUTPUT_DIR
    timestamp_dir = create_report_dir(reports_dir)

    print("Actual test execution starting...\n")

    # Step 2: Execute based on mode detection
    print(args)
    # 1. RERUN MODE (Highest Priority)
    if hasattr(args, 'rerun_xml_path') and args.rerun_xml_path is not None:
        # args.rerun_xml_path will contain:
        # 1. The user-provided path (if they typed '--r path/to/xml')
        # 2. The const value (DEFAULT_RERUN_XML_PATH) (if they typed just '--r')
        # You'll need to pass the determined path to your execution function
        timestamp_dir = os.path.join(timestamp_dir + "_rerun_failed")
        rerun_failed_tests(args, timestamp_dir, robot_args)
        print(args)

    # 2. PARALLEL MODE
    elif args.parallel and args.parallel > 1:
        run_tests_parallel(args, timestamp_dir)

    # 3. SERIAL MODE (Default)
    else:
        # Step 1: Dry run to collect test names (if needed for serial execution logic)
        test_names = collect_test_names(args, timestamp_dir)
        run_tests_serial(args, timestamp_dir, test_names)

    print("Actual test execution Done...\n")
    finalize_reports(timestamp_dir, reports_dir)


    print("\n🎉 All done!")
if __name__ == "__main__":
    # -----------------------------
    # Example Usage from command line:
    #
    # 1. Serial Case:
    # python runner.py serial --i smoke_test --test "Login Test" --tests "MyTestFolder"
    #
    # 2. Parallel Case:
    # python runner.py parallel -p 4 --i smoke_test --tests "MyTestFolder"
    #
    # 3. Rerun Case:
    # python runner.py rerun -r Reports/previous/output.xml --tests "MyTestFolder"
    # -----------------------------
    Runner()


