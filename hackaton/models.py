from django.db import models

# Create your models here.
class Pyme(models.Model):
    pyme_name = models.CharField(max_length=250)
    pyme_document = models.FileField(default='default.png',blank=True, upload_to='PymeFolders')
    
    def __str__(self):
        return self.pyme_name

