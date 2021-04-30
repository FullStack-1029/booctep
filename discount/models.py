from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# from home.models import *

class discount(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    promo_code = models.TextField(null=True, blank=True)
    price_off_percentage = models.IntegerField(default=0)
    valid_days = models.IntegerField(null=True, blank=True)
    valid_categories = models.TextField(default='0')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)





