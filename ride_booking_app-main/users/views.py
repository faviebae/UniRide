from datetime import timezone

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import logout
from .models import User, DriverProfile, StudentProfile
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    DriverProfileSerializer, StudentProfileSerializer
)

class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Logged out successfully"})

class UserProfileView(APIView):
    def get(self, request):
        user = request.user
        user_data = UserSerializer(user).data
        
        if user.is_driver and hasattr(user, 'driver_profile'):
            user_data['driver_profile'] = DriverProfileSerializer(user.driver_profile).data
        elif user.is_student and hasattr(user, 'student_profile'):
            user_data['student_profile'] = StudentProfileSerializer(user.student_profile).data
        
        return Response(user_data)
    
    def patch(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DriverLocationUpdateView(APIView):
    """Update driver's current location"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if not request.user.is_driver:
            return Response({"error": "Only drivers can update location"}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        
        if not latitude or not longitude:
            return Response({"error": "Latitude and longitude required"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        profile = request.user.driver_profile
        profile.current_latitude = latitude
        profile.current_longitude = longitude
        profile.last_location_update = timezone.now()
        profile.save()
        
        # Broadcast location update via WebSocket
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"driver_{request.user.id}",
            {
                'type': 'location_update',
                'latitude': latitude,
                'longitude': longitude,
            }
        )
        
        return Response({"message": "Location updated"})