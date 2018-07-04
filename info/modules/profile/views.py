from flask import g, jsonify
from flask import redirect
from flask import render_template

from info.utils.commons import login_required
from info.utils.response_code import RET
from . import profile_blue


# 个人中心基本页面
@profile_blue.route('/info')
@login_required
def user_info():
    user = g.user
    if not user:
        return redirect('/')
    data = {
        'user': user.to_dict()
    }
    return render_template('news/user.html', data=data)

# 基本资料 的页面iframe嵌套

@profile_blue.route('/base_info')
@login_required
def base_info():
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户没有登录')
    data = {
        'user': user.to_dict()
    }
    return render_template('news/user_base_info.html', data=data)