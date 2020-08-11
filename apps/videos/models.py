from django.db import models


class FileUpload(models.Model):
    user_key = models.CharField(max_length=100, null=True, blank=True)
    file_up = models.FileField(upload_to='documents/%Y/%m/%d')