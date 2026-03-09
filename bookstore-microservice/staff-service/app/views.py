from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate

from .models import Staff, StaffActivity
from .serializers import StaffSerializer, StaffLoginSerializer, StaffActivitySerializer


class StaffLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = StaffLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user and isinstance(user, Staff):
                # Log activity
                StaffActivity.objects.create(
                    staff=user,
                    action='login',
                    description='Đăng nhập hệ thống',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                return Response({
                    'message': 'Đăng nhập thành công',
                    'staff': StaffSerializer(user).data
                })
            return Response(
                {'error': 'Tên đăng nhập hoặc mật khẩu không đúng'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StaffListView(APIView):
    def get(self, request):
        role = request.query_params.get('role')
        staffs = Staff.objects.all()
        
        if role:
            staffs = staffs.filter(role=role)
        
        serializer = StaffSerializer(staffs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = StaffSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StaffDetailView(APIView):
    def get(self, request, pk):
        try:
            staff = Staff.objects.get(pk=pk)
            serializer = StaffSerializer(staff)
            return Response(serializer.data)
        except Staff.DoesNotExist:
            return Response({'error': 'Không tìm thấy'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            staff = Staff.objects.get(pk=pk)
            serializer = StaffSerializer(staff, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Staff.DoesNotExist:
            return Response({'error': 'Không tìm thấy'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            staff = Staff.objects.get(pk=pk)
            staff.is_active_staff = False
            staff.is_active = False
            staff.save()
            return Response({'message': 'Đã vô hiệu hóa nhân viên'})
        except Staff.DoesNotExist:
            return Response({'error': 'Không tìm thấy'}, status=status.HTTP_404_NOT_FOUND)


class StaffActivityView(APIView):
    def get(self, request, staff_id):
        activities = StaffActivity.objects.filter(staff_id=staff_id)[:50]
        serializer = StaffActivitySerializer(activities, many=True)
        return Response(serializer.data)


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'status': 'healthy', 'service': 'staff-service'})
