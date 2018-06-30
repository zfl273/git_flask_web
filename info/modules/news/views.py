#导入蓝图对象
from . import news_blue
from flask import session, render_template, current_app





@news_blue.route('/')
def index():
    session['name']='feifei'


    return render_template('news/index.html')

# favicon
@news_blue.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('new/favicon.ico')