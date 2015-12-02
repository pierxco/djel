# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponseRedirect

from djel.exceptions import Http302


class Http302Middleware(object):
    """
    Catch Http302 exception and redirect user
    """

    def process_exception(self, request, exception):
        if isinstance(exception, Http302):
            return HttpResponseRedirect(exception.url)
        return None
