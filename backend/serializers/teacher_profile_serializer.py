from rest_framework import serializers

from backend.models import TeacherProfile, WorkExperience


class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = ['id', 'company', 'position', 'start_year', 'end_year', 'description']
        read_only_fields = ['id']


class TeacherProfileSerializer(serializers.ModelSerializer):
    work_experience = WorkExperienceSerializer(many=True)

    class Meta:
        model = TeacherProfile
        fields = ['university', 'degree', 'bio', 'current_position', 'years_of_experience', 'certifications', 'work_experience']

    def create(self, validated_data):
        work_experience_data = validated_data.pop('work_experience', [])
        profile = TeacherProfile.objects.create(**validated_data)
        WorkExperience.objects.bulk_create([
            WorkExperience(profile=profile, **item) for item in work_experience_data
        ])
        return profile

    def update(self, instance, validated_data):
        work_experience_data = validated_data.pop('work_experience', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if work_experience_data is not None:
            instance.work_experience.all().delete()
            WorkExperience.objects.bulk_create([
                WorkExperience(profile=instance, **item) for item in work_experience_data
            ])

        return instance
