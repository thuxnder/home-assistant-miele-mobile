import requests
import hmac
import datetime
import hashlib
import binascii
import json
import re
from urllib.parse import quote
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class NetworkException(Exception):
    def __init__(self, msg):
        super.__init__(self, msg)

class MieleResponse(dict):
    def __init__(self, mieleHomeDevice, path, raw=None):
        if raw is None:
            raw = mieleHomeDevice.get_raw(path)
        dict.__init__(self, raw)
        self.device = mieleHomeDevice
        self.root_path = path


    def _convert_value(self, key, value):
        path = '{}{}{}'.format(self.root_path, '/' if self.root_path[-1] != '/' else '', key)
        if re.match('/Devices/[0-9]+/State(/RemainingTime{1,2}|/StartTime{1,2}|/ElapsedTime{1,2})', path) is not None and isinstance(value, list):
            return int(value[0])*60 + int(value[1])
        elif isinstance(value, dict):
            return { k: self._convert_value('{}{}{}'.format(key, '/' if key[-1] != '/' else '', k), value.get(k)) for k in value.keys() }
        return value

    def get(self, key, default=None):
        value = dict.get(self, key, default)
        if isinstance(value, dict):
            if 'href' in value and isinstance(value['href'], str):
                fullpath = '{}{}'.format(self.root_path, value['href'])
                return MieleResponse(self.device, fullpath)
            else:
                return MieleResponse(self.device, self.root_path, value)
        return self._convert_value(key, value)

    def __str__(self):
        return str( self.toDict(1) )

    def toDict(self, level=0):
        def resolve(data):
            if isinstance(data, MieleResponse):
                if level == 1:
                    return data
                return data.toDict(max(level-1, 0))
            return data
        return { k: resolve(self.get(k)) for k in self.keys() }


class MieleHomeDevice:
    def __init__(self, host, group_id, group_key, timeout=5):
        self.host = host
        self.group_id = group_id
        self.group_key = group_key
        self.timeout = timeout

    def _decrypt_response(self, response_body, signature):        
        key = self.group_key[:int(len(self.group_key)/2)]
        iv = signature[:int(len(signature)/2)]
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        return decryptor.update(response_body) + decryptor.finalize()

    def _parse_response(self, response):
        response_str = response.decode('utf-8')
        if len(response_str) == 0:
            return {}
        return json.loads(response_str)

    def _get_signature(self, resource, date):
        signature_str = 'GET\n{}{}\n\napplication/vnd.miele.v1+json\n{}\n'.format(self.host, resource, date)
        return hmac.new(self.group_key, bytearray(signature_str.encode('ASCII')), hashlib.sha256)

    def _get_date_str(self):
        return datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

    def get_raw(self, resource):
        url = 'http://{}{}'.format(self.host, resource)
        date = self._get_date_str()
        signature = self._get_signature(resource, date)
        headers = {
            'Accept': 'application/vnd.miele.v1+json',
            'User-Agent': 'Miele@mobile 2.3.3 Android',
            'Host': self.host,
            'Date': date,
            'Authorization': 'MieleH256 {}:{}'.format(self.group_id.hex(), signature.hexdigest().upper()),
        }
        response = requests.get(url, headers=headers, timeout=self.timeout)
        response.raise_for_status
        response_signature = binascii.a2b_hex(response.headers['X-Signature'].split(':')[1])
        response_data = self._decrypt_response(response.content, response_signature)
        return self._parse_response(response_data)

    def get(self, path='/'):
        return MieleResponse(self, path)

    def getDevices(self):
        return MieleResponse(self, '/Devices/')

    def getState(self, id=None):
        if id is not None:
            return MieleResponse(self, '/Devices/{id}/State'.format(id=quote(id, safe='')))
        devices = self.getDevices()
        firstDevices = list(devices.keys())[0]
        return devices.get(firstDevices).get('State')

    def getIdent(self, id=None):
        if id is not None:
            return MieleResponse(self, '/Devices/{id}/Ident'.format(id=quote(id, safe='')))
        devices = self.getDevices()
        firstDevices = list(devices.keys())[0]
        return devices.get(firstDevices).get('Ident')
