# -*- coding: utf-8 -*-
# API
# FileName: response.py
# Version: 1.0.0
# Create: 2018-10-18
# Modify: 2018-10-18
try:
    from django.http import HttpResponse
except (ImportError, SyntaxError):
    pass
from . import util
from . import default


class FormatType:
    """
    XML: <key><![CDATA[value]]></key>
    JSON: {"key": "value"}
    """
    XML = 'XML'
    JSON = 'JSON'

    __values__ = [
        XML,
        JSON,
    ]

    __members__ = [
        'FormatType.XML',
        'FormatType.JSON',
    ]


class Response(object):
    @staticmethod
    def django(view_func):
        """
        :param function view_func:
        :return: wrapped_view
        """

        def wrapped_view(request, *args, **kwargs):
            response_format = util.Format.get(
                dict(request.POST), 'response_format', default.RESPONSE_FORMAT)
            if response_format == FormatType.JSON:
                content_type = util.ContentType.JSON
                content = util.Format.json(view_func(request, *args, **kwargs))
            else:
                content_type = util.ContentType.XML
                content = util.Format.xml(view_func(request, *args, **kwargs))
            response = HttpResponse(content)
            response['Content-Type'] = content_type
            response['Access-Control-Allow-Origin'] = default.RESPONSE_CORS
            return response

        return wrapped_view
