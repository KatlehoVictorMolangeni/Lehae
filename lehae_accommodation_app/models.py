from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    phone = models.CharField(max_length=15)
    id_number = models.CharField(max_length=20)
    id_type = models.CharField(max_length=10)

    def __str__(self):
        return self.user.email
    


class Merchant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Personal
    phone = models.CharField(max_length=15)
    id_number = models.CharField(max_length=20)

    # Business
    business_name = models.CharField(max_length=255)
    merchant_type = models.CharField(max_length=50)

    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    address = models.TextField()

    # Verification
    verification_document = models.FileField(upload_to='merchant_docs/')

    # Status (important for your system)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.business_name
    


# =========================
# LOOKUP TABLES
# =========================

class Accreditation(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Campus(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Amenity(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# =========================
# PROPERTY MODEL
# =========================

class Property(models.Model):
    ACCOMMODATION_TYPES = [
        ('Single Room', 'Single Room'),
        ('Sharing', 'Sharing'),
        ('House', 'House'),
        ('Hostel', 'Hostel'),
        ('Rooms', 'Rooms'),
    ]

    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='properties')

    # Basic Information
    title = models.CharField(max_length=255)
    accommodation_type = models.CharField(max_length=50, choices=ACCOMMODATION_TYPES)
    description = models.TextField()

    # Location
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    address = models.TextField()

    # Capacity & Pricing
    number_of_rooms = models.PositiveIntegerField()
    beds_available = models.PositiveIntegerField()
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Media
    cover_image = models.ImageField(upload_to='property_covers/')

    # Documents
    proof_of_accreditation = models.FileField(
        upload_to='property_documents/accreditation/',
        null=True,
        blank=True
    )
    house_policy = models.FileField(
        upload_to='property_documents/policies/',
        null=True,
        blank=True
    )

    # Availability
    available_from = models.DateField()
    is_available = models.BooleanField(default=True)

    # Many-to-Many
    accreditation = models.ManyToManyField(Accreditation, blank=True)
    campuses = models.ManyToManyField(Campus, blank=True)
    amenities = models.ManyToManyField(Amenity, blank=True)

    # Approval & Status
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# =========================
# ADDITIONAL PROPERTY IMAGES
# =========================

class PropertyImage(models.Model):
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='gallery'
    )
    image = models.ImageField(upload_to='property_gallery/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.property.title}"

