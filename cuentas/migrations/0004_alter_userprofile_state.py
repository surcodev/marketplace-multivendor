# Generated by Django 5.1.2 on 2024-11-02 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuentas', '0003_alter_userprofile_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='state',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
