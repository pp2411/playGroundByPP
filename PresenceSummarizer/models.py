from django.db import models

# Create your models here.
# class Result(models.Model):
#     name = models.CharField(max_length=20)
#     timeStamps = models.ManyToManyField("TimeStamps", blank=False)
#     duration = models.TextField()

#     def __str__(self) -> str:
#         return f'{name} was present for total duration of {duration}'

# class TimeStamps(models.Model):
#     case = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='timeStamp')
#     time = models.TimeField()

class ScanRequest(models.Model):
    name = models.CharField(max_length = 40)
    img = models.ImageField(upload_to = 'images/')
    vid = models.FileField(upload_to = 'videos/')

    def __str__(self):
        return f"{self.name} {str(self.img)}"