from django.core.management.base import BaseCommand
from customer.models import CustomUser, Stock
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Setup production environment with admin user and sample stocks'

    def handle(self, *args, **options):
        # Create admin user
        try:
            if not CustomUser.objects.filter(UserName='admin').exists():
                admin = CustomUser.objects.create_superuser(
                    UserName='admin',
                    email='admin@investr.com',
                    FullName='Admin User',
                    Role='ADMIN',
                    password='InvestR2024!'
                )
                self.stdout.write(self.style.SUCCESS('Admin user created (username: admin, password: InvestR2024!)'))
            else:
                self.stdout.write(self.style.WARNING('Admin user already exists'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating admin: {e}'))

        # Create stocks
        stocks_data = [
            {
                'ticker': 'AAPL',
                'name': 'Apple Inc.',
                'initial_price': 189.00,
                'current_price': 189.41,
                'opening_price': 189.00,
                'day_high': 190.50,
                'day_low': 188.00,
                'float_shares': 1000000
            },
            {
                'ticker': 'GOOGL',
                'name': 'Alphabet Inc.',
                'initial_price': 139.00,
                'current_price': 139.64,
                'opening_price': 139.00,
                'day_high': 140.50,
                'day_low': 138.50,
                'float_shares': 1000000
            },
            {
                'ticker': 'AMZN',
                'name': 'Amazon.com Inc.',
                'initial_price': 175.00,
                'current_price': 175.61,
                'opening_price': 175.00,
                'day_high': 176.01,
                'day_low': 174.45,
                'float_shares': 1000000
            },
            {
                'ticker': 'MSFT',
                'name': 'Microsoft Corporation',
                'initial_price': 378.00,
                'current_price': 378.91,
                'opening_price': 378.00,
                'day_high': 380.25,
                'day_low': 377.50,
                'float_shares': 1000000
            },
            {
                'ticker': 'TSLA',
                'name': 'Tesla Inc.',
                'initial_price': 242.00,
                'current_price': 242.84,
                'opening_price': 242.00,
                'day_high': 245.50,
                'day_low': 240.00,
                'float_shares': 1000000
            }
        ]

        created_count = 0
        for stock_data in stocks_data:
            try:
                if not Stock.objects.filter(ticker=stock_data['ticker']).exists():
                    Stock.objects.create(**stock_data)
                    created_count += 1
            except IntegrityError:
                pass

        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f'✓ Created {created_count} stocks'))
        else:
            self.stdout.write(self.style.WARNING(f'All stocks already exist ({Stock.objects.count()} total)'))

        self.stdout.write(self.style.SUCCESS('Production setup complete!'))