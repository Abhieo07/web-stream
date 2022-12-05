from email.policy import default
from django.db import models

# Create your models here.

class AjaxField(models.Model):
    name = models.CharField(max_length=20,default="Name field")
    picture = models.ImageField(upload_to = 'profile_images', default='wink.jpg')
    
    def __str__(self):
        return self.name
