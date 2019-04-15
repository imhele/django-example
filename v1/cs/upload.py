# -*- coding: utf-8 -*-
# API - cs
# FileName: upload.py
# Version: 1.0.0
# Create: 2018-10-23
# Modify: 2018-11-07
import mimetypes
from . import default
from .auth import OSS
from .util import Time, Check
from act import Random, Format, StoreData
from .exception import CSUploadErr, CSCommonErr


class Source(object):
    @staticmethod
    def create(appid):
        """
        :param str appid: Application id
        :return:
        """
        return Source(appid, file_id=Random.string(default.FILE_ID_LEN))

    def __init__(self, appid, file_id=None, suffix=None):
        """
        :param str appid: Application id
        :param str or None file_id: Eg: source/${FileId}.source.cs
        :param str or None suffix: Eg: source/${FileId}.source.cs
        """
        self.file_id = file_id
        if file_id is None:
            self.file_id = suffix.split('/')[-1].split('.')[0]
        self.__prefix = default.PREFIX.format(appid)
        self.suffix = 'source/{0}.source.cs'.format(self.file_id)
        self.key = '{0}{1}'.format(self.__prefix, self.suffix)
        self.timeline = '{0}source/{1}/tl/'.format(self.__prefix, self.file_id)
        self.folder_record = '{0}source/{1}.folder.cs'.format(self.__prefix, self.file_id)


class Folder(object):
    @staticmethod
    def create(appid, folder_name, folder):
        """
        :param str appid: Application id
        :param str folder_name: Folder name
        :param Folder folder: File folder
        :return:
        """
        folder_id = Random.string(default.FOLDER_ID_LEN)
        folder_qs = Format.query_string([
            ('t', Time.unix_str()),
            ('n', folder_name),
            ('i', folder_id),
        ])
        return Folder(appid, '{0}{1}{2}'.format(
            folder.directory, default.RESERVE_CHAR, folder_qs))

    def __init__(self, appid, suffix):
        """
        :param str appid: Application id
        :param str suffix: Eg: folder/.../,t=${CreateTime}&n=${FolderName}&i=${FolderId}
        """
        self.suffix = suffix
        part = suffix.split(default.RESERVE_CHAR)
        self.__prefix = default.PREFIX.format(appid)
        self.key = '{0}{1}'.format(self.__prefix, self.suffix)
        if len(part) == 1:
            self.directory = 'folder/'
        else:
            self.directory = '{0}{1}/'.format(part[0], Format.parse_qs(part[1])['i'])


class FolderFile(object):
    @staticmethod
    def create(appid, file_name, folder, source):
        """
        :param str appid: Application id
        :param str file_name: Filename
        :param Folder folder: File folder
        :param Source source: Source file
        :return:
        """
        folder_file_qs = Format.query_string([
            ('t', Time.unix_str()),
            ('n', file_name),
            ('i', source.file_id),
        ])
        suffix = '{0}{1}'.format(folder.directory, folder_file_qs)
        return FolderFile(appid, suffix, source)

    def __init__(self, appid, suffix, source=None):
        """
        :param str appid: Application id
        :param str suffix: Eg: folder/${FolderId}/.../t=${CreateTime}&n=${FileName}&i=${FileId}
        :param Source source: Source file
        """
        self.source = source
        self.suffix = suffix
        self.__prefix = default.PREFIX.format(appid)
        self.key = '{0}{1}'.format(self.__prefix, suffix)
        if not isinstance(source, Source):
            self.source = Source(appid, file_id=Format.parse_qs(suffix.split('/')[-1])['i'])


