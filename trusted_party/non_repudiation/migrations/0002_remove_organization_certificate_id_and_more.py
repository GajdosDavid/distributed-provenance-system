# Generated by Django 4.2.7 on 2024-03-27 23:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('non_repudiation', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='certificate_id',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='id',
        ),
        migrations.AlterField(
            model_name='certificate',
            name='superior_cert',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.RESTRICT, to='non_repudiation.certificate'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='org_name',
            field=models.CharField(max_length=40, primary_key=True, serialize=False),
        ),
    ]
