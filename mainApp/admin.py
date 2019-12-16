from django.apps import apps
from django.contrib import admin

app = apps.get_app_config('mainApp')

admin.site.site_header = 'SIH Overdrive Admin Dashboard'
admin.site.index_title = 'SIH Overdrive Admin Dashboard'
admin.site.site_title = 'Welcome to SIH Overdrive Admin Dashboard'

inlines = {
}
extraFields = {
}
removeFields = {
}
searchFields = {
}


def has_delete_permission(self, request, obj=None):
    return False


def class_dict(model_name, model):
    model_name = model_name.lower()
    listField = ()
    filterFields = ()
    fields = model._meta.fields
    if model_name in removeFields:
        remove = removeFields[model_name]
    else:
        remove = ()
    for field in fields:
        filterFields = filterFields + (field.name,)
        if field.name not in remove:
            listField = listField + (field.name,)
    if model_name in extraFields:
        listField = listField + extraFields[model_name]
    fields = {'list_display': listField}
    if model_name in inlines:
        fields['inlines'] = inlines[model_name]
    if model_name in searchFields:
        fields['search_fields'] = searchFields[model_name]
    fields['list_filter'] = filterFields
    fields['has_delete_permission'] = has_delete_permission
    return fields


for model_name, model in app.models.items():
    model_admin = type(model_name + "Admin", (admin.ModelAdmin,), class_dict(model_name, model))
    admin.site.register(model, model_admin)
