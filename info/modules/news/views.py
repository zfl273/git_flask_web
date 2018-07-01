#导入蓝图对象
from . import news_blue
from flask import session, render_template, current_app, jsonify
from info.models import User
from info.utils.response_code import RET




@news_blue.route('/')
def index():
    user_id = session.get('user_id')# session为redis数据库
    data = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='查询数据库失败')
        data = {
            'user_info': user.to_dict() if user else None
        }

    return render_template('news/index.html', data=data)

# favicon
@news_blue.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')