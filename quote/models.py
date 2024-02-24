import uuid

from account.models import Address
from common.utils.file_upload_paths import quote_files_path
from common.utils.generate_invoice_id import generate_invoice_id
from common.validators.image_pdf_extension_validator import image_pdf_extension_validator
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class QuoteRequest(models.Model):
    class UNIT_CHOICES(models.TextChoices):
        BAG = "bag", "Bag / Bags"
        BARREL = "barrel", "Barrel / Barrels"
        BUSHEL = "bushel", "Bushel / Bushels"
        CUBIC = "cubic", "Cubic Meter / Cubic Meters"
        DOZEN = "dozen", "Dozen / Dozens"
        GALLON = "gallon", "Gallon / Gallons"
        GRAM = "gram", "Gram / Grams"
        KILOGRAM = "kilogram", "Kilogram / Kilograms"
        KILOMETER = "kilometer", "Kilometer / Kilometers"
        LONG = "long", "Long Ton / Long Tons"
        METER = "meter", "Meter / Meters"
        METRIC = "metric", "Metric Ton / Metric Tons"
        OUNCE = "ounce", "Ounce / Ounces"
        PAIR = "pair", "Pair / Pairs"
        PACK = "pack", "Pack / Packs"
        PIECE = "piece", "Piece / Pieces"
        POUND = "pound", "Pound / Pounds"
        SET = "set", "Set / Sets"
        SHORT = "short", "Short Ton / Short Tons"
        SQUARE = "square", "Square Meter / Square Meters"
        TON = "ton", "Ton / Tons"

    # id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_("Created By"), blank=True, null=True
    )

    supplier = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Target Supplier"),
        blank=True,
        null=True,
        related_name="quote_requests_as_supplier",
    )

    product = models.CharField(_("Product"), max_length=255)

    quantity = models.PositiveBigIntegerField(_("Quantity"))
    unit = models.CharField(_("Unit"), max_length=50, choices=UNIT_CHOICES.choices)

    requirements = models.TextField(_("Requirements"))

    created = models.DateTimeField(auto_now_add=True)

    due_date = models.DateTimeField()

    def __str__(self):
        return f"{self.user.full_name} -> {self.product}"


class QuoteAttachment(models.Model):
    quote = models.ForeignKey(
        QuoteRequest, on_delete=models.CASCADE, verbose_name=_("Related Quote")
    )

    attachment = models.FileField(
        _("Attachment"), validators=[image_pdf_extension_validator], upload_to=quote_files_path
    )

    def __str__(self):
        return str(self.quote.id)


class QuoteOffer(models.Model):
    class STATUS_CHOICES(models.TextChoices):
        PENDING = ("P", "Pending")
        APPROVED = ("A", "Approved")
        DENIED = ("D", "Denied")

    quote = models.ForeignKey(
        QuoteRequest, on_delete=models.CASCADE, verbose_name=_("Target Quote")
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_("Supplier"), blank=True, null=True
    )

    notes = models.TextField(null=True, blank=True)

    brand = models.CharField(max_length=255, verbose_name=_("Brand"))
    quantity = models.PositiveBigIntegerField(_("Available Amount"))

    product_price = models.DecimalField(
        _("Price (Per Product)"), max_digits=10, decimal_places=2
    )
    total_price = models.DecimalField(_("Price (Total)"), max_digits=10, decimal_places=2)

    tax = models.DecimalField(_("TAX"), max_digits=3, decimal_places=2, default=0)

    delivery_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, verbose_name=_("Delivery Address")
    )
    delivery_date = models.DateField()

    payment_type = models.CharField(_("Payment Type"), max_length=255)

    created = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=2, choices=STATUS_CHOICES.choices, default=STATUS_CHOICES.PENDING
    )

    invoice_id = models.CharField(max_length=255, null=True, blank=True, unique=True)

    def __str__(self):
        return f"{self.user.full_name} => {self.quote.user.full_name}"

    def save(self, *args, **kwargs):
        if not self.invoice_id:
            self.invoice_id = generate_invoice_id()
        return super().save(*args, **kwargs)
