# -*- coding: utf-8 -*-
# API
# FileName: main.py
# Version: 1.0.0
# Create: 2018-10-13
# Modify: 2018-10-25
import act


MySQL = act.MySQL(
    'root',
    'PASSWORD',
    db='DATABASE',
    table_name='ActAuth')
OTS = act.OTS(
    '',
    '',
    'endpoint',
    'instance_name',
    table_name='Act')
RequestAuth = act.RequestAuth(OTS, MySQL)


@act.Response.django
def request_auth(view_func):
    """
    :param function view_func:
    :return: wrapped_view
    """

    @RequestAuth.django
    def wrapped_view(request, auth, *args, **kwargs):
        if act.Format.get(auth, 'errcode') == 0:
            get = dict(request.GET)
            post = dict(request.POST)
            return view_func(request, auth, get, post, *args, **kwargs)
        elif act.Format.get(auth, 'errcode', -1) < 0:
            return act.CommonErr.SYS_BUSY
        else:
            return auth

    return wrapped_view
