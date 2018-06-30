from flask_script import Manager
from flask import session
from flask_migrate import MigrateCommand, Migrate



from info import create_app, db

app = create_app('development')
manage = Manager(app)
# 使用迁移框架，绑定程序，数据库和命令
Migrate(app, db)
manage.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manage.run()