import csv

from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    '''
    Команда для создания объектов моделей из файлов csv.
    Будет выглядить так:
    python manage.py load_data_from_csv --file_name comments.csv
    --model_name Comment --app_name reviews.
    '''
    
    help = 'Создает объект модели в базу данных из файла .csv'

    def add_arguments(self, parser):
        parser.add_argument('--file_name', type=str, help="имя файла")
        parser.add_argument('--model_name', type=str, help="имя модели")
        parser.add_argument('--app_name', type=str, help="приложение модели")

    def handle(self, *args, **options):
        file_path = 'static/data/' + options['file_name']
        # Получаем модель
        model = apps.get_model(options['app_name'], options['model_name'])
        # C помощью функции open читаем файл (указываем путь) и режим (r - открыт для чтения)
        # возвращает объект чтения который будет перебирать строки в данном файле - csv_file 
        # encoding - чтобы было без каракуль
        with open(file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            # метод next - переход на следующую строку header = ['id', 'name', 'slug'])
            header = next(reader)
            # Если в csv и models разные названия полей, то можно в ручную сделать так.
            # А можно просто исправить названия в файлах csv.
            # if options['model_name'] == 'Title':
            #     for row in reader:
            #         object_dict = {
            #             'id': row[0],
            #             'name': row[1],
            #             'year': row[2],
            #             'category_id': row[3]
            #         }
            #         model.objects.create(**object_dict)
            # else:
            for row in reader:
                # Функция  zip объединяет 2 массива (заголовк и row(строчка))
                # ['id', 'name', 'slug']) и ['3', 'Р¤РёР»СЊРј', 'mov']
                object_dict = {key: value for key, value in zip(header, row)}
                # Получим словарь {'id': '3', 'name': 'Р¤РёР»СЊРј', 'slug': 'mov'},
                # Передадим его в модель  
                model.objects.create(**object_dict)
