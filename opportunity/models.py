from account.models import Address
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager

User = get_user_model()


class Opportunity(models.Model):
    class PAYMENT_METHOD_CHOICES(models.TextChoices):
        direct = "DIR", _("Direct")
        divided = "DIV", _("Divided")

    class STATUS_CHOICES(models.TextChoices):
        op = "O", _("Open")
        cl = "CL", _("Closed")
        ca = "CA", _("Canceled")
        pp = "P", _("Pending Payment")
        f = "F", _("Finished")

    class OPPORTUNITY_VALUE_CHOICES(models.TextChoices):
        vs = "VS", _("Very Small")
        s = "S", _("Small")
        m = "M", _("Medium")
        b = "B", _("Big")
        e = "E", _("Extraordinary")

    title = models.CharField(_("Title"), max_length=255, db_index=True)

    payment_method = models.CharField(
        _("Payment Method"), max_length=3, choices=PAYMENT_METHOD_CHOICES.choices
    )
    status = models.CharField(
        _("Status"), max_length=2, choices=STATUS_CHOICES.choices, default=STATUS_CHOICES.op
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    tags = TaggableManager()

    delivery_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)

    delivery_date = models.DateTimeField()

    payment_days = models.CharField(max_length=255)

    opportunity_value = models.CharField(
        _("Opportunity Value"), max_length=3, choices=OPPORTUNITY_VALUE_CHOICES.choices
    )

    target_suppliers = models.ManyToManyField(
        User, verbose_name=_("Target Suppliers"), related_name="target_suppliers", blank=True
    )

    views = models.BigIntegerField(_("Views"), default=0)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Opportunities"
