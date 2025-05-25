from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
{%- if cookiecutter.use_async == 'y' %}
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
{%- endif %}
from django.urls import include
from django.urls import path
{%- if cookiecutter.use_drf == 'y' %}
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token
{%- endif %}

urlpatterns = [
    # Django Admin, use {% raw %}{% url 'admin:index' %}{% endraw %}
    path(settings.ADMIN_URL, admin.site.urls),
    # Media files
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
{%- if cookiecutter.use_async == 'y' %}
if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()
{%- endif %}
{% if cookiecutter.use_drf == 'y' %}
# API URLS
urlpatterns += [
    # API base url
    path("api/users/", include("{{ cookiecutter.project_slug }}.users.urls", namespace="users")),
    # DRF auth
    {%- if cookiecutter.use_jwt_auth == 'y' %}
    # dj-rest-auth URLs
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),
    {%- else %}
    path("api/auth-token/", obtain_auth_token, name="obtain_auth_token"),
    {%- endif %}
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
]

{%- if cookiecutter.use_jwt_auth == 'y' and cookiecutter.use_social_auth == 'y' %}
# Social Auth URLs
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.social_serializers import TwitterLoginSerializer

{%- if cookiecutter.social_auth_providers == 'Google' or cookiecutter.social_auth_providers == 'All' %}
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:8000/accounts/google/login/callback/"
    client_class = OAuth2Client
{%- endif %}

{%- if cookiecutter.social_auth_providers == 'Facebook' or cookiecutter.social_auth_providers == 'All' %}
class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
{%- endif %}

{%- if cookiecutter.social_auth_providers == 'Twitter' or cookiecutter.social_auth_providers == 'All' %}
class TwitterLogin(SocialLoginView):
    adapter_class = TwitterOAuthAdapter
    serializer_class = TwitterLoginSerializer
{%- endif %}

{%- if cookiecutter.social_auth_providers == 'Apple' or cookiecutter.social_auth_providers == 'All' %}
class AppleLogin(SocialLoginView):
    adapter_class = AppleOAuth2Adapter
    callback_url = "http://localhost:8000/accounts/apple/login/callback/"
    client_class = OAuth2Client
{%- endif %}

# Add social auth endpoints
urlpatterns += [
    {%- if cookiecutter.social_auth_providers == 'Google' or cookiecutter.social_auth_providers == 'All' %}
    path("api/auth/google/", GoogleLogin.as_view(), name="google_login"),
    {%- endif %}
    {%- if cookiecutter.social_auth_providers == 'Facebook' or cookiecutter.social_auth_providers == 'All' %}
    path("api/auth/facebook/", FacebookLogin.as_view(), name="facebook_login"),
    {%- endif %}
    {%- if cookiecutter.social_auth_providers == 'Twitter' or cookiecutter.social_auth_providers == 'All' %}
    path("api/auth/twitter/", TwitterLogin.as_view(), name="twitter_login"),
    {%- endif %}
    {%- if cookiecutter.social_auth_providers == 'Apple' or cookiecutter.social_auth_providers == 'All' %}
    path("api/auth/apple/", AppleLogin.as_view(), name="apple_login"),
    {%- endif %}
]
{%- endif %}
{%- endif %}

if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
        *urlpatterns,
    ]
