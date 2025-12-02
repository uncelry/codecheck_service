from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from repos.models import SourceFile
from repos.serializers import FileListSerializer, FileDetailSerializer, FileUploadSerializer
from checks.tasks import trigger_check_for_file
from django.shortcuts import get_object_or_404

class UserFilesListView(generics.ListAPIView):
    serializer_class = FileListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SourceFile.objects.filter(owner=self.request.user, deleted=False)

class FileViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet used to create, retrieve, destroy and custom action to re-run check.
    """
    queryset = SourceFile.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    # set serializer dynamically
    def get_serializer_class(self):
        if self.action == 'create':
            return FileUploadSerializer
        if self.action in ['list']:
            return FileListSerializer
        return FileDetailSerializer

    def get_queryset(self):
        return SourceFile.objects.filter(owner=self.request.user)

    def perform_destroy(self, instance):
        # soft-delete
        instance.mark_deleted()

    def create(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        # schedule check
        trigger_check_for_file.delay(obj.id)
        return Response(FileDetailSerializer(obj, context={'request': request}).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        return Response(FileDetailSerializer(obj, context={'request': request}).data)

    def partial_update(self, request, *args, **kwargs):
        # allow re-upload (replace file)
        obj = self.get_object()
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            if not uploaded_file.name.endswith('.py'):
                return Response({'detail': 'Only .py allowed'}, status=400)
            obj.file.delete(save=False)
            obj.file = uploaded_file
            obj.filename = uploaded_file.name
            obj.replaced = True
            obj.status = 'new'
            obj.save()
            # schedule a new check
            trigger_check_for_file.delay(obj.id)
            return Response(FileDetailSerializer(obj, context={'request': request}).data)
        return super().partial_update(request, *args, **kwargs)

    # custom action: POST to /api/files/{id}/rerun to trigger re-check via default router -> use extra action
    from rest_framework.decorators import action

    @action(detail=True, methods=['post'])
    def rerun(self, request, pk=None):
        obj = self.get_object()
        if obj.owner != request.user:
            return Response({"result":"failed", "message":"have no access to this file"}, status=403)
        # schedule task
        trigger_check_for_file.delay(obj.id)
        return Response({"result":"ok","message":"file under testing"})
