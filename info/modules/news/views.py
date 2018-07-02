#导入蓝图对象
from flask import g
from flask import request

from info import db
from . import news_blue
from flask import session, render_template, current_app, jsonify
from info.models import User, News, Category
from info.utils.response_code import RET
from info.utils.commons import login_required


# *****项目首页
@news_blue.route('/')
@login_required
def index():
    user = g.user
    # user_id = session.get('user_id')# session为redis数据库
    # data = None
    # user = None
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)
    #         return jsonify(errno=RET.DBERR, errmsg='查询数据库失败')
    # ****新闻点击排行
    # 默认按照新闻的点击次数倒序排列
    try:
        news_list = News.query.filter().order_by(News.clicks.desc()).limit(6)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库排序错误')
    if not news_list:
        return jsonify(errno=RET.NODATA, errmsg='暂无数据')
    print('news_list为：', news_list)
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_dict())# 转成字典
    #***** 新闻分类数据展示
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库查找分类失败')
    if not categories:
        return jsonify(errno=RET.NODATA, errmsg='暂无分类数据')
    categories_list = []
    for category in categories:
        categories_list.append(category.to_dict())


    data = {
        'user_info': user.to_dict() if user else None,
        'news_dict_list': news_dict_list,
        'categories_list': categories_list
    }

    return render_template('news/index.html', data=data)

# *****首页新闻列表数据通过ajax刷新
@news_blue.route('/news_list')
def get_news_list():
    cid = request.args.get('cid', '1')
    page = request.args.get('page', '1')
    per_page = request.args.get('per_page', '10')
    try:
        cid, page, per_page = int(cid), int(page), int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数格式不正确')
    # 定义过滤条件
    filters = []
    if cid > 1:# 不是：最新
        filters.append(News.category_id == cid)
    try:# 如果cid
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,per_page,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据库异常了')
    news_list = paginate.items
    total_page = paginate.pages
    current_page = paginate.page
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_dict())
    data = {
        'news_dict_list': news_dict_list,
        'total_page': total_page,
        'current_page': current_page
    }
    return jsonify(errno=RET.OK, errmsg='OK', data=data)

# **** 详细新闻 模版注入
@news_blue.route('/<int:news_id>')
@login_required
def get_news_detail(news_id):
    user = g.user
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询新闻数据库异常')

    if not news:
        return jsonify(errno=RET.NODATA, errmsg='新闻已经找不到')

    news.clicks += 1
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='数据库存取失败')
    data = {
        'user': user.to_dict() if user else None,
        'news_detail': news.to_dict()
    }

    return render_template('news/detail.html', data=data)

# *****用户点击收藏
@news_blue.route('/news_collect', methods=['POST'])
@login_required
def news_collect():
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户没有登录')

    news_id = request.json.get('user_id')
    action = request.json.get('action')
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')
    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数格式错误1')
    if action not in ['collect', 'cancel_collect']:
        return jsonify(errno=RET.PARAMERR, errmsg='参数格式错误2')
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库查询失败')
    if not news:
        return jsonify(errno=RET.NODATA, errmsg='新闻数据不存在')

    if action == 'collect':
        if news not in user.collection_news:
            user.collection_news.append(news)
    else:
        user.collection_news.remove(news)
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')

    return jsonify(errno=RET.OK, errmsg='OK')


# favicon
@news_blue.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')