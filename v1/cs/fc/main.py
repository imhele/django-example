# -*- coding: utf-8 -*-
# API - fc
# FileName: main.py
# Version: 1.0.0
# Create: 2018-11-08
# Modify: 2018-11-08
import time
import json
import oss2
import random
import tablestore

OSS_NET = 'oss-cn-beijing-internal.aliyuncs.com'
OTS_NET = 'https://YOUR-BUCKET.cn-beijing.ots-internal.aliyuncs.com'


def record_error(msg, bucket):
    """
    :param dict or str msg:
    :param oss2.Bucket bucket:
    :return:
    """
    key = 'mosdb/log/fc-sfive-{0}-{1:0>4}'.format(time.time(), random.randint(0, 9999))
    bucket.put_object(key, json.dumps(msg, ensure_ascii=False))


def index(event, context):
    evt = json.loads(event)['events'][0]
    auth = oss2.StsAuth(
        context.credentials.access_key_id,
        context.credentials.access_key_secret,
        context.credentials.security_token)
    key = evt['oss']['object']['key']
    bucket = oss2.Bucket(auth, OSS_NET, 'sfive')
    ots = tablestore.OTSClient(
        OTS_NET,
        context.credentials.access_key_id,
        context.credentials.access_key_secret,
        'YOUR-BUCKET',
        sts_token=context.credentials.security_token,
    )
