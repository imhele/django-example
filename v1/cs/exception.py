# -*- coding: utf-8 -*-
# API - cs
# FileName: exception.py
# Version: 1.0.0
# Create: 2018-10-25
# Modify: 2018-10-27
from act import CommonErr


class CSCommonErr(CommonErr):
    INVALID_NAME = {'errcode': 40100, 'errmsg': 'Invalid filename or folder name'}
    INVALID_SOURCE = {'errcode': 40101, 'errmsg': 'Invalid source'}
    INVALID_FOLDER = {'errcode': 40102, 'errmsg': 'Invalid folder'}


class CSUploadErr(CommonErr):
    FOLDER_RECORD_LIMIT = {'errcode': 40103, 'errmsg': 'Length of folder record exceeds limit'}


class CSDownloadErr(CommonErr):
    EXPIRES_LIMIT = {'errcode': 40104, 'errmsg': 'Expiry time exceeds limit'}


__ERROR_MAP__ = {
    -1: CommonErr.SYS_BUSY,
    -2: CommonErr.UNKNOWN,
    -3: CommonErr.SDK,
    40100: CSCommonErr.INVALID_NAME,
    40101: CSCommonErr.INVALID_SOURCE,
    40102: CSCommonErr.INVALID_FOLDER,
    40103: CSUploadErr.FOLDER_RECORD_LIMIT,
    40104: CSDownloadErr.EXPIRES_LIMIT,
}
