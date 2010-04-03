from django.db import models

from raw.models import Post

VIDEO_QUALITIES = (
    (0,'Unknown'),
    (1,'720p'),
    (2,'1080p'),
)


class TV(Post):
    title = models.CharField(max_length=32)
    quality = models.IntegerField(choices=VIDEO_QUALITIES, null=True)