from rest_framework import serializers
from .models import Staff, StaffActivity


class StaffSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = Staff
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name',
                  'phone', 'avatar', 'role', 'role_display', 'department', 'address',
                  'hire_date', 'is_active_staff', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        staff = Staff(**validated_data)
        if password:
            staff.set_password(password)
        staff.save()
        return staff

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class StaffLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class StaffActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffActivity
        fields = '__all__'
