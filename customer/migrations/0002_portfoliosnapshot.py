from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PortfolioSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('snapshot_date', models.DateTimeField(auto_now_add=True, db_column='SnapshotDate')),
                ('total_value', models.DecimalField(db_column='TotalValue', decimal_places=2, help_text='Cash + Stock Holdings Value', max_digits=15)),
                ('cash_balance', models.DecimalField(db_column='CashBalance', decimal_places=2, max_digits=15)),
                ('holdings_value', models.DecimalField(db_column='HoldingsValue', decimal_places=2, max_digits=15)),
                ('account', models.ForeignKey(db_column='AccountID', on_delete=django.db.models.deletion.CASCADE, related_name='snapshots', to='customer.brokerageaccount')),
            ],
            options={
                'db_table': 'PortfolioSnapshot',
                'ordering': ['-snapshot_date'],
            },
        ),
        migrations.AddIndex(
            model_name='portfoliosnapshot',
            index=models.Index(fields=['account', '-snapshot_date'], name='customer_po_account_idx'),
        ),
    ]
