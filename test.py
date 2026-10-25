#创建核心类 用来创建web服务
from flask import Flask

#实例化app对象
app = Flask(__name__)

from flask_sqlalchemy import SQLAlchemy

#通过这个类连接
class Config(object):
    #开启调试模式（出错时页面显示详细信息）
    DEBUG = True
    #建立与数据库的连接         (引擎)账号密码 @本机                     库         字符集
    SQLALCHEMY_DATABASE_URI = 'mysql://root:abcd2005@127.0.0.1:3306/flask_study?charset=utf8'

#导入配置类 将flask 与 MySQL进行连接
#`app` 里面自带一个配置容器，本质就是一个字典，可以存配置
#`from_object()`Flask 内置方法：
# 从一个对象 / 类里面读取所有大写的属性
# 自动装进 app.config 字典
app.config.from_object(Config)

#SQLAlchemy与flask连接
#（定义模型、增删改查都靠它）
db = SQLAlchemy(app=app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20))

#需要访问网址才执行操作
@app.route('/')
def index():
    # #增加
    st1 = Student(name = '赵六')
    # #把数据加入会话
    db.session.add(st1)
    # #提交，真正写入数据库
    db.session.commit()

    # #删除
    # #     查询    筛选条件    找到数据    删除                删除
    Student.query.filter(Student.id==4).delete()
    db.session.commit()

    # #修改
    Student.query.filter(Student.id==3).update({'name':'dj'})
    db.session.commit()

    #查询               主键查询
    st2 = Student.query.get(2)
    print(st2.name)
    st_all = Student.query.all()
    print(st_all)

    return 'test'


if __name__ == '__main__':
    #flask 应用上下文，数据库操作必须在上下文里面执行
    with app.app_context():
        #根据你写的所有 Model 类，在数据库里面创建对应的数据表
        # 已经存在的表不会重复创建、不会覆盖
        db.create_all()
    app.run()