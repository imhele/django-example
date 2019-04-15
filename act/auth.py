# -*- coding: utf-8 -*-
# API - act
# FileName: auth.py
# Version: 1.0.0
# Create: 2018-10-13
# Modify: 2018-10-18
import hmac
import time
import hashlib
from . import default
from .store import MySQL, OTS
from .util import Format, Hash, Random
from .exception import AuthErr, CommonErr


class SignType(object):
    MD5 = 'MD5'
    HMAC_SHA1 = 'HMAC_SHA1'
    HMAC_SHA256 = 'HMAC_SHA256'

    __values__ = [
        MD5,
        HMAC_SHA1,
        HMAC_SHA256,
    ]

    __members__ = [
        'SignType.MD5',
        'SignType.HMAC_SHA1',
        'SignType.HMAC_SHA256',
    ]


class Auth(object):
    def __init__(self, act_id, secret, sign_type=default.SIGN_TYPE):
        """
        :param str act_id: ID for every action
        :param str secret: Secret of your application
        :param str sign_type: The method of computing signature
        """
        self.act_id = act_id.strip()
        self.secret = secret.strip()
        self.sign_type = sign_type.strip().upper()
        self.signature = None
        self.expiry_time = 0

    def set_sign_type(self, sign_type):
        self.sign_type = sign_type.strip().upper()

    def __compute_sign(self, data):
        """
        :param dict data: The parameters required for signature
        :return: Signature
        """
        sign_bytes = Format.query_string(data, sort=True).encode(default.CODING)
        if self.sign_type == SignType.MD5:
            signature = Hash.md5_hex_str(sign_bytes, True)
        elif self.sign_type == SignType.HMAC_SHA1:
            h = hmac.new(self.secret.encode(default.CODING), sign_bytes, hashlib.sha1)
            signature = Hash.base64_str(h.digest())
        else:
            h = hmac.new(self.secret.encode(default.CODING), sign_bytes, hashlib.sha256)
            signature = Hash.base64_str(h.digest())
        return signature

    def sign(self, expires_in=default.SIGN_EXPIRES_IN, expiry_time=None, use_cache=False):
        """
        :param int or None expires_in: Valid time of signature. Unit: second
        :param int or str or None expiry_time: Expiry time of signature. Unit: second. Unix timestamp
        :param bool use_cache: Using the cached signature
        :return: expiry_time, signature
        """
        timestamp = int(time.time())
        if not use_cache or timestamp + default.SIGN_EXPIRES_BUFFER > int(self.expiry_time):
            expiry_time = str(expiry_time or timestamp + expires_in)
            param = {
                'act_id': self.act_id,
                'expiry_time': expiry_time,
                'secret': self.secret,
                'sign_type': self.sign_type,
            }
            self.signature = self.__compute_sign(param)
            self.expiry_time = expiry_time
        return self.expiry_time, self.signature

    def nonce_sign(self, data=None, nonce=None, nonce_len=default.NONCE_LEN):
        """
        :param dict or None data: The parameters required for signature
        :param str or None nonce: Random string
        :param int nonce_len: Length of random string
        :return: nonce, nonce_sign
        """
        if nonce is None:
            nonce = Random.string(nonce_len)
        if data is None:
            data = dict()
        data['act_id'] = Format.get(data, 'act_id', self.act_id)
        data['secret'] = Format.get(data, 'secret', self.secret)
        nonce_sign = self.__compute_sign(data)
        return nonce, nonce_sign


class RequestAuth(object):
    def __init__(self, database, second_choice=None):
        """
        :param MySQL or OTS database: Database
        :param MySQL or OTS second_choice: Second choice of database
        """
        self.db = database
        self.sc = second_choice or database

    def check_signature(self, act_id, expiry_time, signature, sign_type):
        """
        :param str act_id: ID for every action
        :param str expiry_time: Expiry time of signature. Unit: second. Unix timestamp
        :param str signature: Signature
        :param str sign_type: The method of computing signature
        :return: check result
        """
        if sum(map(lambda i: i is None, (act_id, expiry_time, signature))):
            return CommonErr.PARAM_MISS
        if not time.time() < int(expiry_time) < time.time() + default.MAX_SIGN_EXPIRES_IN:
            return AuthErr.EXPIRED_SIGN
        act = self.db.select([('ActID', act_id)])
        app = self.sc.select([('AppID', act.dict['PassiveParty'])])
        _, resign = Auth(act_id, app.dict['Secret'], sign_type).sign(expiry_time=expiry_time)
        if not resign == signature:
            return AuthErr.INVALID_SIGN
        return {
            'errcode': 0,
            'act': act,
            'app': app,
        }

    def django(self, view_func):
        """
        :param view_func:
        :return: wrapped_view
        """

        def wrapped_view(request, *args, **kwargs):
            get = dict(request.GET)
            post = dict(request.POST)
            act_id = Format.get(post, 'act_id')
            expiry_time = Format.get(post, 'expiry_time')
            signature = Format.get(post, 'signature')
            sign_type = Format.get(post, 'sign_type', default.SIGN_TYPE)
            if act_id is None or expiry_time is None or signature is None or sign_type is None:
                act_id = Format.get(get, 'act_id')
                expiry_time = Format.get(get, 'expiry_time')
                signature = Format.get(get, 'signature')
                sign_type = Format.get(get, 'sign_type', default.SIGN_TYPE)
            auth_res = self.check_signature(act_id, expiry_time, signature, sign_type)
            return view_func(request, auth_res, *args, **kwargs)

        return wrapped_view
