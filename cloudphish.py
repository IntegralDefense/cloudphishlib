#!/usr/bin/python3

import os
import sys
import argparse
import logging

from cloudphishlib import cloudphish, load_config

logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(name)s - [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


if __name__ == "__main__":

    config = load_config()
    profiles = config.sections()
    parser = argparse.ArgumentParser(description="simple user interface to cloudphish")
    parser.add_argument('-e', '--environment', dest='environment', choices=profiles, default='default', help='select the ace cloudphish node you want to work with.')
    parser.add_argument('-s', '--submit', dest='url', help="submit a url/check on a url")
    parser.add_argument('-r', '--reprocess', action='store_true', help="make cloudphish reprocess a url")
    parser.add_argument('-a', '--alert', action='store_true', help="ACE alert if cloudphish finds a detection, and an alert hasn't already been generated")
    parser.add_argument('-c', '--clear', dest='clear_url', help="clear the cloudphish cache for a url")
    parser.add_argument('-g', '--get', dest='sha256_content', help="get the cached content")
    args = parser.parse_args()

    # ignore the proxy
    #if 'https_proxy' in os.environ:
    #    del os.environ['https_proxy']

    cp = cloudphish(profile=args.environment)

    if args.url:
        print(cp.submit(args.url, reprocess=args.reprocess, alert=args.alert, text=True))
    elif args.sha256_content:
        print(cp.get(args.sha256_content))
    elif args.clear_url:
        print(cp.clear(args.clear_url))
