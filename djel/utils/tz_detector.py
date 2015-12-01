# Adapted from https://github.com/adamcharnock/django-tz-detect
#
# Copyright (c) 2012 Adam Charnock
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.


from datetime import datetime
from itertools import chain
from django.conf import settings
import pytz


TZ_DETECT_TIMEZONES = getattr(settings, 'TZ_DETECT_TIMEZONES',
                              ('Australia/Sydney', 'Asia/Tokyo'))

TZ_DETECT_COUNTRIES = getattr(settings, 'TZ_DETECT_COUNTRIES',
                              ('AU', 'CN', 'US', 'BR', 'RU', 'GB'))


def get_prioritized_timezones(country_hints=None):
    country_hints = country_hints or []
    def tz_gen():
        yield TZ_DETECT_TIMEZONES
        for c in country_hints:
            yield pytz.country_timezones(c)
        for c in TZ_DETECT_COUNTRIES:
            yield pytz.country_timezones(c)
        yield pytz.common_timezones
    return chain.from_iterable(tz_gen())


def offset_to_timezone(offset, country_hints=None):
    """Convert a minutes offset (JavaScript-style) into a pytz timezone"""
    closest_tz = None
    closest_delta = 1440

    # JS offsets are flipped and can be negative, so
    # unflip and put into range 0 - 1440
    user_offset = (offset * -1)
    user_offset = (user_offset + 1440) % 1440

    for tz_name in get_prioritized_timezones(country_hints):
        try:
            tz = pytz.timezone(tz_name)
        except KeyError:
            continue
        tz_offset = datetime.now(tz=tz).utcoffset().seconds / 60
        delta = tz_offset - user_offset
        if abs(delta) < abs(closest_delta):
            closest_tz = tz
            closest_delta = delta
            if delta == 0:
                break
    return closest_tz


def safe_offset_to_timezone_name(offset_str, country_hint=''):
    # takes a string, and returns a string of the timezone name. Returns empty string on error
    try:
        offset = int(offset_str)
        tz = offset_to_timezone(offset, [country_hint])
        if tz:
            return tz.zone
    except ValueError:
        pass
    return ''
