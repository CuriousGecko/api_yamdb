import csv

from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Команда для создания объектов моделей из файлов csv.

    # Будет выглядеть так:
    # python manage.py load_data_from_csv --file_name comments.csv --model_name Comment --app_name reviews
    """

    help = 'Создает объект модели в базу данных из файла .csv'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file_name',
            type=str,
            help='имя файла',
        )
        parser.add_argument(
            '--model_name',
            type=str,
            help='имя модели',
        )
        parser.add_argument(
            '--app_name',
            type=str,
            help='приложение модели',
        )

    def handle(self, *args, **options):
        file_path = 'static/data/' + options['file_name']
        model = apps.get_model(
            options['app_name'],
            options['model_name'],
        )
        with open(file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(
                csv_file,
                delimiter=','
            )
            header = next(reader)
            objects_of_model = []
            for row in reader:
                object_dict = {
                    key: value for key, value in zip(header, row)
                }
                objects_of_model.append(model(**object_dict))
            model.objects.bulk_create(objects_of_model)
            
            # model.objects.bulk_create([
            #     model(**{key: value for key, value in zip(header, row)})
            #     for row in reader
            # ])
