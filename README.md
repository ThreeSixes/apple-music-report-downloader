# Apple Muisc Report Downloader

## Background

This is a command-line utility designed to download reports from Apple Music and supports automatic JWT authentication. It currently only supports the `in-review` report, but can be extended to support other types of reports. When run the tool will write reports to the directory it was run in.

## Requirements

* [Pyenv](https://github.com/pyenv/pyenv) should be installed on the system downloading reports
* [Pipenv](https://pipenv.pypa.io/en/latest/) should be installed on the system downloading reports
* An Apple-provided `private key` file
* An Apple-provided `issuer ID`
* An Apple-provided `key ID`

## Installation process

Once Pyenv and Pipenv have been installed the follwoing commands can be run to perform the initial installation.
* Copy `config.json.dist` to `config.json` in this folder.
* Copy your Apple-provided `private key` file with a `p8` extension into this folder.
* Edit `config.json` and replace the example entries with the name of your `issuer ID`, `key ID`, and the name of your `private key`.
* `pyenv install 3.9.14`
* `pipenv shell`
* `pipenv install`

## Running the application

In order to run the application you'll first need to run a command to enter the Pipenv shell. This will only need to happen if it hasn't already been run since your shell was opened. If you're running the script immediately after installation you won't need to run it.

`pipenv shell`

To run the `in-review` report you will need to know the date that you're running the report for, and you will need to specify the date as an argument when you run the command to get the in-review report. The Apple API expects the date to be in the following format: `YYYY-MM-DD` where `YYYY` is the 4-digit year, `MM` is the two digit month, and `DD` is the two-digit day of the month. For this example we'll use `November 10th, 2022` as our target date. The command is as follows:

`./apple_report_downloader.py --get-in-review 2022-11-10`

If successful the program will exit without any terminal output and a file called `in-review-2022-11-10.tsv` will be written in the current folder containing the report from Apple in a tab separated value (TSV) format. The date of the file name will change with the specified date argument.

If the Apple API returns an HTTP error code an appropriate error message will be printed on the screen.

For a list of supported command line arguments run `./apple_report_downloader.py --help`.


## References

[Apple Music Analytics API endpoint descriptions](https://help.apple.com/itc/musicanalyticsapi/#/itc120a2ce63)
