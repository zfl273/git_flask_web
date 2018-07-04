from flask import current_app
from flask import g, jsonify
from flask import redirect
from flask import render_template
from flask import request, session

from info import constants
from info import db
from info.models import Category
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
    signature = request.json.get('signature')
    gender = request.json.get('gender')

    if not all([nick_name, signature,gender]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺少')
    if gender not in ['MAN','WOMEN']:
        return jsonify(errno=RET.PARAMERR, errmsg='参数格式不对')
    user.nick_name = nick_name
    user.signature = signature
    user.gender = gender
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')
        # 修改redis缓存中昵称信息
    session['nick_name'] = nick_name
    # 返回结果
    return jsonify(errno=RET.OK, errmsg='OK')


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

# 修改密码
@profile_blue.route('/pass_info',methods=['GET','POST'])
@login_required
def pass_info():
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR,errmsg='用户未登录')
    if request.method == 'GET':
        return render_template('news/user_pass_info.html')
    # 获取参数
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")
    # 检查参数的完整性
    if not all([old_password,new_password]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数缺失')
    # 检查旧密码是否正确
    if not user.check_password(old_password):
        return jsonify(errno=RET.PWDERR,errmsg='密码错误')
    # 保存新密码,generate_password_hash
    user.password = new_password
    # 提交数据到数据库中
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')

    # 返回结果
    return jsonify(errno=RET.OK,errmsg='OK')




@profile_blue.route('/news_release',methods=['GET','POST'])
@login_required
def news_release():
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户mei登陆')

    if request.method == 'GET':
        try:
            categories = Category.query.filter(Category.id>1).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='数据库异常')
        if not categories:
            return jsonify(errno=RET.NODATA, errmsg='无分类数据 ')

        category_list = []
        for category in categories:
            category_list.append(category.to_dict())

        data = {
            'categories':category_list
        }
        return render_template('news/user_news_release.html', data=data)















