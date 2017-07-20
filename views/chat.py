from flask import Blueprint, request, jsonify, g
from libraries.authentification import login_required
from models.room import Room
from models.room_member import RoomMember
from models.message import Message
from models.user import User
from app import db, socketio
from underscore import _
from libraries.authentification import get_jwt_user
from flask_socketio import join_room, rooms as socket_rooms

chat_view = Blueprint('chat_view', __name__)
connected_users = []

@chat_view.route('/chat/message', methods=['POST'])
@login_required()
def send_message():
    data = request.get_json()

    if (not data['room_id'] and not data['to_id']) or data['to_id'] == g.user['id']:
        return jsonify({'message': "Bad Request"}), 400

    if data['room_id']:
        room_id = data['room_id']
        room = Room.find(room_id)
        room_member = RoomMember.where('room_id', room_id).where('user_id', g.user['id']).first()
        if not room or not room_member:
            return jsonify({'message': "Unknown Room"}), 400
    else:
        user = User.find(data['to_id'])
        if not user:
            return jsonify({'message': "Unknown User"}), 400
        room = Room.where('is_group', 0) \
            .select('rooms.id') \
            .join('room_members as rm', 'rm.room_id', '=', 'rooms.id') \
            .where('rm.user_id', g.user['id']) \
            .where_has(
            'members',
            lambda q: q.where('user_id', data['to_id']).where_raw('room_id = rooms.id')
        ) \
            .distinct() \
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

            #connect exist socket to room
            clients = _.where(connected_users,{'id':data['to_id']})
            my_clients = _.where(connected_users,{'id':g.user['id']})

            clients = _.compact(_.union(clients, my_clients))
            for item in clients:
                join_room('room-%s' % room.id, sid=item['sid'], namespace='/')




        room_id = room.id

    message = Message()
    message.sender_id = g.user['id']
    message.room_id = room_id
    message.message = data['message'] if data['message'] else '...'
    message.save()

    RoomMember.where('room_id', room_id).where('user_id', g.user['id']).update(last_read_message=message.id)

    message_response = message.serialize()
    message_response['first_name'] = g.user['first_name']
    message_response['last_name'] = g.user['last_name']
    message_response['avatar'] = g.user['avatar']

    return jsonify(message_response), 200


@chat_view.route('/chat/rooms', methods=['GET'])
@login_required()
def rooms():
    rooms = Room.select('rooms.*') \
        .add_select(
        db.raw(
            '(select m.created_at from messages as m where rooms.id = m.room_id order by m.created_at desc limit 1) as last_message_date')
    ) \
        .add_select(
        db.raw(
            'IF(rooms.is_group,false,(select CONCAT(u.first_name," ",u.last_name) from room_members as mem join users as u on u.id = mem.user_id where mem.room_id = rooms.id and u.id != %s limit 1)) as username' %
            g.user['id'])
    ) \
        .add_select(
        db.raw(
            'IF(rooms.is_group,false,(select u.avatar from room_members as mem join users as u on u.id = mem.user_id where mem.room_id = rooms.id and u.id != %s limit 1)) as avatar' %
            g.user['id'])
    ) \
        .add_select(
        db.raw(
            'IF(rooms.is_group,false,(select u.id from room_members as mem join users as u on u.id = mem.user_id where mem.room_id = rooms.id and u.id != %s limit 1)) as friend_id' %
            g.user['id'])
    ) \
        .add_select(
        db.raw(
            '(select count(m.id) from room_members as mem join messages as m on m.room_id = mem.room_id where mem.user_id = %s and mem.room_id = rooms.id and m.id > IF(mem.last_read_message,mem.last_read_message,0)) as unread_messages' %
            g.user['id'])
    ) \
        .join('room_members as rm', 'rm.room_id', '=', 'rooms.id') \
        .where('rm.user_id', g.user['id']) \
        .group_by('rooms.id') \
        .order_by('last_message_date', 'desc') \
        .get()\
        .serialize()

    for room in rooms:
        if not room['is_group']:
            client = _.findWhere(connected_users, {'id': room['friend_id']})
            room['online'] = True if client else False

    return jsonify(rooms), 200


