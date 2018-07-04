from flask import current_app
from flask import g, jsonify
from flask import redirect
from flask import render_template
from flask import request, session

from info import constants
from info import db
from info.utils.commons import login_required
from info.utils.response_code import RET
from . import profile_blue
from info.utils.image_storage import storage

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

@profile_blue.route('/base_info',methods=['GET','POST'])
@login_required
def base_info():
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户没有登录')
    if request.method=='GET':
        data = {
            'user': user.to_dict()
        }
        return render_template('news/user_base_info.html', data=data)
    nick_name = request.json.get('nick_name')


# 头像设置
@profile_blue.route('/pic_info',methods=['GET','POST'])
@login_required
def save_user_avatar():
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR,errmsg='没登录')
    if request.method == 'GET':
        data = {
            'user': user.to_dict()
        }
        return render_template('news/user_pic_info.html', data=data)

    avatar = request.files.get('avatar')
    if not avatar:
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺少')
    try:
        image_data = avatar.read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.IOERR, errmsg='读取文件错误')

    try:
        image_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传图片错误')
    user.avatar_url = image_name
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')

    image_url = constants.QINIU_DOMIN_PREFIX + image_name
    return jsonify(errno=RET.OK, errmsg="ok", data={'avatar_url':image_url})
