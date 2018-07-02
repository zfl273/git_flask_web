#自定义装饰器
from flask import current_app
from flask import g
from flask import session

# 自定义过滤器
from info.models import User


def index_class(index):
    if index==1:
        return 'first'
    elif index == 2:
        return 'second'
    elif index == 3:
        return 'third'
    else:
        return ''





# 自定义装饰器，检查用户登录状态
import functools
def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        user = None
        if user_id:
            try:
                user = User.query.filter_by(id=user_id).first()
            except Exception as e:
                current_app.logger.error(e)

        g.user = user
        return f(*args, **kwargs)
    return wrapper




