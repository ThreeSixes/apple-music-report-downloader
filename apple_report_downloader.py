#!/usr/bin/env python3

""" Apple Music Report Downloader
This project is licensed under the GPLv3 licnse. A copy of the license should have been
included with the repository.

By ThreeSixes (https://github.com/ThreeSixes) 10 Nov, 2022
"""

from functools import lru_cache
import json
import os
from pprint import pprint

import jwt
import requests
import time


class Configurator:
    def __init__(self, config_file=None, args={}):
        """Configurator

        Args:
            config_file (str, optional): Name of a JSON-formatted config file to use. Defaults to None.
            args (dict, optional): Initial configuration options. Defaults to {}.
        """

        # Built-in defaults.
        self.__config = {
            "api_base_url": "https://musicanalytics.apple.com",
            "jwt_expire_sec": 1200
        }

        # Add any incoming arguments.
        self.__config.update(args)

        # Get a configuration file.
        self.__config_file = config_file

        # Default items expected by the configurator.
        self.__required_items = [
            "api_base_url",
            "issuer_id",
            "jwt_expire_sec",
            "key_id",
            "privkey_path"
        ]

        # Configure!
        self.__configure(args)


    def __configure(self, args):
        """Create a configuration from a variety of sources. Each source is overriden by the next.
        1) Defaults specified in the constructor
        2) JSON configuration file if specified
        3) Environment variables
        4) Arguments sent in

        Args:
            args (dict): Initially-specified arguments.

        Raises:
            KeyError: Indicates a missing mandatory config option.
        """

        # Load configuration from files.
        if self.__config_file is not None:
            self.__configure_from_file()

        # Configure from environment variables.
        self.__configure_from_env()

        # Add any incoming arguments.
        self.__config.update(args)

        # Validate that we have all our configuration.
        for item in self.__required_items:
            if item not in self.__config:
                raise KeyError(f"Missing configuration item: {item}")


    def __configure_from_env(self):
        """Load configuration from environment variables.
        """
        env_vars = os.environ

        # Search for any of our items in environment variables.
        for item in self.__required_items:
            item_upper = item.upper()

            # If we have a match use it.
            if item_upper in env_vars:
                self.__config.update({item: env_vars[item_upper]})


    def __configure_from_file(self):
        """Load configuration from a JSON file.
        """
        if self.__config_file is not None:
            with open(self.__config_file, "r") as f:
                contents = f.read()
                self.__config.update(json.loads(contents))


    @property
    def configuration(self):
        """A dictionary containing the configuration.
        """

        return self.__config


