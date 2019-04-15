# -*- coding: utf-8 -*-
# API - act
# FileName: exception.py
# Version: 1.0.0
# Create: 2018-10-13
# Modify: 2018-10-18
from .util import Format


class CommonErr(Exception):
    SYS_BUSY = {'errcode': -1, 'errmsg': 'System busy'}
    UNKNOWN = {'errcode': -2, 'errmsg': 'Unknown error'}
    SDK = {'errcode': -3, 'errmsg': 'SDK exception'}
    PARAM_MISS = {'errcode': 40000, 'errmsg': 'Required parameter missing'}
    PARAM_LENGTH = {'errcode': 40001, 'errmsg': 'Parameter length exceeds the specified range'}

    def __init__(self, errcode, detail):
        """
        :param int errcode: Error code. https://www.yuque.com/mof/api/errcode
        :param str detail: Detail
        usage: raise CommonErr(-1)
        """
        self.errcode = errcode
        self.errmsg = Format.get(__ERROR_MAP__, errcode, self.UNKNOWN)['errmsg']
        self.detail = detail

    def __str__(self):
        return str({
            'errcode': self.errcode,
            'errmsg': self.errmsg,
            'detail': self.detail,
        })


class AuthErr(CommonErr):
    INVALID_ACTID = {'errcode': 40010, 'errmsg': 'Invalid act_id'}
    INVALID_SIGN = {'errcode': 40011, 'errmsg': 'Invalid signature'}
    EXPIRED_SIGN = {'errcode': 40012, 'errmsg': 'The signature has expired'}


class SDKErr(CommonErr):
    def __init__(self, detail=str(), doc=None):
        """
        :param str detail:
        :param object or tuple doc:
        """
        if doc is not None:
            detail += 'class {}: {}'.format(doc.__name__, doc.__doc__)
        CommonErr.__init__(self, -3, 'SDK exception. ' + detail)


class InvalidParam(SDKErr):
    def __int__(self, detail=str(), doc=None):
        """
        :param str detail:
        :param object doc:
        """
        SDKErr.__init__(self, 'Invalid parameter. ' + detail, doc)


__ERROR_MAP__ = {
    -1: CommonErr.SYS_BUSY,
    -2: CommonErr.UNKNOWN,
    -3: CommonErr.SDK,
    40000: CommonErr.PARAM_MISS,
    40001: CommonErr.PARAM_LENGTH,
    40010: AuthErr.INVALID_ACTID,
    40011: AuthErr.INVALID_SIGN,
    40012: AuthErr.EXPIRED_SIGN,
}
