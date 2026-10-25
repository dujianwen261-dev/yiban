#一行注释
"""
多行注释
"""

#变量命名规则
#变量命名规则
#变量名只能包含字母、数字和下划线，且不能以数字开头
#变量名是区分大小写的
myNum = 1
a = "word"
b = False

#元组 作用：存储多个元素，不可重复，可嵌套，不可修改
c = (1, 3, 5)
#列表 作用：存储多个元素，可重复，可嵌套，可修改
a = [1,2,3,4]
#集合 作用：存储多个元素，不可重复，可嵌套，可修改
b = {1, 2, 3}
#字典 作用：存储多个元素，键值对，可重复，可嵌套，可修改
d = {"name": "zhang", "age": 18}

# print(f"hello{myNum}", a, b, c, d)
# #输出不换行
# print("我是人\t我是鬼", end="")

# x = int(input("请输入内容："))
#str是字符串
# b = str(x)
# c = float(x)
# print(b, c)

# x = 2
# import random
# #次方
# x = x**random.randint(1, 10)
# print(x)

#布尔运算 not and or
# a = True
# b = False
# print(a and b)
# print(a or b)
# print(not a)

#字符串操作
# s1 = "H"
# s2 = "i"
# hi = s1 + s2
# hh = s1*2
# hii = s1 + s2*2
# # print(hi, hh, hii)
#
# a = 11
# b = a % 2
# c = b == 0
# if c:
#     print("偶数")
# else:
#     print("奇数")

# a = 55
# if a < 0 or a > 100:
#     print("不合法")
# elif a <= 60:
#     print("不及格")
# else:
#     print("及格")

# a = 0
# while a < 10:
#     print(a)
#     a += 1
#     if a == 5:
#         continue
#     # if a == 7:
#     #     break
# else:
#     print("循环结束")

# for i in range(10):
#     print(i, end = "")
# string = "abcd"
# for i in string:
#     print(i, end = "")

# a = range(-1, 5)
# print(a)
# for i in a:
#     print(i, end = "")

# a = "my name is xxx"
# print(a)
# b = a[:5]
# print(b)
# c = a[1:]
# print(c)
# d = a[:]
# print(d)
# e = a[1:5]
# print(e)
# f = a[1:10:2]
# print(f)
# #反转
# g = a[::-1]
# print(g)
# h = a[-5:-1]
# print(h)

#通过空格把字符串里面的每一段分割出来
# arr = a.split(" ")
# print(arr)
# string = "-".join(arr)
# print(string)

#字符串转换 第一个字符大写
# a = "hello".capitalize()
# print(a)
#每一段首字母大写
# a = "hello world".title()
# print(a)
#全部大写
# a = "hello".upper()
# print(a)
#全部小写
# a = "HEllo".lower()
# print(a)

#删除空白字符
# b = "     hello".lstrip()
# print(b)
# b = "hello     ".rstrip()
# print(b)
# b = "     hello     ".strip()
# print(b)

# string = "app"
# s = string[0]
# print(s)
# arr = [1, 2, 3, 4]
# a = arr[0]
# print(a)

# array = [[1, 2,],[3, 4], [5, 6]]
# a = array[1]
# print(a)
# b = array[1][1]
# print(b)

#列表无限嵌套
# array = [
#     [[1, 2], [3, 4]],
#     [[5, 6], [4, 3]],
#     [[7, 8], [6, 5]]
# ]
# # a = array[2][1][0]
# # print(a)
# for a in array:
#     for b in a:
#         for c in b:
#             print(c)

# b = 6
arr = [1, False, "hi", b, [1, 2, 3]]
# if b not in arr:
#     print(1)
# else:
#     print(0)
# arr.append("abc")
# print(arr)
# arr.insert(1, 't')
# print(arr)
# arr.pop(0)
# print(arr)
# arr.remove("hi")
# print(arr)
# arr.clear()
# print(arr)
# del arr
# print(arr)
#[]列表可以修改
# arr[0] = 123
# print(arr)
#赋值a到b 最好用copy 这样的话b不会随着a的修改而修改
#b = arr.copy()
#如果直接赋值b会随着a的变化而变化 因为b是a的引用
# b = a

