from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
  type = models.TextField()
  author = models.ForeignKey(User)
  date = models.DateTimeField()
  post = models.TextField()

  def __unicode__(self):
    return self.post
    