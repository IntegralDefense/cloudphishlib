import os
import sys
import time
import json
import logging
import requests
from configparser import ConfigParser

# simple api for common cloudphish requests
class cloudphish():
    server = 'cloudphish1.local'
    port = 5000
    base_url = 'https://{}:{}/'.format(server, port)
    logger = logging.getLogger(__name__)
    # path to ca_bundle that signed the server cert
    # leaving True, means requests will still verify
    CA_BUNDLE_FILE = True
    if 'integral_ca_bundle' in os.environ:
        CA_BUNDLE_FILE = os.environ['integral_ca_bundle']
    elif os.path.exists(os.path.join('/','usr','local','share','ca-certificates','integral-ca.pem')):
        CA_BUNDLE_FILE = os.path.join('/','usr','local','share','ca-certificates','integral-ca.pem')

    def __init__(self, server=None, port=None, ca_bundle_file_path=None):
        if server:
            self.server = server
        if port:
            self.port = port
        if ca_bundle_file_path:
            self.CA_BUNDLE_FILE = ca_bundle_file_path

    def submit(self, url, reprocess=False, alert=False, text=False):
        self.logger.debug("checking on '{}'".format(url))
        path = os.path.join('saq','cloudphish','submit')
        arguments = {'url': url}
        if alert:
            arguments['a'] = 1
        if reprocess:
            arguments['r'] = 1

        r = requests.post(self.base_url + path, params=arguments, verify=self.CA_BUNDLE_FILE)

        if text:
            return r.text
        return json.loads(r.text)

    def get(self, sha256, compress=False):
        self.logger.debug("downloading content for: {}".format(sha256))
        path = os.path.join('saq','cloudphish')
        if compress:
            path = os.path.join(path, 'download_alert')
        else:
            path = os.path.join(path, 'download')
        arguments = {'s': sha256}

        r = requests.get(self.base_url + path, params=arguments, verify=self.CA_BUNDLE_FILE)

        if r.status_code != requests.codes.ok:
            raise Exception("Received status code {} message: '{}'".format(r.status_code, r.text))

        return r.text

    def clear(self, url):
        self.logger.debug("Clearing chached results for : '{}'".format(url))
        path = os.path.join('saq','cloudphish','clear_alert')
        arguments = {'url': url}

        r = requests.get(self.base_url + path, params=arguments, verify=self.CA_BUNDLE_FILE)
        return json.loads(r.text)

