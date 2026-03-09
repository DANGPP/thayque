from rest_framework import serializers
from .models import Customer, CustomerProfile


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ['loyalty_points', 'total_orders', 'total_spent', 
                  'preferred_payment_method', 'preferred_shipping_address']


class CustomerSerializer(serializers.ModelSerializer):
    profile = CustomerProfileSerializer(read_only=True)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Customer
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name',
                  'phone', 'address', 'avatar', 'date_of_birth', 'is_active_customer',
                  'created_at', 'updated_at', 'profile']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        customer = Customer(**validated_data)
        if password:
            customer.set_password(password)
        customer.save()
        # Create profile
        CustomerProfile.objects.create(customer=customer)
        return customer

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = Customer
        fields = ['username', 'email', 'password', 'password_confirm', 
                  'first_name', 'last_name', 'phone', 'address']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Mật khẩu không khớp")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        customer = Customer(**validated_data)
        customer.set_password(password)
        customer.save()
        CustomerProfile.objects.create(customer=customer)
        return customer


class CustomerLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
