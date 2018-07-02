






# 自定义装饰器，检查用户登录状态
from flask import session


def login_required(f):
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        user = None
        if user_id:
            try:
                user = User.query.filter_by(id=)




