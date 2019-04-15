# -*- coding: utf-8 -*-
# API - cs
# FileName: util.py
# Version: 1.0.0
# Create: 2018-10-24
# Modify: 2018-11-07
import re
import json
import time
from . import default


class Time(object):
    @staticmethod
    def unix_str(reverse=True, format_char='0', format_len=10):
        ts = int(time.time())
        if reverse:
            ts = pow(10, format_len) - ts
        return '{{0:{0}>{1}}}'.format(format_char, format_len).format(ts)


class Check(object):
    @staticmethod
    def file_name(file_name):
        """
        :param str file_name:
        :return:
        """
        try:
            file_name = json.dumps(file_name, ensure_ascii=False)
            return not re.search(r'[\\/,?=&%"]', file_name)
        except:
            return False

    @staticmethod
    def folder_name(folder_name):
        """
        :param str folder_name:
        :return:
        """
        try:
            folder_name = json.dumps(folder_name, ensure_ascii=False)
            return not re.search(r'[\\/,?=&%"]', folder_name)
        except:
            return False

    @staticmethod
    def download_expires(expires):
        """
        :param int expires:
        :return:
        """
        r = default.DOWNLOAD_URL_EXPIRES_RANGE
        return r[1] <= expires <= r[0]
