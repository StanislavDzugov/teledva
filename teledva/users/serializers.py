from django.contrib.auth import password_validation
from rest_framework import serializers

from .models import CustomUser, Company


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        exclude = ('password', 'is_superuser', 'is_staff')
        read_only_fiedls = (
            'username', 'is_active', 'date_joined', 'last_login', 
        )


class CompanySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Company
        fields = '__all__'


class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'password', 'first_name', 'last_name',
            'is_active', 'date_joined', 'last_login', 'is_superuser', 'is_staff'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }
        read_only_fiedls = (
            'is_active', 'date_joined', 'last_login', 'is_superuser', 'is_staff' 
        )

    def create(self, validated_data):
        validated_data['is_active'] = True
        return CustomUser.objects.create_user(**validated_data)


class UpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=255, required=True)
    new_password = serializers.CharField(max_length=255, required=True)

    def validate(self, attrs):
        user = self.context['request'].user
        if user.check_password(attrs['old_password']) is False:
            raise serializers.ValidationError('Incorrect old password')
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError('Passwords must be different')
        attrs['user'] = user
        return attrs
    
    def validate_new_password(self, new_password):
        min_length = password_validation.MinimumLengthValidator()
        min_length.validate(new_password)
        only_numeric = password_validation.NumericPasswordValidator()
        only_numeric.validate(new_password)
        return new_password
    
    def save(self, **kwargs):
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user