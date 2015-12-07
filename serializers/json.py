# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.utils.functional import Promise
from django.utils.encoding import force_text
from django.core.serializers.json import DjangoJSONEncoder


class DjangoJSONLazyEncoder(DjangoJSONEncoder):
    """
    A JSON encoder that renders lazy translation objects.
    Taken from https://docs.djangoproject.com/en/1.8/topics/serialization/#serialization-formats-json
    """
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(DjangoJSONLazyEncoder, self).default(obj)
