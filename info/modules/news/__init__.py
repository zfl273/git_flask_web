#  创建蓝图
from flask import Blueprint

news_blue = Blueprint('news_blue', __name__)

#
from . import views