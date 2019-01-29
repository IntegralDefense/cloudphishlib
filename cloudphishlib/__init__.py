import os
import sys
import time
import json
import logging
import requests
from configparser import ConfigParser


def load_config(required_keys=[]):
    """Load cloudphish configuration. Configuration files are looked for in the following locations::
        /<python-lib-where-cloudphishlib-installed>/etc/ace_cloudphish.ini
        /etc/ace/cloudphish/ace_cloudphish.ini
        ~/<current-user>/.ace/cloudphish/ace_cloudphish.ini

    Configuration items found in later config files take presendence over earlier ones.

    :param str profile: (optional) Specifiy a cloudphish node to work with.
    :param list required_keys: (optional) A list of required config keys to check for
    """

    logger = logging.getLogger(__name__+".load_config")
    config = ConfigParser()
    config_paths = []
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # default
    config_paths.append(os.path.join(BASE_DIR, 'etc', 'ace_cloudphish.ini'))
    # global
    config_paths.append('/etc/ace/cloudphish/ace_cloudphish.ini')
    # legacy
    #config_paths.append('/opt/cloudphishlib/etc/ace_cloudphish.ini')
    # user specific
    config_paths.append(os.path.join(os.path.expanduser("~"),'.ace', 'cloudphish', 'ace_cloudphish.ini'))
    finds = []
    for cp in config_paths:
        if os.path.exists(cp):
            logger.debug("Found config file at {}.".format(cp))
            finds.append(cp)
    if not finds:
        logger.critical("Didn't find any config files defined at these paths: {}".format(config_paths))
        raise Exception("MissingLercConfig", "Config paths : {}".format(config_paths))

    config.read(finds)
    return config


# simple api for common cloudphish requests
class cloudphish():
    """Simple ACE Cloudphish API wrapper.

    :param str profile: Specify the ACE Cloudphish environment to work with. Default works with a localhost ACE install.
    :param str server: (optional) specify a Cloudphish server address.
    :param str port: (optional) specify the server port.
    :param str ca_bundle_file_path: (optional) The path to the CA bundle file authoritative for the server.
    """

    logger = logging.getLogger(__name__)
    def __init__(self, profile='default', server=None, port=None, ca_bundle_file_path=None):

        self.config = load_config()
        self.server = self.config[profile]['server']
        self.port = self.config[profile]['port']
        self.CA_BUNDLE_FILE = self.config[profile]['ca_bundle_file']
        if server:
            self.server = server
        if port:
            self.port = port
        if ca_bundle_file_path:
            self.CA_BUNDLE_FILE = ca_bundle_file_path
        self.base_url = 'https://{}:{}/'.format(self.server, self.port)
        if self.config[profile].getboolean('ignore_system_proxy'):
            if 'https_proxy' in os.environ:
                del os.environ['https_proxy']


    def submit(self, url, reprocess=False, alert=False, text=False):
        self.logger.debug("checking on '{}'".format(url))
        path = os.path.join('api','cloudphish','submit')
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
        path = os.path.join('api','cloudphish')
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
        path = os.path.join('api','cloudphish','clear_alert')
        arguments = {'url': url}

        r = requests.get(self.base_url + path, params=arguments, verify=self.CA_BUNDLE_FILE)
        return json.loads(r.text)

