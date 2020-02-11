from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.db.models import Func, F


class CustomManager(models.Manager):
    def bulk_create(self, objs, **kwargs):
        a = super(models.Manager, self).bulk_create(objs, **kwargs)
        for i in objs:
            post_save.send(i.__class__, instance=i, created=True)
        return a


class Month(Func):
    function = 'EXTRACT'
    template = '%(function)s(MONTH from %(expressions)s)'
    output_field = models.IntegerField()


class File(models.Model):
    STARTED = 'ST'
    IN_PROGRESS = 'IP'
    COMPLETED = 'CD'
    FAILED = 'FD'
    status = [
        (STARTED, 'STARTED'),
        (IN_PROGRESS, 'IN PROGRESS'),
        (COMPLETED, 'COMPLETED'),
        (FAILED, 'FAILED')
    ]
    file = models.FileField(upload_to='invoice/%Y/%m/%d')
    status = models.CharField(max_length=20, choices=status, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    validation_results = models.TextField(blank=True, null=True)
    progress = models.IntegerField(default=0)

    class Meta:
        verbose_name = _('File')
        verbose_name_plural = _('Files')
        ordering = ['-id']

    def __str__(self):
        return str(self.id)


class Customer(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    file = models.ForeignKey(
        File,
        verbose_name=_("File"),
        null=True,
        on_delete=models.PROTECT,
        related_name="invoice_file",
    )
    customer = models.ForeignKey(
        Customer,
        verbose_name=_("Customer"),
        null=True,
        on_delete=models.PROTECT,
        related_name="invoice_customer",
    )
    number = models.IntegerField(unique=True, db_index=True)
    date = models.DateField(default=timezone.now())
    due_date = models.DateField(default=timezone.now())
    description = models.TextField(blank=True, null=True)
    quantity = models.IntegerField()
    unit_amount = models.IntegerField()
    total = models.IntegerField(null=True, blank=True)

    objects = CustomManager()

    class Meta:
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')
        ordering = ['-total']

    def __str__(self):
        return u'{}{}'.format(self.number, self.date)


def update_invoice_total(sender, instance, created, **kwargs):
    try:
        Invoice.objects.filter(number=instance.number).update(total=F('unit_amount') * F('quantity'))
    except Exception as ex:
        pass


post_save.connect(update_invoice_total, sender=Invoice)