class Upload(object):
    def __init__(self, act=None, app=None):
        """
        :param StoreData act:
        :param StoreData app:
        """
        self.act = act
        self.app = app

    @staticmethod
    def __folder_file(folder_file, headers=None, new_file=False, oss=None):
        """
        :param FolderFile folder_file: Folder file
        :param dict or None headers: Get folder file with headers
        :param bool new_file:
        :param OSS oss: Reusable oss session
        :return:
        """
        position = 0
        folder_record = folder_file.source.folder_record
        suffix = folder_file.suffix
        if oss is None:
            oss = OSS()
        if not new_file:
            suffix = default.RESERVE_CHAR + suffix
            record_head = oss.intranet.head_object(folder_record)
            position = int(record_head.headers['Content-Length'])
            headers = {'Content-Type': record_head.headers['Content-Type']}
        if position > default.FOLDER_RECORD_MAX_LEN:
            return CSUploadErr.FOLDER_RECORD_LIMIT
        oss.intranet.append_object(
            folder_record, position, suffix, headers=headers)
        oss.intranet.put_object(folder_file.key, str(), headers=headers)

    def folder(self, current_folder, folder_name):
        """
        :param str current_folder: Eg: folder/.../,t=${CreateTime}&n=${FolderName}&i=${FolderId}
        :param str folder_name: Folder name
        :return:
        """
        if not Check.folder_name(folder_name):
            return CSCommonErr.INVALID_NAME
        if not current_folder.startswith('folder/'):
            return CSCommonErr.INVALID_FOLDER
        appid = self.act.dict['PassiveParty']
        current = Folder(appid, current_folder)
        new_one = Folder.create(appid, folder_name, current)
        oss = OSS()
        oss.intranet.put_object(new_one.key, str())
        return {
            'errcode': 0,
            'folder': new_one.suffix,
        }

    def normal(self, content_type, current_folder, file_name, intranet):
        """
        :param str or None content_type: Content type in headers
        :param str current_folder: Eg: folder/.../,t=${CreateTime}&n=${FolderName}&i=${FolderId}
        :param str file_name: Filename
        :param bool intranet: Return intranet url
        :return:
        """
        # check exception of parameters
        headers = None
        if content_type is None or mimetypes.guess_extension(content_type) is None:
            content_type = mimetypes.guess_type(file_name)[0]
        if content_type is not None:
            headers = {'Content-Type': content_type}
        if not Check.file_name(file_name):
            return CSCommonErr.INVALID_NAME
        if not current_folder.startswith('folder/'):
            return CSCommonErr.INVALID_FOLDER
        # create new source
        appid = self.act.dict['PassiveParty']
        source = Source.create(appid)
        folder_file = FolderFile.create(
            appid, file_name, Folder(appid, current_folder), source)
        if len(folder_file.key.encode(default.CODING)) > 1000:
            return CSCommonErr.INVALID_NAME
        oss = OSS(intranet=True, extranet=True)
        put_result = self.__folder_file(folder_file, headers, True, oss)
        if put_result is not None:
            return put_result
        url = oss.sign_url('PUT', source.key,
                           default.UPLOAD_URL_EXPIRES,
                           headers=headers, intranet=intranet)
        return {
            'errcode': 0,
            'url': url,
            'headers': headers,
            'source': source.suffix,
            'folder_file': folder_file.suffix,
        }

    def folder_file(self, current_folder, file_name, folder_file, source_file):
        """
        :param str current_folder: Eg: folder/.../,t=${CreateTime}&n=${FolderName}&i=${FolderId}
        :param str file_name: Filename
        :param str or None folder_file: Eg: folder/${FolderId}/.../t=${CreateTime}&n=${FileName}&i=${FileId}
        :param str or None source_file: Eg: source/${FileId}.source.cs
        :return:
        """
        if not Check.file_name(file_name):
            return CSCommonErr.INVALID_NAME
        if not current_folder.startswith('folder/'):
            return CSCommonErr.INVALID_FOLDER
        if not current_folder.startswith('source/'):
            return CSCommonErr.INVALID_SOURCE
        appid = self.act.dict['PassiveParty']
        if source_file is not None:
            source = Source(appid, suffix=source_file)
        else:
            source = FolderFile(appid, suffix=folder_file).source
        folder_file = FolderFile.create(
            appid, file_name,
            Folder(appid, current_folder), source)
        put_result = self.__folder_file(folder_file)
        if put_result is not None:
            return put_result
        return {
            'errcode': 0,
            'source': folder_file.source.suffix,
            'folder_file': folder_file.suffix,
        }
