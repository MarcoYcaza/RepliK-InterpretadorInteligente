from django.db import models

# Create your models here.
class Pyme(models.Model):
    pyme_name = models.CharField(max_length=250)
    pyme_document = models.FileField(default='default.pdf',blank=True, upload_to='')
    register_created_at = models.DateTimeField(auto_now_add=True, null=True)
    date =  models.CharField(max_length=250,blank=True,null=True)
    mnt_units = models.CharField(max_length=250,blank=True,null=True)
    cashResources = models.CharField(max_length=20, blank=True,null=True)
    totalAssets = models.FloatField(default=0, blank=True,null=True)
    totalLiabilities = models.FloatField(default=0, blank=True,null=True)
    totalEquity = models.FloatField(default=0, blank=True,null=True)
    sales = models.FloatField(default=0, blank=True,null=True)
    costSales =models.FloatField(default=0, blank=True,null=True)
    grossProfit =models.FloatField(default=0, blank=True,null=True)
    operatingProfit=models.FloatField(default=0, blank=True,null=True)
    profitBeforeTax =models.FloatField(default=0, blank=True,null=True)
    netProfit =models.FloatField(default=0, blank=True,null=True)
    accuracy = models.FloatField(default=0, blank=True,null=True)
    more_info = models.TextField(default="here additional info", blank=True,null=True)

    def __str__(self):
        return self.pyme_name + " " + str(self.register_created_at)
