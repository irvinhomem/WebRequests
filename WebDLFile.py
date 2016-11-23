import logging
import json
import csv

import requests
import shutil
import cgi

#https://androzoo.uni.lu/api/download?apikey=${APIKEY}&sha256=${SHA256}

class WebDLFile(object):

    def __init__(self):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        # self.logger.setLevel(logging.WARNING)

        # Initialize basic params
        self.config_file_path = "configs/configs.json"

        config_json = self.load_config_file()
        self.apk_list_filename = "first-20.csv"
        self.apk_list_path = config_json['apk_list_path']
        self.api_key = config_json['api_key']

        self.all_sha256_hashes = []
        # # Test
        # self.sha256_hash = "00001112E046D8BBF8B5529A9ECB39920F828209EF4ABFEB95AAB46D41F56A7D"

        self.target_url = "https://androzoo.uni.lu/api/download"

        self.output_file_path = "/home/irvin/AndroZoo_APKs/"

    def load_config_file(self):
        # apikey_on_file = ""
        with open(self.config_file_path) as json_config_file:
            json_data = json.load(json_config_file)

        self.logger.debug(json_data)
        # api_key_on_file = data['api_key']
        # self.apk_list_path = data['apk_list_path']
        # return api_key_on_file
        return json_data

    def read_apk_csv(self):
        full_apk_list_path = self.apk_list_path + self.apk_list_filename
        self.logger.debug("APK list full path: %s" % full_apk_list_path)

        with open(full_apk_list_path, mode='r', newline='') as csvfile:
            sha256_hash_rdr = csv.reader(csvfile, delimiter=',')
            # Skip first line (header)
            next(sha256_hash_rdr)

            self.logger.info("Opened config file ...")
            for row in sha256_hash_rdr:
                self.all_sha256_hashes.append(row[0])
        self.logger.info("Finished loading [ %i ] hashes" % len(self.all_sha256_hashes))

    def download_file(self, curr_sha256_hash):
        url_params = {"apikey": self.api_key, "sha256": curr_sha256_hash}
        #out_file_name = self.sha256_hash + ".apk"
        #resp = requests.post(self.target_url, data = url_params)
        resp = requests.get(self.target_url, params=url_params, stream=True)
        self.logger.debug("Response Status Code: %s" % resp.status_code)
        if resp.status_code == 200:
            # Get original filename out of HTTP headers
            header_params = cgi.parse_header(resp.headers['content-disposition'])
            self.logger.debug("HTTP Header Params: %s" % str(header_params))
            original_filename = header_params[1]['filename']

            # Write file
            out_file_path = self.output_file_path + original_filename
            self.logger.debug("Output File Path: %s" % out_file_path)
            with open(out_file_path, 'wb') as out_file:
                shutil.copyfileobj(resp.raw, out_file)
                self.logger.info("Successful Download: %s" % original_filename)



downloader = WebDLFile()
#downloader.load_config_file()
downloader.read_apk_csv()

#downloader.download_file()