from flask import Flask, session
from flask_script import Manager
from config import config

app = Flask(__name__)
manage = Manager(app)
app.config.from_object(config['development'])
@app.route('/')
def index():
    return 'index'
if __name__ == '__main__':
    manage.run()