from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True, 
        allow_blank=False,
        max_length=150,
        trim_whitespace=True
    )
    password = serializers.CharField(
        required=True, 
        write_only=True,
        max_length=128
    )
