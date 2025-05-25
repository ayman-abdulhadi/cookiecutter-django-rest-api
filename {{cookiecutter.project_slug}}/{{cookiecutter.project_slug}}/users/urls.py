from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter
from django.conf import settings

from .views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()
router.register("", UserViewSet)

app_name = "users"
urlpatterns = router.urls
