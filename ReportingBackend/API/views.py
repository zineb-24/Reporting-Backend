from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from .serializers import LoginSerializer, UserSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics, permissions
from .serializers import (UserCreateSerializer, UserUpdateSerializer, SalleSerializer, 
                          SalleCreateSerializer, UserSalleLinkSerializer, UserSalleListSerializer)
from .models import User, Salle, User_Salle
from django.contrib.auth.hashers import check_password


class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Update last_login timestamp
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        login(request, user)
        
        # Create or get token
        token, created = Token.objects.get_or_create(user=user)
        
        # Create response with token and redirect information
        response_data = {
            'token': token.key,
            'user_id': user.id_user,
            'email': user.email,
            'is_admin': user.is_admin,
            'redirect_url': 'api/admin-dashboard/' if user.is_admin else 'api/user-dashboard/'
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class UserDashboardView(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request):

        # Debug prints
        #print(f"Auth: {request.auth}")
        #print(f"User: {request.user}")
        #print(f"Headers: {request.headers}")

        if request.user.is_admin:
            return Response({
                'error': 'Unauthorized access',
                'redirect': 'api/admin-dashboard/'
            }, status=status.HTTP_403_FORBIDDEN)
            
        user_data = UserSerializer(request.user).data
        return Response({
            'message': 'User Dashboard',
            'user': user_data
        })


class AdminDashboardView(APIView):
    authentication_classes = [TokenAuthentication]
    
    def get(self, request):
        if not request.user.is_admin:
            return Response({
                'error': 'Unauthorized access',
                'redirect': '/user-dashboard/'
            }, status=status.HTTP_403_FORBIDDEN)
            
        user_data = UserSerializer(request.user).data
        # Count total users for dashboard stats
        user_count = User.objects.filter(is_admin=False).count()
        admin_count = User.objects.filter(is_admin=True).count()
        # Count total gyms (salles)
        gym_count = Salle.objects.count()
        
        return Response({
            'message': 'Admin Dashboard',
            'user': user_data,
            'stats': {
                'regular_users': user_count,
                'admin_users': admin_count,
                'total_gyms': gym_count
            }
        })


# Create user account
class AdminUserCreateView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    #For debugging
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        print("User creation response:", response.data)
        return response
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context
    
    def perform_create(self, serializer):
        if not self.request.user.is_admin:
            raise permissions.PermissionDenied("Only admin users can create new users")
        serializer.save()


# List of All Users with possibility to filter by Admins or Regular Users
class AdminUserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if not user.is_admin:
            raise permissions.PermissionDenied("Only admin users can view user list")
        
        # Get the role filter parameter
        role_filter = self.request.query_params.get('role', None)
        queryset = User.objects.all()
        
        # Apply role filter if provided
        if role_filter is not None:
            if role_filter.lower() == 'admin':
                queryset = queryset.filter(is_admin=True)
            elif role_filter.lower() == 'user':
                queryset = queryset.filter(is_admin=False)
        
        return queryset


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    lookup_field = 'id_user'
    
    def get_object(self):
        obj = super().get_object()
        if not self.request.user.is_admin:
            raise permissions.PermissionDenied("Only admin users can manage user accounts")
        return obj
    
    def perform_destroy(self, instance):
        # Add any custom logic before deletion if needed
        # For example, prevent admins from deleting themselves
        if instance == self.request.user:
            raise permissions.PermissionDenied("You cannot delete your own account")
        instance.delete()


class AdminSalleListView(generics.ListAPIView):
    serializer_class = SalleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if not user.is_admin:
            raise permissions.PermissionDenied("Only admin users can view salle list")
        return Salle.objects.all()


class AdminSalleCreateView(generics.CreateAPIView):
    serializer_class = SalleCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context
    
    def perform_create(self, serializer):
        if not self.request.user.is_admin:
            raise permissions.PermissionDenied("Only admin users can create new salles")
        serializer.save()


class AdminSalleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SalleSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Salle.objects.all()
    lookup_field = 'id_salle'
    
    def get_object(self):
        obj = super().get_object()
        if not self.request.user.is_admin:
            raise permissions.PermissionDenied("Only admin users can manage salles")
        return obj
    
    def perform_update(self, serializer):
        if not self.request.user.is_admin:
            raise permissions.PermissionDenied("Only admin users can update salles")
        serializer.save()
    
    def perform_destroy(self, instance):
        if not self.request.user.is_admin:
            raise permissions.PermissionDenied("Only admin users can delete salles")
        instance.delete()


class AdminUserSalleLinkView(generics.CreateAPIView):
    serializer_class = UserSalleLinkSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    #For debugging
    def create(self, request, *args, **kwargs):
        print("Received link data:", request.data)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        if not self.request.user.is_admin:
            raise permissions.PermissionDenied("Only admin users can create user-salle links")
        serializer.save()
    
    
class AdminUserSalleLinkListView(generics.ListAPIView):
    serializer_class = UserSalleListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_admin:
            raise permissions.PermissionDenied("Only admin users can view user-salle links")
        
        # Filter parameters
        user_id = self.request.query_params.get('user_id', None)
        salle_id = self.request.query_params.get('salle_id', None)
        
        queryset = User_Salle.objects.all()
        
        # Apply filters if provided
        if user_id:
            queryset = queryset.filter(id_user__id_user=user_id)
        if salle_id:
            queryset = queryset.filter(id_salle__id_salle=salle_id)
            
        return queryset


class AdminUserSalleLinkDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = UserSalleListSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User_Salle.objects.all()
    lookup_field = 'id'
    
    def get_object(self):
        obj = super().get_object()
        if not self.request.user.is_admin:
            raise permissions.PermissionDenied("Only admin users can manage user-salle links")
        return obj


class AdminUserSallesView(generics.ListAPIView):
    """View to get all salles for a specific user"""
    serializer_class = SalleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_admin:
            raise permissions.PermissionDenied("Only admin users can view this information")
        
        user_id = self.kwargs.get('user_id')
        if not user_id:
            return Salle.objects.none()
            
        # Get all salles linked to this user
        return Salle.objects.filter(user_Links__id_user__id_user=user_id)


class AdminSalleUsersView(generics.ListAPIView):
    """View to get all users for a specific salle"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_admin:
            raise permissions.PermissionDenied("Only admin users can view this information")
        
        salle_id = self.kwargs.get('salle_id')
        if not salle_id:
            return User.objects.none()
            
        # Get all users linked to this salle
        return User.objects.filter(salle_Links__id_salle__id_salle=salle_id)


class AdminUserChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, id_user):
        # Check if current user is an admin
        if not request.user.is_admin:
            return Response({"error": "Only administrators can change passwords"}, 
                          status=status.HTTP_403_FORBIDDEN)
            
        user = get_object_or_404(User, id_user=id_user)
        
        new_password = request.data.get('new_password')
        
        # Validate new password
        if not new_password or len(new_password) < 6:
            return Response({"new_password": "Password must be at least 6 characters"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)