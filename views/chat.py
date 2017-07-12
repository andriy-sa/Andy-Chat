from flask import Blueprint, request, jsonify, g
from libraries.authentification import login_required
from models.room import Room
from models.room_member import RoomMember
from models.message import Message
from models.user import User
from app import db
chat_view = Blueprint('chat_view', __name__)


@chat_view.route('/chat/message', methods=['POST'])
@login_required()
def send_message():
    data = request.get_json()

    if (not data['room_id'] and not data['to_id']) or data['to_id'] == g.user['id']:
        return jsonify({'message':"Bad Request"}), 400

    if data['room_id']:
        room_id = data['room_id']
        room = Room.find(room_id)
        if not room:
            return jsonify({'message': "Unknown Room"}), 400
    else:
        user = User.find(data['to_id'])
        if not user:
            return jsonify({'message': "Unknown User"}), 400
        room = Room.where('is_group',0)\
            .select('rooms.id')\
            .join('room_members as rm','rm.room_id','=','rooms.id')\
            .where('rm.user_id',g.user['id']) \
            .where_has(
                'members',
                lambda q: q.where('user_id', data['to_id']).where_raw('room_id = rooms.id')
            )\
            .distinct()\
            .first()

        if not room:
            room = Room()
            room.save()

            member1 = RoomMember()
            member1.room_id = room.id
            member1.user_id = data['to_id']
            member1.save()

            member2 = RoomMember()
            member2.room_id = room.id
            member2.user_id = g.user['id']
            member2.save()

        room_id = room.id

    message = Message()
    message.sender_id = g.user['id']
    message.room_id = room_id
    message.message = data['message'] if data['message'] else '...'
    message.save()

    RoomMember.where('room_id', room_id).where('user_id',g.user['id']).update(last_read_message=message.id)

    return jsonify({'status':True}), 200


@chat_view.route('/chat/rooms', methods=['GET'])
@login_required()
def rooms():
    rooms = Room.select('rooms.*')\
        .add_select(
            db.raw('(select m.created_at from messages as m where rooms.id = m.room_id order by m.created_at desc limit 1) as last_message_date')
        ) \
        .add_select(
            db.raw('IF(rooms.is_group,false,(select CONCAT(u.first_name," ",u.last_name) from room_members as mem join users as u on u.id = mem.user_id where mem.room_id = rooms.id and u.id != %s limit 1)) as username' % g.user['id'])
        )\
        .add_select(
            db.raw('(select count(m.id) from room_members as mem join messages as m on m.room_id = mem.room_id where mem.user_id = %s and mem.room_id = rooms.id and m.id > IF(mem.last_read_message,mem.last_read_message,0)) as unread_messages' % g.user['id'])
        )\
        .join('room_members as rm', 'rm.room_id', '=', 'rooms.id') \
        .where('rm.user_id', g.user['id']) \
        .group_by('rooms.id') \
        .order_by('last_message_date','desc')\
        .get()

    return jsonify(rooms.serialize()), 200
