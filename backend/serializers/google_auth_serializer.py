from rest_framework import serializers


class GoogleSignInSerializer(serializers.Serializer):
    id_token = serializers.CharField(required=True)


class GoogleRegistrationSerializer(serializers.Serializer):
    sub = serializers.CharField(required=True, help_text="Google user ID (sub claim)")
    email = serializers.EmailField(required=True)
    dni = serializers.CharField(required=True, min_length=7, max_length=9, help_text="DNI del usuario")
    padron = serializers.CharField(required=False, min_length=5, max_length=7, help_text="Padrón (solo estudiantes)")
    is_student = serializers.BooleanField(default=True)
    is_teacher = serializers.BooleanField(default=False)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        is_student = attrs.get('is_student', False)
        is_teacher = attrs.get('is_teacher', False)
        padron = attrs.get('padron')

        if not is_student and not is_teacher:
            raise serializers.ValidationError("El usuario debe ser estudiante o docente")

        if is_student and not padron:
            raise serializers.ValidationError({'padron': 'El padrón es obligatorio para estudiantes'})

        if padron and not padron.isdigit():
            raise serializers.ValidationError({'padron': 'El padrón debe contener solo números'})

        return attrs