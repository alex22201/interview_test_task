from django.urls import path
from rest_framework.routers import DefaultRouter

from redirects.views import PrivateRedirectView, PublicRedirectView, RedirectRuleViewSet

router = DefaultRouter()
router.register("url", RedirectRuleViewSet, basename="redirect-rule")

urlpatterns = [
    path(
        "redirect/public/<str:redirect_identifier>",
        PublicRedirectView.as_view(),
        name="redirect-public",
    ),
    path(
        "redirect/private/<str:redirect_identifier>",
        PrivateRedirectView.as_view(),
        name="redirect-private",
    ),
    *router.urls,
]
