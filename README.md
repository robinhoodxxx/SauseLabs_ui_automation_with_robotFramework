# Sauce Labs UI Automation with Robot Framework

This project demonstrates how to integrate Robot Framework with Sauce Labs for cross-browser UI automation. By leveraging Sauce Labs' cloud infrastructure, this setup allows for scalable and parallel test execution across various browser and OS combinations.

## Table of Contents

* [Project Overview](#project-overview)
* [Prerequisites](#prerequisites)
* [Installation](#installation)
* [Project Structure](#project-structure)
* [Configuration](#configuration)
* [Running Tests](#running-tests)
* [Reporting](#reporting)
* [Contributing](#contributing)
* [License](#license)

## Project Overview

This repository provides a framework for automating UI tests using Robot Framework and executing them on Sauce Labs. It utilizes the SeleniumLibrary for browser interactions and the Sauce Visual plugin for visual testing.

## Prerequisites

Before getting started, ensure you have the following installed:

* [Python 3.10+](https://www.python.org/downloads/)
* [Robot Framework](https://robotframework.org/)
* [SeleniumLibrary](https://robotframework.org/SeleniumLibrary/)
* [Sauce Labs Visual Plugin](https://pypi.org/project/saucelabs-visual/)

## Installation

1. Clone this repository:

```bash
git clone https://github.com/robinhoodxxx/SauseLabs_ui_automation_with_robotFramework.git
cd SauseLabs_ui_automation_with_robotFramework
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Project Structure

```
SauseLabs_ui_automation_with_robotFramework/
├── Testcases/           # Contains test case files
├── keywords/            # Custom keywords
├── resources/           # Shared resources
├── requirements.txt     # Python dependencies
├── robot.options        # Robot Framework options
└── run.bat              # Windows batch script to run tests
```



## Running Tests

To execute tests, use the following command:

```bash
run.bat Testcases
```

This command runs tests on the specified browser, platform, and version, saving the results in the `results/` directory.

## Reporting

After test execution, Robot Framework generates reports and logs in the `results/` directory. These include:

* `report.html` – Overview of the test run
* `log.html` – Detailed execution log
* `output.xml` – Machine-readable output

For visual testing, Sauce Labs provides insights into visual diffs and session details.

## Contributing

Contributions are welcome! Please fork this repository, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License.
