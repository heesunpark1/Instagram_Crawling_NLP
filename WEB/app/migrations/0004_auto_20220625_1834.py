# Generated by Django 2.2 on 2022-06-25 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20171126_1545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='musictagplaylist',
            name='ext_tags',
            field=models.CharField(blank=True, max_length=170, null=True),
        ),
    ]
