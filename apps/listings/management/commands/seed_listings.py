import random
from django.core.management.base import BaseCommand
from apps.users.models import User
from apps.listings.models import Listing
from apps.core.models import HousingType


CITIES = {
    'Köln': ['Innenstadt', 'Ehrenfeld', 'Nippes', 'Deutz', 'Altstadt'],
    'Berlin': ['Mitte', 'Kreuzberg', 'Charlottenburg', 'Wedding', 'Prenzlauer Berg'],
    'Düsseldorf': ['Altstadt', 'Oberkassel', 'Benrath', 'Gerresheim', 'Flingern'],
    'Hamburg': ['Altona', 'Eimsbüttel', 'St. Pauli', 'Wandsbek', 'Harburg'],
    'München': ['Schwabing', 'Sendling', 'Bogenhausen', 'Neuhausen', 'Giesing'],
}

STREETS = ['Hauptstraße', 'Bahnhofstraße', 'Gartenweg', 'Kirchstraße', 'Ringstraße',
           'Schulstraße', 'Lindenallee', 'Waldweg', 'Bergstraße', 'Marktplatz']

TITLE_TEMPLATES = {
    HousingType.APARTMENT: ['Уютная квартира', 'Светлая квартира в центре', 'Современная квартира',
                             'Квартира с балконом', 'Просторная квартира'],
    HousingType.HOUSE: ['Дом с садом', 'Семейный дом', 'Загородный дом', 'Дом с гаражом', 'Дом у леса'],
    HousingType.STUDIO: ['Компактная студия', 'Студия для студента', 'Минималистичная студия', 'Студия у метро'],
    HousingType.ROOM: ['Комната в квартире', 'Бюджетная комната', 'Комната рядом с университетом'],
}

DESCRIPTIONS = [
    'Отличное расположение, рядом остановка общественного транспорта.',
    'Недавно отремонтировано, вся техника новая.',
    'Тихий район, отлично подходит для семьи.',
    'Рядом магазины, школа и детская площадка.',
    'Просторно, много естественного света.',
    'Идеально для студентов, близко к университету.',
]


class Command(BaseCommand):
    help = 'Создаёт 100 тестовых объявлений с разными параметрами'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=100, help='Сколько объявлений создать')

    def handle(self, *args, **options):
        count = options['count']

        owner = User.objects.first()
        if not owner:
            self.stdout.write(self.style.ERROR('Нет ни одного пользователя в базе — сначала создай суперюзера.'))
            return

        housing_types = list(HousingType.values)
        created = 0

        for i in range(count):
            city = random.choice(list(CITIES.keys()))
            district = random.choice(CITIES[city])
            housing_type = random.choice(housing_types)
            title = random.choice(TITLE_TEMPLATES[housing_type])

            Listing.objects.create(
                owner=owner,
                title=f'{title} #{i + 1}',
                description=random.choice(DESCRIPTIONS),
                country='Germany',
                city=city,
                district=district,
                street=random.choice(STREETS),
                house_number=str(random.randint(1, 200)),
                price=random.randint(280, 3500),
                rooms=random.randint(1, 6),
                housing_type=housing_type,
                is_active=random.random() > 0.1,  # ~90% активных
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f'Создано объявлений: {created}'))