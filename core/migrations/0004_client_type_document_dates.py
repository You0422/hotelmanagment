# Generated manually to align Client with model (type_document, numero_document, date_entree, date_sortie)

from django.db import migrations, models


def default_date():
    from django.utils import timezone
    return timezone.now().date()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_hotelsetting_report_remove_service_service_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='type_document',
            field=models.CharField(choices=[('CNI', 'Carte Nationale'), ('Passeport', 'Passeport')], default='CNI', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='client',
            name='numero_document',
            field=models.CharField(default='N/A', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='client',
            name='date_entree',
            field=models.DateField(default=default_date),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='client',
            name='date_sortie',
            field=models.DateField(default=default_date),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='client',
            name='document_identification',
        ),
        migrations.RemoveField(
            model_name='client',
            name='periode_occupation',
        ),
    ]
