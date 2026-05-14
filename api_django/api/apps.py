from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        @receiver(post_migrate)
        def create_initial_data(sender, **kwargs):
            if sender.name == 'api':
                Order_cat = self.get_model('Order_cat')
                if not Order_cat.objects.exists():
                    Order_cat.objects.bulk_create([
                        Order_cat(id=1, name='В очереди'),
                        Order_cat(id=2, name='Обрабатывается'),
                        Order_cat(id=3, name='Отправлен на почту'),
                        Order_cat(id=4, name='Завершился с ошибкой'),
                    ])


class UserConfig(AppConfig):
    name = 'user'
    verbose_name = 'пользователи'