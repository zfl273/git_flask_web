from . import passport_blue
from flask import request, jsonify, current_app, make_response
from info.utils.response_code import RET
from info.utils.captcha.captcha import captcha
from info import redis_store
from info import constants

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



