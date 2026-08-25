from django.contrib import admin
from django.urls import include, path
from drf_spectacular.renderers import OpenApiJsonRenderer2
from drf_spectacular.views import SpectacularJSONAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("retrieve-token/", TokenObtainPairView.as_view(), name="retrieve-token"),
    path("refresh-token/", TokenRefreshView.as_view(), name="refresh-token"),
    # OpenApiJsonRenderer2 serves the schema as plain "application/json" so browsers
    # display it instead of downloading it as a file.
    path(
        "api/schema/",
        SpectacularJSONAPIView.as_view(renderer_classes=[OpenApiJsonRenderer2]),
        name="schema",
    ),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("", include("redirects.urls")),
]
