from flask import Flask
from config import development
from flask_orator import Orator


app = Flask(__name__)

app.config.from_object(development)
db = Orator(app)

if __name__ == '__main__':
    db.cli.run()