from orator import Model
from models import room_member
from orator.orm import has_many


class Room(Model):
    @has_many('room_id', 'id')
    def members(self):
        return room_member.RoomMember
