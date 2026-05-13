from django.contrib import admin
from .models import Profile, Merchant, PropertyImage, Property, Accreditation, Campus, Amenity

admin.site.register(Profile)
admin.site.register(Merchant)
admin.site.register(Property)
admin.site.register(PropertyImage) 
admin.site.register(Accreditation)
admin.site.register(Campus)
admin.site.register(Amenity)
admin.site.site_header = "Lehae Accommodation Admin"
admin.site.site_title = "Lehae Accommodation Admin Portal"
admin.site.index_title = "Welcome to Lehae Accommodation Admin Portal"
