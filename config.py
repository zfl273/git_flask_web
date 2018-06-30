class Config(object):
    DEBUG = None


class developmentConfig(Config):
    DEBUG = True


class productionConfig(Config):
    DEBUG = False

config = {
    'development':developmentConfig,
    'production':productionConfig
}