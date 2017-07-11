from flask import Flask, g, jsonify
from flask_orator import Orator
from config import development
from flask_bcrypt import Bcrypt
from libraries.authentification import jwt, get_jwt_user
import wtforms_json
from flask_socketio import SocketIO

app = Flask(__name__)

db = Orator()
bcrypt = Bcrypt()
wtforms_json.init()
socketio = SocketIO(app, async_mode='eventlet')

@app.before_request
def _before_reques():
    g.user = get_jwt_user()


@app.after_request
def _after_request(response):
    response.headers["Access-Control"] = "*"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "X-REQUESTED-WITH, CONTENT-TYPE, ACCEPT, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, HEAD, OPTIONS"
    response.headers["Access-Control-Expose-Headers"] = "CONTENT-TYPE, X-DEPRECATED"

    return response


@app.errorhandler(405)
def page_not_found(e):
    return jsonify({'message': 'Method Not Allowed'}), 405


def create_app():
    app.config.from_object(development)

    db.init_app(app)

    bcrypt.init_app(app)

    from views.auth import auth_view
    from views.users import user_view
    from models.user import authenticate, identity

    jwt.identity_handler(identity)
    jwt.authentication_handler(authenticate)
    jwt.init_app(app)

    # Register Routes
    app.register_blueprint(auth_view, url_prefix='/api')
    app.register_blueprint(user_view, url_prefix='/api')

    return app
