from rest_framework import serializers
from .models import Exam
from apps.subject.models import Subject

# 1. 생성용 (POST)
class ExamCreateSerializer(serializers.ModelSerializer):
    thumbnail_img = serializers.ImageField(write_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'title', 'subject_id', 'thumbnail_img', 'thumbnail_img_url']
        read_only_fields = ['id', 'thumbnail_img_url']

    def create(self, validated_data):
        thumbnail_img = validated_data.pop('thumbnail_img')
        # S3 업로드 경로 예시 (요구사항 반영)
        validated_data['thumbnail_img_url'] = f"https://oz-externship.s3.ap-northeast-2.amazonaws.com/exams/{thumbnail_img.name}"
        return super().create(validated_data)

# 2. 목록 조회용 (GET List)
class ExamListSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject_id.title', read_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'title', 'subject_name', 'created_at', 'updated_at']

# 3. 상세 조회용 (GET Detail)
class ExamDetailSerializer(serializers.ModelSerializer):
    subject = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = ['id', 'title', 'subject', 'thumbnail_img_url', 'created_at', 'updated_at']

    def get_subject(self, obj):
        return {"id": obj.subject_id.id, "title": obj.subject_id.title}

# 4. 수정용 (PUT)
class ExamUpdateSerializer(serializers.ModelSerializer):
    thumbnail_img = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Exam
        fields = ['id', 'title', 'subject_id', 'thumbnail_img', 'thumbnail_img_url']
        read_only_fields = ['id', 'thumbnail_img_url']

    def update(self, instance, validated_data):
        thumbnail_img = validated_data.pop('thumbnail_img', None)
        if thumbnail_img:
            instance.thumbnail_img_url = f"https://oz-externship.s3.ap-northeast-2.amazonaws.com/exams/{thumbnail_img.name}"
        return super().update(instance, validated_data)

class ExamDeleteRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id']