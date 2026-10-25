from flask import Flask, render_template, request

app = Flask(__name__)

# 蓝图
from book1 import bookbp1
from book2 import bookbp2
app.register_blueprint(bookbp1, url_prefix='/book1')
app.register_blueprint(bookbp2, url_prefix='/book2')


@app.route('/', methods=['GET', 'POST'])
def index():
    print("请求方式：", request.method)
    page = request.args.get('page')
    pagenum = request.args.get('pagenum')
    print(page, pagenum)

    if request.method == 'POST':
        # 先判断有没有json数据，防止None.get报错
        if request.json:
            name = request.json.get('name')
            print("拿到json里的name：", name)
        else:
            print("这次POST没有携带JSON！")
        return "post"

    return render_template('index.html')


@app.route('/dj2')
def dj():
    return 'djw666'


if __name__ == '__main__':
    app.run(debug=True)
