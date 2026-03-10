from rest_framework import serializers
from .models import Customer, CustomerProfile, PersonalInfo, JobInfo, AddressInfo


class PersonalInfoSerializer(serializers.ModelSerializer):
    """Serializer for PersonalInfo model"""
    class Meta:
        model = PersonalInfo
        fields = ['fullname', 'nickname', 'gender', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class JobInfoSerializer(serializers.ModelSerializer):
    """Serializer for JobInfo model"""
    class Meta:
        model = JobInfo
        fields = ['job_title', 'company', 'industry', 'years_of_experience', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class AddressInfoSerializer(serializers.ModelSerializer):
    """Serializer for AddressInfo model"""
    full_address = serializers.CharField(read_only=True)
    
    class Meta:
        model = AddressInfo
        fields = ['street_address', 'ward', 'district', 'city', 'country', 
                  'postal_code', 'is_default', 'full_address', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ['loyalty_points', 'total_orders', 'total_spent', 
                  'preferred_payment_method', 'preferred_shipping_address']


class CustomerSerializer(serializers.ModelSerializer):
    profile = CustomerProfileSerializer(read_only=True)
    personal_info = PersonalInfoSerializer(read_only=True)
    job_info = JobInfoSerializer(read_only=True)
    address_info = AddressInfoSerializer(read_only=True)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Customer
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name',
                  'phone', 'avatar', 'date_of_birth', 'is_active_customer',
                  'created_at', 'updated_at', 'profile', 'personal_info', 'job_info', 'address_info']
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
    
    # Nested fields
    fullname = serializers.CharField(required=False, allow_blank=True)
    job_title = serializers.CharField(required=False, allow_blank=True)
    street_address = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Customer
        fields = ['username', 'email', 'password', 'password_confirm', 
                  'first_name', 'last_name', 'phone', 
                  'fullname', 'job_title', 'street_address']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Mật khẩu không khớp")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Extract nested data
        fullname = validated_data.pop('fullname', '')
        job_title = validated_data.pop('job_title', '')
        street_address = validated_data.pop('street_address', '')
        
        # Create customer
        customer = Customer(**validated_data)
        customer.set_password(password)
        customer.save()
        
        # Create related models
        CustomerProfile.objects.create(customer=customer)
        
        if fullname:
            PersonalInfo.objects.create(customer=customer, fullname=fullname)
        
        if job_title:
            JobInfo.objects.create(customer=customer, job_title=job_title)
        
        if street_address:
            AddressInfo.objects.create(customer=customer, street_address=street_address)
        
        return customer


class CustomerLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class CustomerUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating customer profile"""
    # Nested update fields
    personal_info = PersonalInfoSerializer(required=False)
    job_info = JobInfoSerializer(required=False)
    address_info = AddressInfoSerializer(required=False)
    
    class Meta:
        model = Customer
        fields = ['phone', 'avatar', 'date_of_birth', 'first_name', 'last_name', 'email',
                  'personal_info', 'job_info', 'address_info']
        
    def update(self, instance, validated_data):
        # Extract nested data
        personal_info_data = validated_data.pop('personal_info', None)
        job_info_data = validated_data.pop('job_info', None)
        address_info_data = validated_data.pop('address_info', None)
        
        # Update customer basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update or create PersonalInfo
        if personal_info_data:
            PersonalInfo.objects.update_or_create(
                customer=instance,
                defaults=personal_info_data
            )
        
        # Update or create JobInfo
        if job_info_data:
            JobInfo.objects.update_or_create(
                customer=instance,
                defaults=job_info_data
            )
        
        # Update or create AddressInfo
        if address_info_data:
            AddressInfo.objects.update_or_create(
                customer=instance,
                defaults=address_info_data
            )
        
        return instance