@chat_view.route('/chat/messages/<int:room_id>', methods=['GET'])
@login_required()
def messages(room_id):
    room_member = RoomMember.where('room_id', room_id).where('user_id', g.user['id']).first()
    if not room_member:
        return jsonify({'message': "Unknown Room"}), 400

    room = Room.where('id', room_id).with_('members.user').first()

    messages = Message.select('messages.*', 'u.first_name', 'u.last_name', 'u.avatar') \
        .where('room_id', room_id) \
        .join('users as u', 'u.id', '=', 'messages.sender_id') \
        .order_by('created_at', 'desc') \
        .limit(100) \
        .get()

    return jsonify({'room': room.serialize(), 'messages': messages.serialize()}), 200


@chat_view.route('/chat/room', methods=['POST'])
@login_required()
def create_room():
    data = request.get_json()

    # prepare users ids
    if 'users' in data:
        ids = data['users'] if _.isList(data['users']) else []
    else:
        ids = []

    if 'room_id' in data:
        room = Room.where('id', data['room_id']).where('user_id', g.user['id']).first()
        if not room:
            return jsonify({'message': "Unknown Room"}), 400
    else:
        room = Room()
        room.name = data['name'] if 'name' in data else None
        room.user_id = g.user['id']
        room.is_group = True
        room.save()
        ids.append(g.user['id'])

    ids = _.uniq(ids)
    for id in ids:
        try:
            member = RoomMember()
            member.room_id = room.id
            member.user_id = id
            member.save()

            clients = _.where(connected_users, {'id': id})
            if clients and _.isList(clients):
                for item in clients:
                    join_room('room-%s' % room.id, sid=item['sid'], namespace='/')

        except Exception as e:
            pass

    return jsonify({'room_id': room.id}), 200


@chat_view.route('/chat/room/detach', methods=['POST'])
@login_required()
def detach_room_users():
    data = request.get_json()
    room_id = data['room_id'] if 'room_id' in data else None

    room = Room.where('id', room_id).where('user_id', g.user['id']).first()
    if not room:
        return jsonify({'message': "Unknown Room"}), 400

    # prepare users ids
    if 'users' in data:
        ids = data['users'] if _.isList(data['users']) else []
    else:
        ids = []

    RoomMember.where('room_id', room_id).where('user_id', '!=', g.user['id']).where_in('user_id', ids).delete()

    return jsonify({'message': 'Success'}), 200


@chat_view.route('/chat/room/leave/<int:room_id>', methods=['POST'])
@login_required()
def leave_room(room_id):
    member = RoomMember.select('room_members.user_id', 'r.user_id as owner_id') \
        .join('rooms as r', 'r.id', '=', 'room_members.room_id') \
        .where('room_members.room_id', room_id) \
        .where('room_members.user_id', g.user['id']) \
        .first()

    if not member:
        return jsonify({'message': "Unknown Room"}), 400

    if member.user_id == member.owner_id:
        Room.where('id', room_id).delete()
    else:
        member.delete()

    return jsonify({'message': 'Success'}), 200


@chat_view.route('/chat/update_counter/<int:room_id>', methods=['POST'])
@login_required()
def update_counter(room_id):
    data = request.get_json()
    if data and 'message_id' in data:
        try:
            RoomMember.where('user_id', g.user['id']).where('room_id', room_id).update(last_read_message=data['message_id'])
        except Exception:
            return jsonify({'message':'Bad Request'}), 400

    return jsonify({}), 200




# Socket events
@socketio.on('connect')
def s_connect():
    g.user = get_jwt_user()
    if not g.user:
        return jsonify({}), 403

    # get user rooms
    my_rooms = RoomMember.select('room_id').where('user_id', g.user['id']).group_by('room_id').get()
    for room in my_rooms:
        join_room('room-%s' % room.room_id)

    connected_users.append({
        'id': g.user['id'],
        'sid': request.sid
    })

    socketio.emit('user_connect',{'id':g.user['id']})


@socketio.on('disconnect')
def s_disconnect():
    client = _.findWhere(connected_users, {'sid': request.sid})
    if client:
        user_id = client['id']
        connected_users.remove(client)
        clients_exist = _.where(connected_users,{'id':user_id})
        if not clients_exist or not len(clients_exist):
            socketio.emit('user_disconnect', {'id': user_id})



@socketio.on('message')
def s_message(data):
    rooms = socket_rooms()
    if 'room_id' in data and 'room-%s' % data['room_id'] in rooms:
        socketio.emit('message', data, room='room-%s' % data['room_id'], skip_sid=request.sid)

@socketio.on('user_typing')
def s_user_typing(data):
    rooms = socket_rooms()
    if 'room_id' in data and 'room-%s' % data['room_id'] in rooms:
        socketio.emit('user_typing', data, room='room-%s' % data['room_id'], skip_sid=request.sid)
