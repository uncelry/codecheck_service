from rest_framework.routers import DefaultRouter
from repos.views import FileViewSet, UserFilesListView
from django.urls import path, include

router = DefaultRouter()
router.register(r'files', FileViewSet, basename='files')

urlpatterns = [
    # path('files/', UserFilesListView.as_view(), name='files-list'), # GET /api/files/
    path('', include(router.urls)),
]
