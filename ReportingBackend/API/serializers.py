from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Salle, User_Salle

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            # Since USERNAME_FIELD = 'email', Django will look up the user by email,
            # but authenticate() expects the parameter to be named 'username'
            user = authenticate(request=self.context.get('request'), 
                               username=email,  # Using 'username' parameter which maps to email
                               password=password)
            
            if not user:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
        else:
            raise serializers.ValidationError('Must include "email" and "password".')

        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    admin_creator = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id_user', 'email', 'name', 'phone', 'is_admin', 'is_active', 'last_login', 'admin_creator', 'date_creation']
        read_only_fields = ['id_user', 'last_login', 'admin_creator', 'date_creation']
    
    def get_admin_creator(self, obj):
        if obj.admin_creator:
            return {
                'id_user': obj.admin_creator.id_user,
                'name': obj.admin_creator.name
            }
        return None


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['id_user', 'email', 'name', 'phone', 'password', 'is_admin']
        read_only_fields = ['id_user']  # Make id_user read-only
    
    def create(self, validated_data):
        # Get the admin user who is creating this account
        admin_user = self.context['request'].user
        
        # Create user with the admin as creator
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            phone=validated_data.get('phone', ''),
            password=validated_data['password'],
            is_admin=validated_data.get('is_admin', False),
            admin_creator=admin_user
        )
        return user
    
    def to_representation(self, instance):
        
        #Customize the response data after user creation
        representation = super().to_representation(instance)
        representation['id_user'] = instance.id_user
        return representation


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    admin_creator = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id_user', 'email', 'name', 'phone', 'password', 'is_admin', 'is_active', 'admin_creator', 'date_creation']
        read_only_fields = ['id_user', 'admin_creator', 'date_creation']
    
    def get_admin_creator(self, obj):
        if obj.admin_creator:
            return {
                'id_user': obj.admin_creator.id_user,
                'name': obj.admin_creator.name
            }
        return None
    
    def update(self, instance, validated_data):
        # Handle password separately
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
    

class SalleSerializer(serializers.ModelSerializer):
    admin_creator = serializers.SerializerMethodField()
    
    class Meta:
        model = Salle
        fields = ['id_salle', 'name', 'phone', 'date_creation', 'admin_creator']
        read_only_fields = ['id_salle', 'date_creation', 'admin_creator']
    
    def get_admin_creator(self, obj):
        if obj.admin_creator:
            return {
                'id_user': obj.admin_creator.id_user,
                'name': obj.admin_creator.name
            }
        return None


class SalleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salle
        fields = ['name', 'phone']
    
    def create(self, validated_data):
        # Get the admin user who is creating this salle
        admin_user = self.context['request'].user
        
        # Create salle with the admin as creator
        salle = Salle.objects.create(
            name=validated_data['name'],
            phone=validated_data.get('phone', ''),
            admin_creator=admin_user
        )
        return salle

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id_salle'] = instance.id_salle
        return representation


class UserSalleLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Salle
        fields = ['id', 'id_user', 'id_salle', 'date_creation', 'admin_creator']
        read_only_fields = ['id', 'date_creation', 'admin_creator']
    
    def validate(self, data):
        # Check if the link already exists
        if User_Salle.objects.filter(id_user=data['id_user'], id_salle=data['id_salle']).exists():
            raise serializers.ValidationError("This user is already linked to this salle.")
        return data
    
    def create(self, validated_data):
        # Get the admin user who is creating this link
        admin_user = self.context['request'].user
        
        # Create the link with the admin as creator
        link = User_Salle.objects.create(
            id_user=validated_data['id_user'],
            id_salle=validated_data['id_salle'],
            admin_creator=admin_user
        )
        return link


class UserSalleListSerializer(serializers.ModelSerializer):
    admin_creator = serializers.SerializerMethodField()
    id_user = serializers.SerializerMethodField()
    id_salle = serializers.SerializerMethodField()
    
    class Meta:
        model = User_Salle
        fields = ['id', 'admin_creator', 'id_user', 'id_salle', 'date_creation']
    
    def get_admin_creator(self, obj):
        return {
            'id_user': obj.admin_creator.id_user,
            'name': obj.admin_creator.name
        }
    
    def get_id_user(self, obj):
        return {
            'id_user': obj.id_user.id_user,
            'name': obj.id_user.name
        }
    
    def get_id_salle(self, obj):
        return {
            'id_salle': obj.id_salle.id_salle,
            'name': obj.id_salle.name
        }