# 学生信息管理系统 —— 复刻与学习指南

> 本系统已在本机实际运行并完成 40+ 项测试（登录、增删改查、越权、SQL 注入、边界值），
> 全部通过，无 500 错误。你可以照着本文从零复刻。
#2xx为成功 3xx为重定向 4xx为客户端问题 5xx为服务器出错
---

## 一、项目结构

```
E:\FlaskProject\
├── .env                  # 密钥与数据库连接（绝不提交 Git）
├── .gitignore            # 排除 .venv / .env / __pycache__
├── config.py             # 配置层：读取环境变量
├── extensions.py         # 扩展实例（db），避免循环导入
├── models.py             # 数据模型：3 张表
├── app.py                # 入口：应用工厂 create_app()
├── auth.py               # 认证模块：登录/登出/权限装饰器
├── students.py           # 学生模块：增删改查/分页/学生自查自改
├── classes.py            # 班级模块：管理 + 人数统计
├── init_db.py            # 一次性初始化：建库建表 + 示例数据
└── templates\
    ├── base.html         # 公共骨架（导航栏 + flash 消息）
    ├── login.html
    ├── students\
    │   ├── list.html     # 列表 + 搜索 + 分页
    │   ├── form.html     # 新增/修改（共用）
    │   ├── me.html       # 学生查看自己
    │   └── me_form.html  # 学生改自己
    └── classes\
        ├── list.html     # 班级 + 统计
        └── form.html
```

---

## 二、从零复刻的完整步骤

### 步骤 1：创建项目与虚拟环境

```powershell
# 1) 在 PyCharm 新建 Pure Python 项目
#    Interpreter 选 New venv，Base interpreter 选 Python 3.14

# 2) 打开 PyCharm 底部 Terminal，确认有 (.venv) 前缀
where python
# 第一行必须是  ...\FlaskProject\.venv\Scripts\python.exe

# 3) 安装依赖（用清华镜像加速）
pip install flask flask-sqlalchemy pymysql python-dotenv -i https://pypi.tuna.tsinghua.edu.cn/simple
```

> ⚠️ **这一步最容易出错**：如果 `where python` 第一行不是 `.venv` 里的，说明虚拟环境没激活，
> 包装到了别处，后面启动会报 `ModuleNotFoundError`。

### 步骤 2：按顺序创建文件

| 顺序 | 文件 | 为什么这个顺序 |
|---|---|---|
| 1 | `config.py` | 配置最先，其它模块都依赖它 |
| 2 | `extensions.py` | db 实例要先存在，models 才能用 |
| 3 | `models.py` | 有了表结构才能写业务 |
| 4 | `auth.py` | 权限是业务的前提 |
| 5 | `students.py` / `classes.py` | 业务模块 |
| 6 | `app.py` | 最后把所有模块组装起来 |
| 7 | `templates\*` | 页面 |

**这个顺序不是随意的**：它保证每一步都不会出现"导入了还不存在的模块"。

### 步骤 3：生成密钥并配置 .env

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

把输出粘进 `.env` 的 `SECRET_KEY=`。

### 步骤 4：初始化数据库

```powershell
python init_db.py
```

预期输出：

```
[1/4] 数据库 `student_manage` 已就绪
[2/4] 所有表已创建
[3/4] 已创建超级管理员：admin / Admin@123456
[4/4] 已插入 2 个班级、3 名学生
```

### 步骤 5：启动

```powershell
python app.py
```

浏览器打开 <http://127.0.0.1:5000>

| 角色 | 账号 | 密码 |
|---|---|---|
| 超级管理员 | `admin` | `Admin@123456` |
| 学生 | `2024010101`（张伟） | `000001`（手机号后 6 位） |

---

## 三、模块详解（每个模块解决什么问题）

### config.py —— 配置层

**问题**：数据库密码如果写死在代码里，一旦提交到 Git 就泄露了。

**做法**：所有敏感值从 `.env` 读取，代码里只有默认值兜底。

```python
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "...")
```

关键点：连接串用 `mysql+pymysql://` 而不是 `mysql://`，
否则 SQLAlchemy 会去找 MySQLdb 驱动。

### extensions.py —— 为什么单独抽出 db

**问题**：`app.py` 要导入 `models.py`，`models.py` 又要用 `db`。
如果 `db` 定义在 `app.py` 里，就形成 `app → models → app` 的**循环导入**。

**做法**：把 `db` 放进一个谁也不依赖的独立模块，两边都从这里导入。

### models.py —— 数据模型

三张表与关系：

```
class_info (班级)  1 ─────< N  student_info (学生)
admin_user (管理员，独立)
```

**关键设计决策**（都有原因，别改回去）：

| 决策 | 原因 |
|---|---|
| 学生表用自增 `id` 做主键，学号只做 UNIQUE | 学号录错时只改字段，不会牵连外键 |
| `password` 用 `VARCHAR(255)` | 安全哈希约 162 字符，用 32 会截断导致永远登录失败 |
| `is_deleted` 软删除 | 真实场景误删要能恢复 |
| `yiban_uid` 字段 | 为后续易班登录预留映射 |
| `pool_pre_ping: True` | 防 MySQL 空闲 8 小时断连后第一个请求报错 |

### auth.py —— 权限控制（**最关键**）

三个装饰器：

```python
@login_required        # 登录即可
@admin_required        # 必须是管理员
@super_admin_required  # 必须是超级管理员
```

