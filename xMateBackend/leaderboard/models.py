from django.db import models
from django.conf import settings

# Create your models here.
class Leaderboard(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rank = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=0)

    def Update_rank(self):
        self.points = self.user.total_points
        self.save()
