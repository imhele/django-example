# -*- coding: utf-8 -*-
# API - act
# FileName: views.py
# Version: 1.0.0
# Create: 2018-10-13
# Modify: 2018-11-07
import time
from . import cs
from .main import request_auth
from act import Format, CommonErr


class UploadView(object):
    @staticmethod
    @request_auth
    def folder(_, auth, __, post):
        current_folder = Format.get(post, 'current_folder', 'folder/')
        folder_name = Format.get(post, 'folder_name')
        for param in (current_folder, folder_name):
            if param is None:
                return CommonErr.PARAM_MISS
        return cs.Upload(auth['act'], auth['app']).folder(current_folder, folder_name)

    @staticmethod
    @request_auth
    def normal(_, auth, __, post):
        content_type = Format.get(post, 'content_type')
        current_folder = Format.get(post, 'current_folder', 'folder/')
        file_name = Format.get(post, 'file_name', str(time.time() * 1000))
        intranet = bool(Format.get(post, 'intranet', False))
        return cs.Upload(auth['act'], auth['app']).normal(content_type, current_folder, file_name, intranet)

    @staticmethod
    @request_auth
    def folder_file(_, auth, __, post):
        current_folder = Format.get(post, 'current_folder', 'folder/')
        file_name = Format.get(post, 'file_name', str(time.time() * 1000))
        folder_file = Format.get(post, 'folder_file')
        source_file = Format.get(post, 'source_file')
        if folder_file is None or source_file is None:
            return CommonErr.PARAM_MISS
        return cs.Upload(auth['act'], auth['app']).folder_file(current_folder, file_name, folder_file, source_file)


class DownloadView(object):
    @staticmethod
    @request_auth
    def normal(_, auth, __, post):
        content_type = Format.get(post, 'content_type')
        expires = int(Format.get(post, 'expires', 60))
        folder_file = Format.get(post, 'folder_file')
        intranet = bool(Format.get(post, 'intranet', False))
        source_file = Format.get(post, 'source_file')
        if folder_file is None or source_file is None:
            return CommonErr.PARAM_MISS
        return cs.Download(auth['act'], auth['app']).normal(content_type, expires, folder_file, intranet, source_file)
