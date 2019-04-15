# -*- coding: utf-8 -*-
# API - fc
# FileName: cs.py
# Version: 1.2.0
# Create: 2018-11-08
# Modify: 2018-11-10
import csv
import oss2
from act import OTS
import tablestore as ts

RESERVE_LENGTH = 60
CR = 'Content-Range'
OP = '?x-oss-process='
MAX_READ_BYTES = 30 * 1024 * 1024


class CSLog(object):
    def __init__(self, bucket, key):
        """
        :param oss2.Bucket bucket:
        :param str key:
        """
        self.key = key
        self.body = bytes()
        self.error = list()
        self.record = dict()
        self.bucket = bucket
        self.length = MAX_READ_BYTES
        self.range = [0, MAX_READ_BYTES - 1]
        self.fetch()

    def fetch(self):
        if self.range[1] - self.range[0] < RESERVE_LENGTH:
            return self.database()
        resp = self.bucket.get_object(self.key, self.range)
        self.body = resp.read()
        if self.range[0] == 0:
            if CR not in resp.headers:
                self.range = [0, 0]
                return self.counter()
            self.length = int(resp.headers[CR].split('/')[1])
        valid_len = MAX_READ_BYTES - self.body[::-1].find(b'\n')
        self.body = self.body[:valid_len]
        self.range[0] += valid_len
        self.range[1] = self.range[0] + MAX_READ_BYTES
        self.range[1] = min(self.range[1], self.length) - 1
        return self.counter()

    def counter(self):
        if self.body[-1] == b'\n':
            self.body = self.body[:-1]
        self.body = csv.reader(
            self.body.decode().split('\n'),
            delimiter=' ', quotechar='"')
        for row in self.body:
            if not row:
                continue
            # noinspection PyBroadException
            try:
                rec = row[6].split('mosdb', 1)[-1]
                rec = rec.replace('%2f', '/', 6)
                rec = rec.replace('%2F', '/', 6)
                rec = rec.split('/user/', 1)
                if len(rec) < 2:
                    continue
                rec = rec[-1].split('/', 1)
                if not rec[1].startswith('data/app/cs/'):
                    continue
                if rec[0] not in self.record:
                    self.record[rec[0]] = [0, 0]
                if row[8] != '-':
                    self.record[rec[0]][0] += int(row[8])
                if row[24] != '-':
                    self.record[rec[0]][1] += int(row[24])
                if rec[1].find(OP) == -1:
                    continue
                self.record[rec[0]][0] += int(int(row[8]) / 10) \
                    if row[19] == '-' else int(int(row[19]) / 10)
            except Exception:
                self.error.append(row[13])
        return self.fetch()

    def database(self):
        del self.body
        for key in self.record:
            [flow, storage] = self.record[key]
