from django.contrib import admin

from redirects.models import RedirectRule


@admin.register(RedirectRule)
class RedirectRuleAdmin(admin.ModelAdmin):
    list_display = ("redirect_identifier", "redirect_url", "owner", "is_private", "created")
    list_filter = ("is_private",)
    search_fields = ("redirect_identifier", "redirect_url", "owner__username")
    readonly_fields = ("id", "redirect_identifier", "created", "modified")
