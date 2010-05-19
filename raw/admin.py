from django.contrib import admin
from models import *


class HistoryInline(admin.TabularInline):
    model = ParseHistory
    extra = 1


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [HistoryInline]


admin.site.register(Group, GroupAdmin)