from rest_framework import serializers
from repos.models import SourceFile
from checks.serializers import CheckLogSerializer

class FileListSerializer(serializers.ModelSerializer):
    last_check = serializers.DateTimeField(required=False)
    status = serializers.CharField()

    class Meta:
        model = SourceFile
        fields = ('id', 'filename', 'last_check', 'status')

class FileDetailSerializer(serializers.ModelSerializer):
    checks = serializers.SerializerMethodField()

    class Meta:
        model = SourceFile
        fields = ('id','filename','file','uploaded_at','status','last_check','checks')

    def get_checks(self, obj):
        # Avoid circular import at top-level
        from checks.models import CheckLog
        from checks.serializers import CheckLogSerializer
        logs = CheckLog.objects.filter(source_file=obj).order_by('-created_at')
        return CheckLogSerializer(logs, many=True).data

class FileUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)

    class Meta:
        model = SourceFile
        fields = ('file',)

    def validate_file(self, value):
        name = value.name
        if not name.endswith('.py'):
            raise serializers.ValidationError('Only .py files are allowed')
        return value

    def create(self, validated_data):
        request = self.context['request']
        f = validated_data['file']
        obj = SourceFile.objects.create(
            owner=request.user,
            file=f,
            filename=f.name,
            status='new'
        )
        return obj
