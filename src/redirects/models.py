import uuid

from django.conf import settings
from django.db import models

from redirects.utils import generate_redirect_identifier


class RedirectRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="redirect_rules",
    )
    redirect_url = models.URLField()
    is_private = models.BooleanField(default=False)
    redirect_identifier = models.CharField(
        max_length=16,
        unique=True,
        editable=False,
        blank=True,
    )

    class Meta:
        ordering = ["-created"]

    def __str__(self) -> str:
        return f"{self.redirect_identifier} -> {self.redirect_url}"

    def save(self, *args, **kwargs):
        if not self.redirect_identifier:
            self.redirect_identifier = self._generate_unique_identifier()
        super().save(*args, **kwargs)

    @classmethod
    def _generate_unique_identifier(cls) -> str:
        identifier = generate_redirect_identifier()
        while cls.objects.filter(redirect_identifier=identifier).exists():
            identifier = generate_redirect_identifier()
        return identifier
