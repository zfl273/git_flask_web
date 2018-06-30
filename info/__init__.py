# 集成数据库扩展
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
# 将session存入redis
from flask_session import Session
from config import config


db = SQLAlchemy()

def create_app(config_name):

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    Session(app)
    db.init_app(app)
    return app