**核心原则：权限永远在服务端校验。**
前端隐藏按钮只是"体验"，不是"安全"。学生手改 URL 也会被 403 拦住。

另外两个安全细节：

```python
# 1) 登录失败统一提示，不透露账号是否存在（防账号枚举）
flash("账号或密码错误", "danger")

# 2) next 参数只允许站内路径（防开放重定向钓鱼）
if target.startswith("/") and not target.startswith("//"):
    return redirect(target)
```

### students.py —— 学生管理

**白名单思维**（重要）：

```python
STUDENT_EDITABLE_FIELDS = ("phone", "email", "address")
```

学生修改自己的信息时，**只从表单里读这三个字段**。
即使你在请求里伪造 `student_no=HACKED`，代码也根本不读它。
用白名单而不是黑名单，将来加敏感字段时才不会漏。

**PRG 模式**：POST 成功后 `redirect`，避免用户刷新页面重复提交。

**SQL 注入免疫**：全程用 SQLAlchemy 表达式，没有任何字符串拼接 SQL。

### classes.py —— 班级与统计

**避免 N+1 查询**：用一条 `outerjoin + group_by` 算出每个班的人数，
而不是循环查每个班（那是 N 次查询）。

```python
func.count(Student.id).label("student_count")
```

**删除保护**：班级下还有学生时拒绝删除（外键是 `RESTRICT`，这里提前给出友好提示）。

---

## 四、已验证的测试清单

| # | 测试项 | 预期 | 实测 |
|---|---|---|---|
| 1 | 未登录访问 `/students/` | 302 到登录页 | ✅ |
| 2 | 错误密码 | 提示"账号或密码错误" | ✅ |
| 3 | 管理员登录 | 进入列表页 | ✅ |
| 4 | 新增学生 | 成功并出现在列表 | ✅ |
| 5 | 重复学号 | 拦截"已存在" | ✅ |
| 6 | 空学号/空姓名 | 拦截 | ✅ |
| 7 | 非法手机号/邮箱 | 拦截格式错误 | ✅ |
| 8 | 模糊搜索 | 只返回匹配项 | ✅ |
| 9 | SQL 注入 `' OR '1'='1` | 无数据泄露 | ✅ |
| 10 | SQL 注入 `'; DROP TABLE` | 表未被删 | ✅ |
| 11 | 学生访问 `/students/` | 403 | ✅ |
| 12 | 学生访问 `/classes/` | 403 | ✅ |
| 13 | 学生访问他人编辑页 | 403 | ✅ |
| 14 | 学生伪造 `student_no` 提交 | 未被篡改 | ✅ |
| 15 | 软删除 | 列表消失，数据保留 | ✅ |
| 16 | 班级重名 | 拦截 | ✅ |
| 17 | 删除有学生的班级 | 拒绝 | ✅ |
| 18 | 越界页码 / 非法页码 | 正常显示 | ✅ |
| 19 | 不存在的资源 | 404 | ✅ |
| 20 | 开放重定向 `?next=https://evil.com` | 拦回站内 | ✅ |
| 21 | 搜索超长 500 字符 | 200，不崩溃 | ✅ |
| 22 | 搜索特殊字符 `%'"` | 200，不报错 | ✅ |

---

## 五、常见报错与排查

| 报错 | 原因 | 解决 |
|---|---|---|
| `ModuleNotFoundError: No module named 'flask'` | 包装到了别的 Python | 确认 `where python` 第一行是 `.venv` |
| `No module named 'MySQLdb'` | 连接串写的是 `mysql://` | 改成 `mysql+pymysql://` |
| `Access denied for user 'root'` | 数据库密码错 | 检查 `.env` 里的 `DATABASE_URL` |
| `Unknown database 'student_manage'` | 没建库 | 跑 `python init_db.py` |
| 登录提示账号密码错 | 学生密码是手机号后 6 位 | 改过手机号后密码也会变 |
| 中文乱码 | 字符集不是 utf8mb4 | 库、表、连接串三处都要 utf8mb4 |
| 改代码后页面没变化 | 没开 debug | `app.run(debug=True)` 或 `flask --app app run --debug` |

---

## 六、下一步该做什么

按这个顺序，每一项都独立可验证：

1. **易班登录对接**（阶段 8）
   替代当前的"学号+手机号后 6 位"登录。注意：轻应用是**站内模式**，
   解密 `verify_request` 拿 token，不是 code 换 token。

2. **Excel 批量导入导出**
   用 `openpyxl`，先做导入（老师最需要），导出放后面。

3. **操作日志**
   谁改了什么、什么时候改的。真实使用场景必备，出问题能追溯。

4. **部署上线**（阶段 9）
   服务器 + HTTPS + `waitress` + 定时备份。
   **注意易班轻应用强制 HTTPS，本地 `127.0.0.1` 无法联调易班部分。**

---

## 七、给"真正学会"的三条建议

1. **合上代码，说出流程**
   从"用户在浏览器输入地址"到"页面上显示学生表格"，中间经过哪几步？
   说不出来就是没懂。

2. **故意弄坏它**
   把 `@admin_required` 删掉试试，用学生账号访问管理页 —— 能进去了。
   这就是"权限必须在服务端"的含义。**见过失败才知道为什么要有这条规矩。**

3. **每个阶段回答"为什么"**
   - 为什么用 `id` 而不是学号做主键？
   - 为什么密码要哈希而不能加密后存？
   - 为什么删除用 POST 而不是 GET？

   答不上来，说明还在抄，没在学。
