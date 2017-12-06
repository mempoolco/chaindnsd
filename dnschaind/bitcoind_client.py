import json
import base64
import requests
from decimal import Decimal


class BitcoindException(Exception):
    def __init__(self, message, method, params):
        self._message = message
        self._method = method
        self._params = params

    def getmessage(self):
        return self._message

    def getmethod(self):
        return self._method

    def getparams(self):
        return self._params


class BitcoinRPCClient(object):
    def __init__(self, btcd_user, btcd_password, btcd_url, logger=None, cache=None):
        self.logger = logger
        btcd_authpair = btcd_user + b':' + btcd_password
        btcd_auth_header = b'Basic ' + base64.b64encode(btcd_authpair)

        self.btcd_url = btcd_url
        self.btcd_headers = {'content-type': 'application/json', 'Authorization': btcd_auth_header}
        self.cache = cache

    def call(self, method: str, *params, parse_float=Decimal):
        return self._call(method, True, *params, parse_float=parse_float)

    def _emptyrescall(self, method, *params):
        return self._call(method, False, *params)

    def _call(self, method: str, json_response: bool, *params, parse_float: type = Decimal):
        payload = {
            'method': method,
            'params': params,
            'jsonrpc': '2.0',
            'id': 0,
        }

        json_data = json.dumps(payload)
        resp = requests.post(self.btcd_url, data=json_data, headers=self.btcd_headers)
        content = resp.text
        if json_response:
            content = json.loads(content, parse_float=parse_float)
            if content['error']:
                self.logger and self.logger.warn('bitcoind error message: {}'.format(content['error']))
                raise BitcoindException(content['error'], method, params)

            self.logger and self.logger.debug("bitcoind call %s(%s) -> %s" % (method, params, content['result']))
            return content['result']
        else:
            return content

    def getinfo(self):
        return self.call('getinfo')

    def listunspent(self, address, minconf, maxconf):
        return self.call('listunspent', minconf, maxconf, [address])

    def getrawtransaction(self, txid=None):
        rawtx = self.call('getrawtransaction', txid, 1)
        return rawtx

    def decoderawtransaction(self, rawtx=None):
        decoded = self.call('decoderawtransaction', rawtx)
        return decoded

    def getblock(self, block_hash, verbose=True):
        return self.call('getblock', block_hash, verbose)

    def getblockheader(self, block_hash, verbose=True):
        return self.call('getblockheader', block_hash, verbose)

    def getblockhash(self, block_height):
        return self.call('getblockhash', block_height)

    def getrawmempool(self, verbose=False):
        return self.call('getrawmempool', verbose)

    def getmempoolentry(self, txid: str):
        return self.call('getmempoolentry', txid)

