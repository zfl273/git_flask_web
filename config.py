class Config(object):
    DEBUG = None
    SQLALCHEMY_DATABASE_URI = 'mysql://root:woaini2008@localhost:3306/git_flask_web'
    # 动态追踪修改设置，如未设置只会提示警告
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class developmentConfig(Config):
    DEBUG = True


class productionConfig(Config):
    DEBUG = False

config = {
    'development':developmentConfig,
    'production':productionConfig
}