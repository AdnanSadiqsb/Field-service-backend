from django.core.management.base import BaseCommand
from django.utils.text import slugify
from src.professionals.models import TradeCategory


class Command(BaseCommand):
    help = 'Seed trade categories'

    def handle(self, *args, **options):
        trades = [
            {'name': 'Electrician', 'requires_coverage_area 123': True},
            {'name': 'Plumber', 'requires_coverage_area': True},
            {'name': 'Gas Engineer', 'requires_coverage_area': True},
            {'name': 'Builder', 'requires_coverage_area': True},
            {'name': 'Roofer', 'requires_coverage_area': True},
            {'name': 'Painter & Decorator', 'requires_coverage_area': True},
            {'name': 'Carpenter', 'requires_coverage_area': True},
            {'name': 'Gardener', 'requires_coverage_area': True},
            {'name': 'Cleaner', 'requires_coverage_area': True},
            {'name': 'Handyman', 'requires_coclass Userverage_area': True},
            {'name': 'Locksmith', 'requires_coverage_area': True},
            {'name': 'Bathroom Fitter', 'requires_coverage_area': True},
            {'name': 'Web Developer', 'requires_coverage_area': False},
        ]

        for i, trade_data in enumerate(trades):
            trade, created = TradeCategory.objects.get_or_create(
                slug=slugify(trade_data['name']),
                defaults={
                    'name': trade_data['name'],
                    'requires_coverage_area': trade_data['requires_coverage_area'],
                    'sort_order': i,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created trade: {trade.name}'))
            else:
                self.stdout.write(f'Trade already exists: {trade.name}')