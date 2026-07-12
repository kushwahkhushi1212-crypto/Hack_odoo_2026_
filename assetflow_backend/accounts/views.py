from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .permissions import IsOrgAdmin
from .serializers import (
    ChangeRoleSerializer, EmployeeSerializer, SignupSerializer,
)

User = get_user_model()


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Allows the AssetFlow login form (email + password) to obtain a JWT pair."""
    username_field = User.USERNAME_FIELD

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = EmployeeSerializer(self.user).data
        return data


class LoginView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class SignupView(generics.CreateAPIView):
    """POST /api/auth/signup/ — public, creates an employee profile."""
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    """GET/PATCH /api/auth/me/ — the logged-in employee's own profile."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(EmployeeSerializer(request.user).data)

    def patch(self, request):
        serializer = EmployeeSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    Full employee directory management — used by the "Employee" tab in
    Organization Setup. Read is open to any authenticated user (needed for
    the transfer / allocation "To" dropdown); writes are admin-only.
    """
    queryset = User.objects.select_related('department').all()
    serializer_class = EmployeeSerializer
    filterset_fields = ['department', 'role', 'is_active_employee']
    search_fields = ['first_name', 'last_name', 'email', 'employee_id']

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [IsOrgAdmin()]

    def get_serializer_class(self):
        return EmployeeSerializer


class ChangeRoleView(APIView):
    """PATCH /api/auth/employees/<id>/role/ — admin promotes/demotes a user."""
    permission_classes = [IsOrgAdmin]

    def patch(self, request, pk):
        user = generics.get_object_or_404(User, pk=pk)
        serializer = ChangeRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.role = serializer.validated_data['role']
        user.save(update_fields=['role'])
        return Response(EmployeeSerializer(user).data, status=status.HTTP_200_OK)
