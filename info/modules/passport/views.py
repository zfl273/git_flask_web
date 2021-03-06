from . import passport_blue
from flask import request, jsonify, current_app, make_response, session
from info.utils.response_code import RET
from info.utils.captcha.captcha import captcha
from info import redis_store
from info import constants, db
import re, random
from info.libs.yuntongxun import sms
from info.models import User
from datetime import datetime

#通过图片的url请求这个地址,给前端发送验证码图片
@passport_blue.route('/image_code')
def register():
    # 1 实现图片生成，前端通过args传过来
    image_code_id = request.args.get('image_code_id')
    if not image_code_id:
        return jsonify(errno=RET.PARAMERR, errmsg='没有数据')
    name, text, image = captcha.generate_captcha()#生成图片验证码
    print(text)
    # redis尝试保存图片验证码，保存失败返回错误信息，保存成功发送
    try:
        redis_store.setex("ImageCode_"+image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存图片验证码失败')
    else:# 返回图片并告知类型
        response = make_response(image)
        response.headers['Content-Type'] = 'image/jpg'
        return response

# 点击获取短信验证码的视图函数,手机号匹配正确，手机号没有注册，图片验证码正确则发送短信
@passport_blue.route('/sms_code',methods=['POST'])
def send_sms_code():
    mobile = request.json.get('mobile')# 手机号
    image_code = request.json.get('image_code')# 短信码
    image_code_id = request.json.get('image_code_id')# uuid
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺少')

    if not re.match(r'^1[345678][0-9]{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号码格式不对')

    try:
        real_image_code = redis_store.get("ImageCode_"+image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg='图片验证码已经过期')
    try:
        redis_store.delete('ImageCode_'+image_code_id)
    except Exception as e:
        current_app.logger.error(e)

    if real_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.PARAMERR, errmsg='图片验证码不一致')
    try:
        user = User.query.filter(User.mobile==mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据库异常')
    else:
        if user:
            return jsonify(errno=RET.DATAEXIST, errmsg='手机号码已注册')

    # 生成随机数
    sms_code = ''
    for i in range(6):
        sms_code += str(random.randint(0, 9))
    print(sms_code)
    # 生成短信验证码
    try:
        redis_store.setex('SMSCode_' + mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='短信验证码存储失败')
    # 第三方接口发送信息
    try:
        ccp = sms.CCP()
        # 手机号，【验证码 ， 有效时间/分】，模版1
        result = ccp.send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES/60], 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='发送短信失败')

    if 0 == result:
        return jsonify(errno=RET.OK, errmsg='发送成功')
    else:
        return jsonify(errno=RET.THIRDERR, errmsg='发送短信失败')

# 注册业务
@passport_blue.route('/register', methods=['POST'])
def register1():
    # 点击注册按钮，前端发送手机号码，手机验证码和密码过来
    mobile = request.json.get('mobile')
    sms_code = request.json.get('sms_code')
    password = request.json.get('password')
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='前端发送数据缺少')

    if not re.match(r'^1[3456789]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号码格式不正确')

    try:
        real_sms_code = redis_store.get('SMSCode_' + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常查询')
    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码过期')
    if real_sms_code != str(sms_code):
        return jsonify(errno=RET.DATAERR, errmsg='短信验证码不正确')

    try:
        redis_store.delete('SMSCode_'+mobile)
    except Exception as e:
        current_app.logger.error(e)
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库查询失败')
    if user:
        return jsonify(errno=RET.DATAEXIST, errmsg='手机号已经注册')

    user = User()
    user.mobile = mobile
    user.nick_name = str(mobile)
    user.password = password

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='存储到mysql数据异常')
    # 把用户信息缓存到redis中,保存到session中
    session['user_id'] = user.id
    session['mobile'] = mobile
    session['nick_name'] = mobile
    return jsonify(errno=RET.OK, errmsg='注册成功')


# 用户登录业务逻辑
@passport_blue.route('/login', methods=['POST'])
def login():
    mobile = request.json.get('mobile')
    password = request.json.get('password')
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='前端发送数据不全')

    if not re.match(r'^1[3456789][0-9]{9}$', mobile):
        return jsonify(errno=RET.DATAERR, errmsg='手机号码不正确')
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    if (not user) or (not user.check_password(password)):
        return jsonify(errno=RET.DATAERR, errmsg='用户名或密码不正确')

    user.last_login = datetime.now()

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='登录时间写入失败')
    session['user_id'] = user.id
    session['mobile'] = user.mobile
    session['nick_name'] = user.nick_name

    return jsonify(errno=RET.OK, errmsg='登录成功')


# 用户退出，清楚缓存信息
@passport_blue.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('mobile', None)
    session.pop('nick_name', None)
    return jsonify(errno=RET.OK, errmsg="OK")