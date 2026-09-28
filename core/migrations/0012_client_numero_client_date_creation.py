from datetime import datetime, time

import django.utils.timezone
from django.db import migrations, models


def numeroter_clients_existants(apps, schema_editor):
    """Attribue un numéro par hôtel (dans l'ordre de création) aux clients existants."""
    Client = apps.get_model('core', 'Client')
    compteurs = {}
    for client in Client.objects.order_by('hotel_id', 'id'):
        compteurs[client.hotel_id] = compteurs.get(client.hotel_id, 0) + 1
        client.numero_client = compteurs[client.hotel_id]
        # Faute de date de création connue, on reprend la date d'entrée
        if client.date_entree:
            client.date_creation = django.utils.timezone.make_aware(
                datetime.combine(client.date_entree, time.min)
            )
        client.save(update_fields=['numero_client', 'date_creation'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_alter_expense_categorie'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='numero_client',
            field=models.PositiveIntegerField(blank=True, editable=False, null=True, verbose_name='N° client'),
        ),
        migrations.AddField(
            model_name='client',
            name='date_creation',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='Client depuis'),
        ),
        migrations.RunPython(numeroter_clients_existants, migrations.RunPython.noop),
        migrations.AlterModelOptions(
            name='client',
            options={'ordering': ['numero_client'], 'verbose_name': 'Client', 'verbose_name_plural': 'Clients'},
        ),
        migrations.AddConstraint(
            model_name='client',
            constraint=models.UniqueConstraint(fields=('hotel', 'numero_client'), name='unique_numero_client_par_hotel'),
        ),
    ]
