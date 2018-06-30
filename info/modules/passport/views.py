from . import passport_blue
from flask import request, jsonify, current_app, make_response
from info.utils.response_code import RET
from info.utils.captcha.captcha import captcha
from info import redis_store
from info import constants
import re, random
from info.libs.yuntongxun import sms
from info.models import User

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



