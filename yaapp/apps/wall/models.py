from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
  kind = models.TextField()
  author = models.ForeignKey(User)
  date = models.DateTimeField()
  data = models.TextField()

  def __unicode__(self):
    return self.data
    