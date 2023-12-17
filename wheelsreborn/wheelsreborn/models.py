# models.py
from django.db import models
from django.contrib.auth.models import User

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car_owner_name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    variant = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)  # You may adjust the max_length based on your needs
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip = models.CharField(max_length=10)
    inspection_date = models.DateField()
    message = models.TextField()

    def __str__(self):
        return f"{self.car_owner_name}'s Booking"

class Profile(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    bio = models.TextField(max_length=255,null=True, blank=True, default="Tell us something about you")
    phone = models.CharField(max_length=10,null=True, blank=True, default="Your Mobile")
    address1 = models.CharField(max_length=255,null=True, blank=True, default= "Address Line 1")
    address2 = models.CharField(max_length=255,null=True, blank=True, default= "Address Line 2")
    city = models.CharField(max_length=150,null=True, blank=True, default="Your City")
    state = models.CharField(max_length=150,null=True, blank=True, default="Your State")
    zip = models.CharField(max_length=6,null=True, blank=True, default="123456")
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    '''def save(self, *args, **kwargs):
        # Check if there's an existing profile image
        if self.pk:
            existing_instance = Profile.objects.get(pk=self.pk)
            if existing_instance.profile_image:
                # Delete the existing profile image
                existing_instance.profile_image.delete(save=False)

        super(Profile, self).save(*args, **kwargs)'''

    def __str__(self):
        return str(self.user)
    
class Images(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    car_image1 = models.ImageField(upload_to='car_images/', blank=True, null=True)
    car_image2 = models.ImageField(upload_to='car_images/', blank=True, null=True)
    car_image3 = models.ImageField(upload_to='car_images/', blank=True, null=True)
    car_image4 = models.ImageField(upload_to='car_images/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Check if there's an existing instance
        if self.pk:
            existing_instance = Images.objects.get(pk=self.pk)
            # Delete the existing car images
            if existing_instance.car_image1:
                existing_instance.car_image1.delete(save=False)
            if existing_instance.car_image2:
                existing_instance.car_image2.delete(save=False)
            if existing_instance.car_image3:
                existing_instance.car_image3.delete(save=False)
            if existing_instance.car_image4:
                existing_instance.car_image4.delete(save=False)

        super(Images, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.user)