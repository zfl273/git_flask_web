#导入蓝图对象
from . import news_blue
from flask import session, render_template





@news_blue.route('/')
def index():
    session['name']='feifei'


    return render_template('news/index.html')