class AppleAPI:
    """Apple API
    """
    def __init__(self, privkey_path, key_id, issuer_id, jwt_expire_sec, api_base_url):
        """Apple API

        Args:
            privkey_path (str): Path to your private key.
            key_id (str): Apple key ID.
            issuer_id (bool): Apple issuer ID.
            jwt_expire_sec (int, optional): Seconds the JWT token is valid for.
            api_base_url (str): Apple API base URL.
        """

        # Set class-wide config items.
        self.__api_base_url = api_base_url
        self.__jwt_expire_sec = jwt_expire_sec
        self.__issuer_id = issuer_id
        self.__key_id = key_id
        self.__privkey_path = privkey_path


    def __send_http_request(self, verb, url, body=None, headers={}, verify_ssl=True):
        """Send an HTTP request.

        Args:
            verb (str): HTTP verb to use.
            url (str): URL to connect to.
            body (str, optional): HTTP requrest body. Defaults to None.
            headers (dict, optional): HTTP headers. Defaults to {}.
            verify_ssl (bool): Use this to disable SSL verification. Defaults to True.

        Returns:
            list: List containing the HTTP response code, headers and text.
        """

        # Request kwargs
        request_kwargs = {'verify': verify_ssl}

        # Did we get a body?
        if body is not None:
            request_kwargs.update({'body': body})

        # Did we get headers?
        if headers is not None:
            request_kwargs.update({'headers': headers})


        # Select our target HTTP verb
        if verb == "delete":
            r = requests.delete(url, **request_kwargs)

        elif verb == "get":
            r = requests.get(url, **request_kwargs)

        elif verb == "head":
            r = requests.head(url, **request_kwargs)

        elif verb == "patch":
            r = requests.patch(url, **request_kwargs)

        elif verb == "post":
            r = requests.post(url, **request_kwargs)

        elif verb == "put":
            r = requests.put(url, **request_kwargs)

        else:
            raise ValueError("Invalid HTTP verb.")

        return(r.status_code, r.headers, r.text)
    

    def __send_signed_http_request(self, verb, url, body=None, headers={}, verify_ssl=True):
        """Send a signed HTTP request. This is a proxy for __send_http_request() that adds a bearer token.

        Args:
            verb (str): HTTP verb to use.
            url (str): URL to connect to.
            body (str, optional): HTTP requrest body. Defaults to None.
            headers (dict, optional): HTTP headers. Defaults to {}.

        Returns:
            list: Response elements from HTTP request.
        """

        # Get a JWT token, add it to headers.
        token = self.__generate_jwt_token()
        headers.update({"Authorization": f"Bearer {token}"})

        # Send the request.
        response = self.__send_http_request(verb, url, body, headers=headers,
            verify_ssl=verify_ssl)

        return response


    @lru_cache(1)
    def __generate_jwt_token(self):
        # Generate expiration time.
        expiration = int(time.time() + self.__jwt_expire_sec)

        # Build headers.
        headers = {
            "alg": "ES256",
            "kid": self.__key_id,
            "typ": "JWT"
        }

        # Build playload
        payload = {
            "iss": self.__issuer_id,
            "exp": expiration,
            "aud": "appstoreconnect-v1"
        }

        # Read the private key file.
        with open(self.__privkey_path, "r") as pk_file:
            private_key = pk_file.read()

        # Encode token.
        token = jwt.encode(payload=payload, key=private_key, algorithm="ES256", headers=headers)

        return token

    
    def request_in_review_report(self, rptg_day):
        """Request in-review report.

        Args:
            rptg_day (str): Reporting day in YYYY-MM-DD format.

        Returns:
            str: Tab-separated values.
        """

        path_part = f"/reports/in-review/v1?rptg_date={rptg_day}"

        # Construct API URL and make the signed request.
        report_url = f"{self.__api_base_url}{path_part}"
        response = self.__send_signed_http_request("get", report_url)
        
        return response


class OuptutDataLayer:
    def __init__(self):
        pass


    def __write_file(self, file_name, content):
        """Write content to a file.

        Args:
            file_name (str): File name
            content (str): File content
        """

        with open(file_name, "w") as f:
            f.write(content)


    def write_in_review_report(self, rprt_date, body):
        """Write the in-review report to disk.

        Args:
            rprt_date (str): String in YYYY-MM-DD format.
            body (str): Returned request body to be written.
        """

        file_name = f"in-review-{rprt_date}.tsv"
        self.__write_file(file_name, body)



# If we were called from the CLI...
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
                        prog = 'apple_report_downloader.py',
                        description = 'Get reports from the Apple Music API')
    parser.add_argument('--config', type=str, default="config.json",
        help="Specify an alternate config file.")
    parser.add_argument('--out', type=str, default=None,
        help="Override default output file name.")
    parser.add_argument('--get-in-review', type=str,
        help="Get in-review report. Accepts a date in YYYY-MM-DD format.")
    args = parser.parse_args()

    initial_args = {}
    operation_ct = 0

    # Increment operation count for each specified operation.
    if args.get_in_review is not False:
        operation_ct += 1

    if operation_ct > 1 or operation_ct < 1:
        print("Please specify exactly one operation.")
        parser.print_usage()
        exit(1)

    # Build objects out.
    output_data_layer = OuptutDataLayer()
    configurator = Configurator(config_file=args.config, args=initial_args)
    api = AppleAPI(**configurator.configuration)

    # Get in-review report
    if args.get_in_review is not False:
        results = api.request_in_review_report(args.get_in_review)

        # Success!
        if results[0] == 200:
            output_data_layer.write_in_review_report(args.get_in_review, results[2])

        else:
            raise RuntimeError("API returned an HTTP %s." %results[0])
