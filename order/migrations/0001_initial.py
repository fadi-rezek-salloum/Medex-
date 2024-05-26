# Generated by Django 5.0.6 on 2024-05-26 12:03

import common.utils.file_upload_paths
import common.validators.image_video_extension_validator
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1, verbose_name='Quantity')),
                ('total_price', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=15, null=True)),
                ('shipping_status', models.CharField(choices=[('OR', 'Ordered'), ('P', 'Shipping is being prepared'), ('OTW', 'On the way'), ('DE', 'Delivered')], default='OR', max_length=15, verbose_name='Shipping Status')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Buyer')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Ordered Date')),
                ('is_paid', models.BooleanField(default=False, verbose_name='Is Paid')),
                ('payment_method', models.CharField(choices=[('CASH', 'Cash')], max_length=55, verbose_name='Payment Method')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='Buyer')),
                ('products', models.ManyToManyField(blank=True, to='order.orderitem', verbose_name='Products')),
            ],
        ),
        migrations.CreateModel(
            name='ReturnRequest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('tracking_number', models.CharField(max_length=50, unique=True, verbose_name='Tracking Number')),
                ('status', models.CharField(choices=[('NOT', 'Not Requested'), ('AP', 'Applied'), ('DEC', 'Declined by Supplier'), ('APR', 'Approved by Supplier'), ('OTW', 'On the way'), ('CMP', 'Return Completed')], default='NOT', max_length=15, verbose_name='Return Status')),
                ('reason', models.CharField(choices=[('POO', 'Poor quality'), ('WRO', 'Wrong materials'), ('ADD', 'Shipped to a wrong address')], max_length=15, verbose_name='Return Reason')),
                ('description', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('decline_reason', models.TextField(blank=True, null=True)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='order.orderitem')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Buyer')),
            ],
        ),
        migrations.CreateModel(
            name='ReturnRequestFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('evidence_file', models.FileField(blank=True, null=True, upload_to=common.utils.file_upload_paths.return_request_files_path, validators=[common.validators.image_video_extension_validator.image_video_extension_validator])),
                ('return_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.returnrequest')),
            ],
        ),
    ]
