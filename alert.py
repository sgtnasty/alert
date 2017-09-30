#!/usr/bin/env python


"""
Alert script for server notifications via Twilio

https://www.twilio.com/docs/quickstart/python/

sudo pip install twilio

"""


import os
import sys
import json
import uuid
import datetime
import logging
import errno
import argparse
from twilio.rest import Client


__version__ = '0.0.3'
APPNAME = 'Twilio Alert Script'
ALERT_CONFIG_FILE = '/usr/local/etc/alert.json'
ALERT_LOGFILE = '/var/log/alert.log'


def config_args():
    """
    Configure command line arguments
    """
    parser = argparse.ArgumentParser(description=APPNAME,
        epilog=("Version {}".format(__version__)))
    parser.add_argument('-c', metavar='CONFIGFILE', required=False, help='path to config file',
        default=ALERT_CONFIG_FILE)
    parser.add_argument('--log', metavar='LOGFILE', required=False, help='path to log file',
        default=ALERT_LOGFILE)
    parser.add_argument('--version', action='version', version=('%(prog)s ' + __version__))
    parser.add_argument('--debug', required=False, help='Enable debugging of this script', action="store_true")
    args = parser.parse_args()
    return args


def config_log(args):
    """
    Configure Python Logging Module
    """
    # create logger
    logger = logging.getLogger('alert')
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s:%(process)d - %(levelname)s - %(message)s')
    # create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    # create file handler
    try:
        fh = logging.FileHandler(args.log)
        fh.setLevel(logging.DEBUG)
        # add formatter to fh
        fh.setFormatter(formatter)
        # add fh to logger
        logger.addHandler(fh)
        logger.setLevel(logging.INFO)
    except IOError as e:
        logger.error("Unable to open log file:%s, reason = %s" % (args.log, errno.errorcode[e[0]]))
    if (args.debug):
        # make sure to set both Handlers to the DEBUG level
        logger.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
        logger.debug("DEBUG Enabeled")
        logger.debug("args=%s" % repr(args))
    return logger


def config_alert(args, log):
    """
    Read the Destiny config file from JSON
    """
    try:
        fh = open(args.c)
        config = json.load(fh)
        fh.close()
    except:
        log.error('Error reading config file. %s: %s' % (sys.exc_type, sys.exc_value))
        sys.exit(1)
    if (args.debug):
        log.debug("config=%s" % repr(config))
    return config

def run(args, log, config):
    log.debug('twilio version: {}'.format(twilio.__version__))
    # Get these credentials from http://twilio.com/user/account
    client = Client(config["account_sid"], config["auth_token"])
    log.debug('twilio client: {}'.format(repr(client)))
    # Make the call
    call = client.api.account.calls.create(to = config["callto"], 
        from_ = config["callfrom"], url = config["url"])
    log.debug('twilio call: {}'.format(repr(call)))
    log.info('call placed: {}'.format(call.sid))


if __name__ == '__main__':
    args = config_args()
    log = config_log(args)
    alert_cfg = config_alert(args, log)
    log.info('{} version {}'.format(APPNAME, __version__))
    run(args, log, alert_cfg)
