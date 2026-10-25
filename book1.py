from flask import Blueprint

# 创建蓝图对象  当前模块名 __name__ flask靠他找这个蓝图对应的静态文件，模板路径
bookbp1 = Blueprint('book1', __name__)

#注意！这个`/`不是整个网站的根`http://127.0.0.1:5000/`！
#它最终的完整地址，取决于 app.py 注册蓝图时设置的`url_prefix`
# 蓝图对象.route()  装饰器，定义路由  路由是蓝图对象的路径
@bookbp1.route('/')
def index():
    return 'book1'

#需要拼接/book1study 才是完整的地址
@bookbp1.route('/book1study')
def book1study():
    return 'book1study'