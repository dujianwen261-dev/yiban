# -*- coding: utf-8 -*-
"""
扩展对象模块
============
把 db 这类"扩展实例"单独放在这里，是为了避免循环导入。

为什么不能放在 app.py？
    如果 models.py 需要 db，而 app.py 又要导入 models.py，
    就形成  app.py -> models.py -> app.py  的循环导入，Python 会报错。
    把 db 抽出来放进一个"谁也不依赖"的模块，两边都从这里导入即可。
"""
from flask_sqlalchemy import SQLAlchemy

# 先创建空实例，真正绑定到 app 的动作在 app.py 的 create_app() 里完成
db = SQLAlchemy()