#字符串不可以修改
# string = "ac"
# # string[0] = "b"
# print(string)

# a = [4, 2, 3, 1]
# a.sort()
# print(a)
# a = sorted(a)

#()元组不可修改
# a[0] = 3 报错
# a = (1, 2, "33")
# # print(a[0])
# for i in arr:
#     print(i, end = " ")
# print()
# for i in range(len(a)):
#     print(a[i])

#集合 作用：存储多个元素，不可重复，可嵌套，可修改
# s = {1, 3, 3, 4, 3}
# print(s)

#字典 作用：存储多个元素，键值对，可重复，可嵌套，可修改
#键就是前面的：  value就是后面的
#键必须是不可变类型
#(1, 2): 5 ✅ 合法 —— 元组是不可变的，可以作为字典的键
#[1, 2]: 5 ❌ 报错 —— 列表是可变的，不能作为字典的键
d = {"name": "zhang", "age": 18, (1, 2): 5}
# print(d)
# for i in d:
#     print(i, d[i])
# print(d.keys())
# print(d.values())
# print(d.items())
# for k, v in d.items():
#     print(k)
#     print(v)
# d["name"] = "dog"
# print(d)
# del d["age"]
# print(d)
# d.clear()
# print(d)

#表示一个空字典
# a = {}
#表示一个空集合
# b = set()

#使用函数进行代码的封装 也可以称为方法

# def day():
#     print("起床")
#     print("刷牙")
#     print("洗脸")
#     print("吃早餐")
#     print("去学校")
# day()

# def isDouble(n):
#     if n % 2 == 0:
#         return True
#     else:
#         return False
# def isDouble(n):
#     return n % 2 == 0
# num = 12
# if isDouble(num):
#     print("偶数")
# else:
#     print("奇数")

#这里的DAY是全局变量
# DAY = 0
# def day():
#     #这里使用global关键字声明DAY是全局变量
#     global DAY
#     if DAY % 2 == 0:
#         print(111)
#     else:
#         print(0)
#     DAY += 1
# day()
# print(DAY)

# def main():
#     for i in range(10):
#         a()
#
# def a():
#     b()
#     c()
#
# def b():
#     pass
#
# def c():
#     # #空语句 用于占位 让代码结构完整
#     pass
#
# """
# 主函数入口 判断是不是在当前这个文件里执行的
# 因为一个项目通常有多个py文件，其他的py文件会被引用到一个最终调用的main.py文件里执行
# 这样做可以防止这个脚本被其他地方引入的时候被不必要的执行了
# """
# print(__name__)
# if __name__ == '__main__':
#     main()

# def g():
#     return 1, 2
#
# b = g()
# #结果为一个元组
# print(b)
# #我们可以把g函数返回一个元组来拆包
#字典列表集合均可以拆包
# a, c = g()
# print(a, c)

#不定长参数 可以接受任意个参数
#普通参数要写在不定长参数前面
# def x(n, *args):
#     print(args)
#     for i in args:
#         print(i)
# x(1, 2, 3, 4, 5 ,6)

#默认参数 顺序要写在 n 后面
#如果是带两个**的不定参数，那么这个参数必须放在最后
#一个* 的参数叫包裹位置参数，可以接受任意个参数
#两个**的参数叫关键字参数，可以接受任意个参数
def x(n, age = 18, *args, **kwargs):
    # print(args)
    if age >= 18:
        print(n)
        for i in args:
            print(i)
    else:
        print("no!")
    print(kwargs["ns"])
    print(kwargs["nt"])
x(1, 20, 2, 3, 4, 5 , 6, ns = 15, nt = 16)