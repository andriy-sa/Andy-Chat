from orator.seeds import Seeder
from models.user import User


class DatabaseSeeder(Seeder):

    def run(self):

        user = User()
        user.first_name = 'Andriy'
        user.last_name = 'Smolyar'
        user.email = 'andriy_smolyar_0@mail.ru'
        user.password = User.make_password('password')
        user.save()

        user = User()
        user.first_name = 'Test'
        user.last_name = 'User'
        user.email = 'test_user@mail.ru'
        user.password = User.make_password('password')
        user.save()

