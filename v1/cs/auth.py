# -*- coding: utf-8 -*-
# API - cs
# FileName: auth.py
# Version: 1.0.0
# Create: 2018-10-24
# Modify: 2018-10-24
import oss2
from . import default


class OSS(object):
    def __init__(self, intranet=True, extranet=False):
        """
        :param bool intranet:
        :param bool extranet:
        """
        self.extranet = None
        self.intranet = None
        if extranet:
            self.extranet = oss2.Bucket(
                oss2.Auth(default.AK_ID, default.AK_SECRET),
                default.DOMAIN,
                default.BUCKET_NAME,
                is_cname=True)
        if intranet:
            self.intranet = oss2.Bucket(
                oss2.Auth(default.AK_ID, default.AK_SECRET),
                default.INTERNAL_DOMAIN,
                default.BUCKET_NAME,
                is_cname=False)

    def sign_url(self, method='GET', key=None, expires=60, headers=None, params=None, intranet=False):
        if intranet:
            return self.intranet.sign_url(method, key, expires, headers, params).replace('http://', 'https://')
        return self.extranet.sign_url(method, key, expires, headers, params).replace('http://', 'https://')

