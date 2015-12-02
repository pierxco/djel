# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class Http302(Exception):
    def __init__(self, url, message=''):
        super(Http302, self).__init__(message)
        self.url = url
        self.message = message
