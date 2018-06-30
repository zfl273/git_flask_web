from flask import Flask, session
from flask_script import Manager
from config import config
# 集成数据库扩展
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import MigrateCommand,Migrate
app = Flask(__name__)
app.config.from_object(config['development'])

db = SQLAlchemy(app)



manage = Manager(app)
# 使用迁移框架，绑定程序，数据库和命令
Migrate(app, db)
manage.add_command('db', MigrateCommand)

@app.route('/')
def index():
    return 'index'
if __name__ == '__main__':
    manage.run()