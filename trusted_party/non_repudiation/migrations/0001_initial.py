# Generated by Django 4.2.7 on 2024-04-01 11:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('cert_digest', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('cert', models.TextField()),
                ('certificate_type', models.CharField(choices=[('root', 'root'), ('intermediate', 'intermediate'), ('client', 'client')], max_length=20)),
                ('is_revoked', models.BooleanField(default=False)),
                ('received_on', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_id', models.CharField()),
                ('document_type', models.CharField(choices=[('graph', 'graph'), ('domain_specific', 'domain_specific'), ('backbone', 'backbone')], max_length=20)),
                ('document_text', models.TextField()),
                ('created_on', models.IntegerField()),
                ('signature', models.TextField()),
                ('certificate', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='non_repudiation.certificate')),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('org_name', models.CharField(max_length=40, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash', models.CharField(max_length=128)),
                ('hash_function', models.CharField(choices=[('SHA256', 'SHA256'), ('SHA512', 'SHA512'), ('SHA3-256', 'SHA3-256'), ('SHA3-512', 'SHA3-512')], max_length=15)),
                ('created_on', models.IntegerField()),
                ('signature', models.BinaryField()),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='non_repudiation.document')),
            ],
        ),
        migrations.AddField(
            model_name='document',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='non_repudiation.organization'),
        ),
        migrations.AddField(
            model_name='certificate',
            name='organization',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.RESTRICT, to='non_repudiation.organization'),
        ),
    ]
