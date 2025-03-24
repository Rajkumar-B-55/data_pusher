from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(
        title="Data Pusher API",
        default_version="v1",
    ),
    public=True,
    authentication_classes=[TokenAuthentication],
    permission_classes=[AllowAny],
)
urlpatterns = [
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),

    path('admin/', admin.site.urls),
    path("api/", include("core.urls")),

]
