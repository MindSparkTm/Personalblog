from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class ClientRequestDetail(models.Model):
    '''
    Table contains entries for saving Meta Data for ClientRequest
    '''
    ip = models.GenericIPAddressField()
    content_type = models.TextField()
    query_string = models.CharField(max_length=100)
    browser_detail = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return u'{}{}'.format(self.ip,self.query_string)

    class Meta:
        verbose_name = _('ClientRequestDetail')
        verbose_name_plural = _('ClientRequestDetails')
        ordering = ['-date_added']

