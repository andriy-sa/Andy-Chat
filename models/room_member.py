from orator import Model
from orator.orm import belongs_to
from models import user
class RoomMember(Model):

    @belongs_to('user_id')
    def user(self):
        return user.User
