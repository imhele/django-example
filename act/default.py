# -*- coding: utf-8 -*-
# API - act
# FileName: default.py
# Version: 1.0.0
# Create: 2018-10-17
# Modify: 2018-10-18
"""
Default settings and values
"""

"""global"""
CODING = 'utf8'

"""auth"""
MAX_SIGN_EXPIRES_IN = 7200
NONCE_LEN = 32
SIGN_TYPE = 'MD5'
SIGN_EXPIRES_BUFFER = 30
SIGN_EXPIRES_IN = 1800

"""exception"""
RESPONSE_CORS = '*'
RESPONSE_FORMAT = 'JSON'

"""store"""
MYSQL_CHARSET = 'utf8mb4'
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
OTS_TIMEOUT = 10
OSS_CNAME = False
ROW_CONDITION = 'IGNORE'
