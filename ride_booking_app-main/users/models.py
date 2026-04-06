from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('driver', 'Driver'),
        ('admin', 'Admin'),
    )
    
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = PhoneNumberField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    fcm_token = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']
    
    objects = UserManager()
    
    def __str__(self):
        return f"{self.email} ({self.role})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_student(self):
        return self.role == 'student'
    
    @property
    def is_driver(self):
        return self.role == 'driver'
    
    @property
    def is_admin_user(self):
        return self.role == 'admin'
    
    def get_average_rating(self):
        if self.is_driver:
            ratings = self.received_ratings.all()
            if ratings.exists():
                return ratings.aggregate(models.Avg('rating'))['rating__avg']
        return 0
    

class DriverProfile(models.Model):
    """Extended profile for drivers with additional fields"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile')
    
    # License information
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry = models.DateField()
    license_photo = models.ImageField(upload_to='licenses/')
    
    # Driver status
    is_available = models.BooleanField(default=False)
    current_latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)
    
    # Stats
    total_trips = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Driver: {self.user.get_full_name()}"

class StudentProfile(models.Model):
    """Extended profile for students"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    
    # Student specific fields
    student_id = models.CharField(max_length=50, blank=True)
    institution = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=100, blank=True)
    
    # Saved locations
    home_address = models.TextField(blank=True)
    home_latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    home_longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    # Preferences
    preferred_payment_method = models.CharField(max_length=20, default='wallet')
    
    # Stats
    total_trips = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Student: {self.user.get_full_name()}"