from django.core.management.base import BaseCommand
from app.models import FGOSCompetency
import json

class Command(BaseCommand):
    help = 'Импорт компетенций ФГОС из JSON файла'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help='Путь к JSON файлу')

    def handle(self, *args, **options):
        file_path = options['file']
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                competencies = json.load(f)
            
            count = 0
            for comp in competencies:
                FGOSCompetency.objects.update_or_create(
                    code=comp['code'],
                    defaults={
                        'name': comp['name'],
                        'specialty_code': comp['specialty_code'],
                        'type': comp['type']
                    }
                )
                count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Успешно импортировано {count} компетенций ФГОС')
            )
            
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'Файл не найден: {file_path}')
            )
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR('Ошибка чтения JSON файла')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка импорта: {str(e)}')
            )