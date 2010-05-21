from django.contrib import admin
from models import *


class HistoryInline(admin.TabularInline):
    model = ParseHistory
    extra = 1


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [HistoryInline]


class PostFilterAdmin(admin.ModelAdmin):
    list_display = ('regex',)


admin.site.register(Group, GroupAdmin)
admin.site.register(PostFilter, PostFilterAdmin)