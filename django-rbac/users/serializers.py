from rest_framework import serializers
from .models import User

# Show the User model without exposing the password field
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id_user', 'username', 'email', 'firstname', 'lastname', 'role')

# Serializer for user registration
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id_user', 'lastname', 'firstname', 'username', 'email', 'role', 'password']

    def create(self, validated_data):
       # Create a new user instance with the provided validated data.
       # The password is hashed before saving.
        
        user = User.objects.create_user(
            lastname=validated_data['lastname'],
            firstname=validated_data['firstname'],
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            role=validated_data.get('role', 'USER')
        )

        return user
    
    