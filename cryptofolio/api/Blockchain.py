import requests
from time import sleep

from .Logger import Logger


import codecs
import json
import time
import urllib.request
from urllib.error import HTTPError
from decimal import Decimal
from wallet_utils.crypto import *


# xpub = "xpub6CUGRUonZSQ4TWtTMmzXdrXDtypWKiKrhko4egpiMZbpiaQL2jkwSB1icqYh2cfDfVxdx4df189oLKnC5fSwqPfgyP3hooxujYzAu3fDVmz"
# xpub_segwit = "xpub6CxXsMT2YRk1CjEPqYRRXxqXPoiVsvYz66sBnyD7rEbG4XJFkYd2FG9wP3KakpuBWC15u21zcCy3g2v6Vw2GQGAqKDxHFip3jBhskd42iE7"
# ypub_segwit = "ypub6XnoB27wh7HV42RWfuD3k3w2ZmrwpYYV1DPQaN71EEy97d7V1CnasKp5QFHAkjZ6uq7teVcZ4sKbZKXfDdSHCVrSBZehqddXzumX9B3kfUF"


def ypub_to_xpub(ypub_string):
    """
    Sometimes extended public keys are written prefixed by 'ypub' instead of 'xpub', designating a segwit address.
    (Trezor, for example, does this.) This function converts a ypub address to an xpub address.
    :param ypub_string: The ypub address, as a string.
    :return: The corresponding xpub address, as a string.
    """
    raw = Base58.check_decode(ypub_string)
    return Base58.check_encode(codecs.decode('0488b21e', 'hex') + raw[4:])  # prefix with 'xpub' then reencode


def http_get(url, as_json=True, headers=None, backoff_coefficient=1.5, max_backoff=10, max_retries=10):
    """
    Send an HTTP GET. Implements automatic retries with exponential backoff in case of failure.
    :param url: The URL to request.
    :param as_json: Parse the response as JSON?
    :param headers: Headers to add to the request.
    :param backoff_coefficient: The number by which to multiply the wait period for each backoff.
    :param max_backoff: The maximum wait time.
    :param max_retries: The maximum number of retries for a failed request.
    """
    for i in range(max_retries + 1):
        rq = urllib.request.Request(url)
        SPOOF_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                      'Chrome/39.0.2171.95 Safari/537.36 '
        rq.add_header('User-Agent', SPOOF_AGENT)
        if headers is not None:
            rq.headers.update(headers)
        try:
            with urllib.request.urlopen(rq) as page:
                print("OK HTTP GET " + url)
                data = page.read()
                if not as_json:
                    return str(data)
                else:
                    encoding = page.info().get_content_charset("utf-8")
                    js = json.loads(data.decode(encoding))
                    return js
        except HTTPError as e:
            print("FAILED HTTP GET " + url)
            time.sleep(min(max_backoff, backoff_coefficient ** i))


def segwit_wallet_balance_hack(extended_public_key):
    """
    Given a segwit xpub (in either xpub or ypub format) at the account level, get the balance of the wallet by scraping
    data from the blockchain.info web interface.
    :param extended_public_key: The account extended public key.
    :return: The BTC balance as a Decimal.
    """
    # Convert from ypub if necessary
    xpub = extended_public_key
    if extended_public_key.find("ypub") == 0:
        xpub = ypub_to_xpub(extended_public_key)

    # You can do a nicer version of this with BeautifulSoup
    page = http_get("https://blockchain.info/xpub/" + xpub, as_json=False)
    balance = page.split('<td id="final_balance">')[1].split('BTC')[0].split('>')[-1]
    return Decimal(balance)


class Blockchain:
    def __init__(self):
        self.logger = Logger(__name__)

    def getBalance(self, address):
        if address.startswith('xpub') or address.startswith('ypub'):
            return segwit_wallet_balance_hack(address)
        else:
            req_url = 'https://blockchain.info/q/addressbalance/' + address
            try:
                response = requests.get(req_url)
                return response.json() / 100000000
            except Exception as e:
                self.logger.log(e)
            return 0.0
