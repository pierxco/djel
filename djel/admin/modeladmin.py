# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.admin.views.main import EMPTY_CHANGELIST_VALUE
from django.core.urlresolvers import reverse
from django.utils.encoding import force_unicode


def fk_link_method(fieldname, description):
    def f(self, obj):
        field = getattr(obj, fieldname)
        if field is not None:
            url = reverse('admin:{}_{}_change'.format(field._meta.app_label, field._meta.model_name), args=(field.pk,))
            link = u'<b><a href="{}">{}</a></b>'.format(url, force_unicode(field))
            ajax_link = '<a href="{}?_popup=1" class="ajax-link"></a>'.format(url)
            return link + ajax_link
        else:
            return EMPTY_CHANGELIST_VALUE
    f.allow_tags = True
    f.short_description = description
    f.admin_order_field = fieldname
    return f


class ReadOnlyAdminMixin(object):
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return super(ReadOnlyAdminMixin, self).get_readonly_fields(request=request, obj=obj)
        else:
            model_fields = [f.name for f in self.model._meta.fields]
            for f in self.readonly_fields:
                if f not in model_fields:
                    model_fields.append(f)
            return model_fields

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return super(ReadOnlyAdminMixin, self).has_add_permission(request)
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return super(ReadOnlyAdminMixin, self).has_delete_permission(request=request, obj=obj)
        else:
            return False


