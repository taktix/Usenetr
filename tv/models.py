from django.db import models


VIDEO_QUALITIES = (
    (0,'Unknown'),
    (1,'720p'),
    (2,'1080p'),
)



class TV(models.Model):
    quality = models.IntegerField(choices=VIDEO_QUALITIES)