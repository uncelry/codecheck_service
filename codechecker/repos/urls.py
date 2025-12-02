from rest_framework.routers import DefaultRouter
from repos.views import FileViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'files', FileViewSet, basename='files')

urlpatterns = [
    path('', include(router.urls)),
]
