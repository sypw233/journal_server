from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username','password', 'email', 'phone', 'user_type', 'last_data_sync_time', 'register_time']
        extra_kwargs = {
            'password': {'write_only': True},
            'last_sync_time': {'read_only': True},
            'register_time': {'read_only': True},
        }
    
    def create(self, validated_data):
        print(validated_data)
        if 'password' not in validated_data:
            raise serializers.ValidationError({'password': 'This field is required.'})
            
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email'),
            phone=validated_data.get('phone'),
            user_type=validated_data.get('user_type', 1)
        )
        return user