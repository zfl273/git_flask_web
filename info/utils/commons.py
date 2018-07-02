
# 自定义过滤器
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
# from flask import session
#
#
# def login_required(f):
#     def wrapper(*args, **kwargs):
#         user_id = session.get('user_id')
#         user = None
#         if user_id:
#             try:
#                 user = User.query.filter_by(id=)




