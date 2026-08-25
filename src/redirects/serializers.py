from rest_framework import serializers

from redirects.models import RedirectRule


class RedirectRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RedirectRule
        fields = [
            "id",
            "created",
            "modified",
            "redirect_url",
            "is_private",
            "redirect_identifier",
        ]
        read_only_fields = ["id", "created", "modified", "redirect_identifier"]
