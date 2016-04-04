# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.admin import ModelAdmin
from django.contrib.admin import site
from django.contrib.admin.sites import AdminSite
from django.core.urlresolvers import reverse
from django.utils.encoding import force_unicode

from .widgets import VerboseForeignKeyRawIdWidget, VerboseManyToManyRawIdWidget


def get_empty_value_display(model_admin):
    if hasattr(model_admin, 'get_empty_value_display'):
        return model_admin.get_empty_value_display()
    else:
        # Django < 1.9
        from django.contrib.admin.views.main import EMPTY_CHANGELIST_VALUE
        return EMPTY_CHANGELIST_VALUE


def fk_link_method(fieldname, description, format_anchor_text_func=force_unicode, admin_order_field=True,
                   add_filter=False, query_param_key=None):
    def f(self, obj):
        field = getattr(obj, fieldname)
        if field is not None:
            url = reverse('admin:{}_{}_change'.format(field._meta.app_label, field._meta.model_name), args=(field.pk,))
            link = u'<b><a href="{}">{}</a></b>'.format(url, format_anchor_text_func(field))
            ajax_link = '<a href="{}?_popup=1" class="ajax-link"></a>'.format(url)
            if add_filter:
                if query_param_key:
                    filter_link = u'<span data-param="{}={}" class="filter-link"></span>'.format(query_param_key,
                                                                                                 field.pk)
                else:
                    filter_link = u'<span data-param="{}__id__exact={}" class="filter-link"></span>'.format(fieldname,
                                                                                                            field.pk)
                return link + '<div class="popup-filter">' + ajax_link + filter_link + '</div>'
            return link + ajax_link
        else:
            return get_empty_value_display(self)


    f.allow_tags = True
    f.short_description = description
    if admin_order_field:
        f.admin_order_field = fieldname if isinstance(admin_order_field, bool) else admin_order_field
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


class ModelAdminWithVerboseRawId(ModelAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in self.raw_id_fields:
            kwargs.pop("request", None)
            field_type = db_field.rel.__class__.__name__
            if field_type == "ManyToOneRel":
                kwargs['widget'] = VerboseForeignKeyRawIdWidget(db_field.rel, site)
            elif field_type == "ManyToManyRel":
                kwargs['widget'] = VerboseManyToManyRawIdWidget(db_field.rel, site)
            return db_field.formfield(**kwargs)
        return super(ModelAdminWithVerboseRawId, self).formfield_for_dbfield(db_field, **kwargs)
