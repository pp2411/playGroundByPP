from django.db import models

class ScanRequest(models.Model):
    name = models.CharField(max_length = 40)
    img = models.ImageField(upload_to = 'images/')
    vid = models.FileField(upload_to = 'videos/')

    def __str__(self):
        return f"{self.name} {str(self.img)}"