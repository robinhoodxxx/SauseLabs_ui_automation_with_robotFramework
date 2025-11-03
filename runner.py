import os
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
    os.makedirs(timestamp_dir, exist_ok=True)
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
def run_tests_serial(args, timestamp_dir, test_names):

    print("🧱 Running tests serially...")
    for test_name in test_names:
        """Run a single test case and save results in its own folder."""
        print(f"▶️ Running test Started: {test_name}")
        # safe_name = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in test_name)
        test_out_dir = os.path.join(timestamp_dir, test_name.strip())
        cmd = [
            "robot",
            "-A", "robot.options",
            "--outputdir", test_out_dir,
            "--variable", f"OUTPUT DIR:{timestamp_dir}",
            "--test", test_name, args.tests

        ]


        print(f"▶️ Running test: {test_name}")
        print(cmd)
        subprocess.run(cmd, shell=True)


# -----------------------------
# ⚡ Run tests in parallel (with pabot)
# -----------------------------
# ⚡ Run tests in parallel (with pabot)
# -----------------------------
def run_tests_parallel(args, timestamp_dir):
    print(f"⚡ Running tests in parallel with {args.parallel} workers using pabot...")

    # --- Build pabot command ---
    cmd = [
        sys.executable, "-m", "pabot.pabot",
        "--processes", str(args.parallel),
        "--outputdir", timestamp_dir,
        "-A", "robot.options",
        "--testlevelsplit",
        "--artifactsinsubfolders",
        "--variable", f"OUTPUT DIR:{timestamp_dir}"
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
    # *** MODIFICATION END ***

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


# -----------------------------
# 📊 Combine all outputs into single overall report
# -----------------------------
def combine_reports(timestamp_dir):
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
    for folder in ["screenshots", "videos"]:
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
def main():
    parser = argparse.ArgumentParser(description="Robot Framework Test Runner with per-test reports")
    parser.add_argument("--i", help="Tag to include", default=None)
    parser.add_argument(
        "--parallel",
        type=int,
        nargs="?",      # optional argument
        const=4,        # default 4 if provided without number
        default=None,   # means serial by default
        help="Run tests in parallel (default 4 workers if no number)"
    )
    parser.add_argument("--tests", help="Tests directory", default="Testcases")

    args = parser.parse_args()

    reports_dir = OUTPUT_DIR
    timestamp_dir = create_report_dir(reports_dir)

    # Step 1: Dry run to collect test names
    test_names = collect_test_names(args, timestamp_dir)
    print("Dry run complete. Collected test names:")


    print("Actual test execution starting...\n")
    # Step 2: Execute
    if args.parallel and args.parallel > 1:
        run_tests_parallel(args, timestamp_dir)
    else:
        run_tests_serial(args, timestamp_dir, test_names)

    print("Actual test execution Done...\n")


    # Step 3: Combine reports
    # combine_reports(timestamp_dir)

    # Step 4: Finalize
    # finalize_reports(timestamp_dir)

    print("\n🎉 All done!")

# -----------------------------
import xml.etree.ElementTree as ET


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

if __name__ == "__main__":
    main()
