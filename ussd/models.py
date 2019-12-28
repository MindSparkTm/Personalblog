from django.db import models
from accounts.models import UserProfile
from django.utils.translation import ugettext_lazy as _
from .handler import get_username
# Create your models here.

class Country(models.Model):
    order_by = ['name']
    name = models.CharField(max_length=60, unique=True)
    international_dialing_code = models.IntegerField(unique=True)
    iso_3_abbreviation = models.CharField(max_length=3, unique=True)
    iso_2_abbreviation = models.CharField(max_length=2, unique=True)
    # currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    # default_timezone = models.CharField(max_length=32, choices=zip(pytz.common_timezones, pytz.common_timezones), blank=True)
    # default_language = models.ForeignKey(Language, on_delete=models.PROTECT)
    zone_1_label = models.CharField(max_length=32, blank=True)
    zone_1_mandatory = models.BooleanField(default=False)
    zone_2_label = models.CharField(max_length=32, blank=True)
    zone_2_mandatory = models.BooleanField(default=False)
    zone_3_label = models.CharField(max_length=32, blank=True)
    zone_3_mandatory = models.BooleanField(default=False)
    zone_4_label = models.CharField(max_length=32, blank=True)
    zone_4_mandatory = models.BooleanField(default=False)
    zone_5_label = models.CharField(max_length=32, blank=True)
    zone_5_mandatory = models.BooleanField(default=False)
    creator = models.ForeignKey(UserProfile, on_delete=models.PROTECT, related_name='+')
    date_last_modified = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return u'{}'.format(self.name)

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'

class Currency(models.Model):
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10)
    country = models.OneToOneField(Country,on_delete=models.CASCADE,related_name='currency')

    def __str__(self):
        return u'{}{}'.format(self.name,self.symbol)

    class Meta:
        verbose_name_plural = ('currencies')
        verbose_name = ('currency')

class USSDCarrier(models.Model):
    code = models.CharField(max_length=5,unique=True)
    name = models.CharField(max_length=60)
    country_default = models.BooleanField(default=False)
    country = models.ForeignKey(Country,on_delete=models.PROTECT,null=True,blank=True)
    date_last_modified = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(UserProfile, on_delete=models.PROTECT, related_name='+')


    def __str__(self):
        return self.name


    def save(self, *args, **kwargs):
        if not hasattr(self, 'creator'):
            self.creator = UserProfile.objects.get_or_create(user__username='system')[0]
        super(USSDCarrier, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("USSD Carrier")
        verbose_name_plural = _("USSD Carriers")

class USSDSession(models.Model):
    """
    Holds all associated data about the current USSD Session.
    Provides the methods that can be uses in the validation code and templates
    for the USSDPageMove(s)
    requires a user in the database called settings.USSD_USER_NAME
    """
    session_id = models.CharField(max_length=64, unique=True, blank=False, null=False)
    user_response = models.CharField(max_length=64, blank=False, null=True)
    phone_number = models.CharField(max_length=64, blank=False, null=False)
    service_code = models.CharField(max_length=64, blank=False, null=True)
    # account = models.ForeignKey(AccountBase, on_delete=models.PROTECT, related_name='ussd_sessions', null=True)
    # payment_plan = models.ForeignKey("readypay.PaymentPlan", on_delete=models.PROTECT, related_name='ussd_sessions', null=True)
    # order = models.ForeignKey("sales.Order", on_delete=models.PROTECT, related_name='ussd_sessions', null=True)
    # loan = models.ForeignKey("loan.Loan", on_delete=models.PROTECT, related_name='ussd_sessions', null=True)
    last_page = models.ForeignKey('USSDPage', null=True, on_delete=models.PROTECT)
    date_last_modified = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)
    carrier = models.ForeignKey(USSDCarrier,on_delete=models.PROTECT,null=True)
    page_task_id = models.CharField(null=True,blank=True,max_length=100)

    def __unicode__(self):
        return u'USSD Session {}'.format(self.id)

    class Meta:
        verbose_name = _("USSD Session")
        verbose_name_plural = _("USSD Sessions")

    @property
    def last_user_input(self):
        if self.user_response:
            return self.user_response.split('*').pop()
        return None


    @property
    def page_task_get_username(self):
        return get_username.delay(self.phone_number)

class USSDPage(models.Model):
    title = models.CharField(max_length=64,blank=False, null=False)
    creator = models.ForeignKey(UserProfile, on_delete=models.PROTECT, related_name='+')
    date_last_modified = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)
    carrier = models.ForeignKey(USSDCarrier,on_delete=models.PROTECT,default=1)

    def __str__(self):
        return u'USSD Page {}: {}'.format(self.id, self.title)

    def save(self, *args, **kwargs):
        super(USSDPage, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("USSD Page")
        verbose_name_plural = _("USSD Pages")
        unique_together = ('title', 'carrier',)



class USSDPageMove(models.Model):
    page = models.ForeignKey(USSDPage, on_delete=models.PROTECT, null=True, blank=True, related_name='page_moves')
    validation_code = models.CharField(max_length=255, blank=True, null=True, help_text="Validation functions on the session, must return success")
    page_tasks = models.CharField(max_length=255, blank=True, null=True, help_text="Update functions on the session, must return success")
    required_user_input = models.CharField(max_length=64, blank=True, null=True)
    next_page = models.ForeignKey(USSDPage, null=False, blank=False, on_delete=models.PROTECT, related_name="previous_page_move")
    error_page = models.ForeignKey(USSDPage, null=True, blank=True, on_delete=models.PROTECT, related_name="previous_error_page_move")
    creator = models.ForeignKey(UserProfile, on_delete=models.PROTECT, related_name='+')
    date_last_modified = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'USSD Page Move {}: {}'.format(self.id, self.next_page.title)

    def save(self, *args, **kwargs):
        super(USSDPageMove, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("USSD Page Move")
        verbose_name_plural = _("USSD Page Moves")
        unique_together = ("page", "required_user_input")


class USSDPageContent(models.Model):
    page = models.ForeignKey(USSDPage, on_delete=models.PROTECT)
    # language = models.ForeignKey(Language, on_delete=models.PROTECT)
    content = models.TextField()
    creator = models.ForeignKey(UserProfile,on_delete=models.PROTECT, related_name='+')
    date_last_modified = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return u'USSD Page Content {}: {}'.format(self.id, self.page.title)


    class Meta:
        verbose_name = _("USSD Page Content")
        verbose_name_plural = _("USSD Page Contents")
        unique_together = ("page",)


