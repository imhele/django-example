# -*- coding: utf-8 -*-
# API - cs
# FileName: default.py
# Version: 1.0.0
# Create: 2018-10-24
# Modify: 2018-10-27
"""
Default settings and values
"""


"""global"""
BUCKET_NAME = 'BUCKET_NAME'
CODING = 'utf-8'
DOMAIN = 'DOMAIN'
INTERNAL_DOMAIN = 'oss-cn-beijing-internal.aliyuncs.com'
PREFIX = 'mosdb/user/{0}/data/app/cs/'
RESERVE_CHAR = ','
RESERVE_CHAR_REPLACE = (RESERVE_CHAR, str())


"""auth"""
AK_ID = str()
AK_SECRET = str()


"""upload"""
UPLOAD_URL_EXPIRES = 60
FILE_ID_LEN = 32
FOLDER_ID_LEN = 8
FOLDER_RECORD_MAX_LEN = 16384


"""download"""
DOWNLOAD_URL_EXPIRES_RANGE = (0, 7200)
