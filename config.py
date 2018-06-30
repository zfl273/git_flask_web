from redis import StrictRedis
class Config(object):
    DEBUG = None
    SQLALCHEMY_DATABASE_URI = 'mysql://root:woaini2008@localhost:3306/git_flask_web'
    # 动态追踪修改设置，如未设置只会提示警告
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #配置session信息
    SESSION_TYPE = 'redis'
    SESSION_USE_SIGNER = True
    # 构造redis的实例

    SESSION_REDIS = StrictRedis(host='localhost', port=6379)
    PERMANENT_SESSION_LIFETIME = 86400
    # 设置秘钥
    SECRET_KEY = '7FVFfsetIITPF/2TJg66No3ySxosUs2+frMZV4VB3/UZK5cICmc5EQ=='



class developmentConfig(Config):
    DEBUG = True


class productionConfig(Config):
    DEBUG = False

config = {
    'development':developmentConfig,
    'production':productionConfig
}