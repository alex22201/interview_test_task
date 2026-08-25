from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView

from redirects.models import RedirectRule
from redirects.serializers import RedirectRuleSerializer


class RedirectRuleViewSet(viewsets.ModelViewSet):
    """CRUD for RedirectRule, scoped to the authenticated user's own rules.

    Ownership is enforced by get_queryset() alone: another user's rule is simply not
    in the queryset, so it answers 404 without disclosing that the rule exists.
    """

    queryset = RedirectRule.objects.all()
    serializer_class = RedirectRuleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class BaseRedirectView(APIView):
    """Resolves a redirect rule by its identifier and answers with a 302.

    Subclasses set `is_private` to pick which visibility of rule they serve and
    `permission_classes` to control who may follow it.
    """

    is_private: bool

    def get(self, request: Request, redirect_identifier: str) -> HttpResponseRedirect:
        rule = get_object_or_404(
            RedirectRule,
            redirect_identifier=redirect_identifier,
            is_private=self.is_private,
        )
        return HttpResponseRedirect(rule.redirect_url)


@extend_schema(
    summary="Follow a public redirect",
    description="Redirects to the rule's target URL. No authentication required.",
    responses={
        302: OpenApiResponse(description="Redirect to the rule's target URL."),
        404: OpenApiResponse(description="No public rule with this identifier."),
    },
)
class PublicRedirectView(BaseRedirectView):
    """GET /redirect/public/<redirect_identifier> -> 302 to the target URL."""

    permission_classes = [AllowAny]
    is_private = False


@extend_schema(
    summary="Follow a private redirect",
    description="Redirects to the rule's target URL. Requires a valid JWT.",
    responses={
        302: OpenApiResponse(description="Redirect to the rule's target URL."),
        401: OpenApiResponse(description="Missing or invalid JWT."),
        404: OpenApiResponse(description="No private rule with this identifier."),
    },
)
class PrivateRedirectView(BaseRedirectView):
    """GET /redirect/private/<redirect_identifier> -> 302, requires a valid JWT."""

    permission_classes = [IsAuthenticated]
    is_private = True
