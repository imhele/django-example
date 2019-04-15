# -*- coding: utf-8 -*-
# API - cs
# FileName: download.py
# Version: 1.0.0
# Create: 2018-10-27
# Modify: 2018-11-07
import mimetypes
from .auth import OSS
from .util import Check
from act import StoreData
from .upload import FolderFile, Source
from .exception import CSCommonErr, CSDownloadErr


class Download(object):
    def __init__(self, act=None, app=None):
        """
        :param StoreData act:
        :param StoreData app:
        """
        self.act = act
        self.app = app

    def normal(self, content_type, expires, folder_file, intranet, source_file):
        """
        :param str or None content_type: Content type in headers
        :param int or None expires: Url expires
        :param str folder_file: Eg: folder/${FolderId}/.../t=${CreateTime}&n=${FileName}&i=${FileId}
        :param bool intranet: Return intranet url
        :param str source_file: Eg: source/${FileId}.source.cs
        :return:
        """
        headers = None
        if content_type is not None:
            if mimetypes.guess_extension(content_type) is not None:
                headers = {'Content-Type': content_type}
        if not Check.download_expires(expires):
            return CSDownloadErr.EXPIRES_LIMIT
        if not folder_file.startswith('folder/'):
            return CSCommonErr.INVALID_FOLDER
        if not source_file.startswith('source/'):
            return CSCommonErr.INVALID_SOURCE
        appid = self.act.dict['PassiveParty']
        if source_file is not None:
            source = Source(appid, suffix=source_file)
        else:
            source = FolderFile(appid, suffix=folder_file).source
        oss = OSS(intranet=intranet, extranet=(not intranet))
        url = oss.sign_url('GET', source.key, expires, headers, intranet=intranet)
        return {
            'errcode': 0,
            'url': url,
            'headers': headers,
            'source': source.suffix,
        }

