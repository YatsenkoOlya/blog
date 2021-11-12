import sqlite3
import os
from flask import Flask, render_template, request, g, flash, abort, redirect, url_for, make_response
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
# from UserLogin import UserLogin

# конфигурация
DATABASE = '/home/CS/jacenko_o_o/public_html/cgi-bin/mydb/main.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path,'main.db')))

# login_manager = LoginManager(app)
# login_manager.login_view = 'login'
# login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
# login_manager.login_message_category = "success"

#
# @login_manager.user_loader
# def load_user(user_id):
#     print("load_user")
#     return UserLogin().fromDB(user_id, dbase)

#установление соединеня с бд
def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    # запись из бд не в виде картежей, а в виде словаря
    conn.row_factory = sqlite3.Row
    return conn

# Вспомогательная функция для создания таблиц БД
def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read()) # запускает выполнение sql скриптов, ктр были прочитаны из файла sq_db.sql
    db.commit() # записываем изменения в бд
    db.close()

#create_db()

# Соединение с БД, если оно еще не установлено
def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

# Установление соединения с БД перед выполнением запроса
dbase = None
@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)

# Закрываем соединение с БД, если оно было установлено
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()

# Главная страница
@app.route("/")
def index():
    return render_template('index.html', menu=dbase.getMenu(), writers=dbase.getWritersAnonce(), posts=dbase.getPostsAnonce())

@app.route("/add_post", methods=["POST", "GET"])
def addPost():
    id_post = "0"
    if request.method == "POST":
    #     # user_id = current_user.get_id()
    #     if len(request.form['name']) > 0 and len(request.form['post']) > 5:
        res = dbase.addPost(request.form['name'], request.form['post'], request.form['auth'], request.form['topic'])
    #проверка
        res2 = dbase.addAuthor(request.form['auth'])
    #         res2 = dbase.addTopic(request.form['topic'])
    #         if not (res and res2):
    #             flash('Ошибка добавления поста', category='error')
    #         else:
    #             flash('Пост добавлена успешно', category='success')
    #             # id_post = dbase.getLastPostId(user_id)['id']
    #     else:
    #         flash('Ошибка добавления поста', category='error')

    return render_template('add_post.html', menu=dbase.getMenu(), title="Добавление статьи", id_post=id_post)

@app.route("/showPost/<id>")
#@login_required
def showPost(id):
    #print("showPost")
    title, post = dbase.getPost_by_id(id)
    #print(id)
    if not title:
        abort(404)
    text = post.split('\n')
    #print(text)
    count = dbase.getCountFiles(id)['COUNT(*)']
    #print("кол-во фотографий")
    #print(count)
    #print(dbase.getFirstFileId(id)['id_file'])
    return render_template('post.html', menu=dbase.getMenu(), title=title, post=text, post_id=id, count=count, file_id=dbase.getFirstFileId(id)['id_file'])

# Пользователь (писатель постов)
@app.route("/writer/<alias>")
# @login_required
def showWriters(alias):
    id, name = dbase.getWriter(alias)
    id_user = 0
    if current_user.is_authenticated:
        id_user = current_user.get_is_admin()
        #print(id_user)

    return render_template('writer.html', menu=dbase.getMenu(), title=name, id=id, posts=dbase.getPostsAnonce1(id), w_id=alias, id_user=id_user)

@app.route('/deleteWriter/<alias>')
def deleteWriter(alias):
    dbase.deleteWritersPost(alias)
    dbase.deleteWriter(alias)
    return redirect(url_for('index'))

@app.route('/deletePost/<alias>/<id_post>')
def deletePost(alias, id_post):
    dbase.deleteWriterPost(id_post)
    dbase.deletePostFiles(id_post)
    #dbase.deleteWriter(alias)
    return redirect(url_for('showWriters', alias=alias))

# Авторизация
# @app.route("/login", methods=["POST", "GET"])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('profile'))
#
#     if request.method == "POST":
#         user = dbase.getUserByEmail(request.form['email'])
#         if user and check_password_hash(user['psw'], request.form['psw']):
#             userlogin = UserLogin().create(user)
#             rm = True if request.form.get('remainme') else False
#             login_user(userlogin, remember=rm)
#             return redirect(request.args.get("next") or url_for("profile"))
#
#         flash("Неверная пара логин/пароль", "error")
#
#     return render_template("login.html", menu=dbase.getMenu(), title="Авторизация")

# # Регистрация
# @app.route("/register", methods=["POST", "GET"])
# def register():
#     if request.method == "POST":
#         if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
#             and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
#             hash = generate_password_hash(request.form['psw'])
#             res = dbase.addUser(request.form['name'], request.form['email'], hash, 0)
#             if res:
#                 flash("Вы успешно зарегистрированы", "success")
#                 return redirect(url_for('login'))
#             else:
#                 flash("Ошибка при добавлении в БД", "error")
#         else:
#             flash("Уже есть пользователь с таким email", "error")
#
#     return render_template("register.html", menu=dbase.getMenu(), title="Регистрация")
#
# @app.route('/logout')
# #@login_required
# def logout():
#     logout_user()
#     flash("Вы вышли из аккаунта", "success")
#     return redirect(url_for('login'))

# Личный кабинет
@app.route('/profile')
#@login_required
def profile():
    #print('is_admin')
    #print(current_user.get_is_admin())
    id_user = 0
    if current_user.is_authenticated:
        id_user = current_user.get_is_admin()
        #print(id_user)
    return render_template("profile.html", menu=dbase.getMenu(), title="Личный кабинет", posts=dbase.getPostsAnonce1(current_user.get_id()), id_user=id_user)

# # Аватарка авторизированного пользователя
# @app.route('/userava/<user_id>', methods=["POST", "GET"])
# # @login_required
# def userava(user_id):
#     user = UserLogin().fromDB(user_id, dbase)
#     img = user.getAvatar(app)
#     if not img:
#         return ""
#
#     h = make_response(img)
#     h.headers['Content-Type'] = 'image/png'
#     return h

# @app.route('/userpost/<user_id>', methods=["POST", "GET"])
# @login_required
# def userpost(user_id):
    # user = UserLogin().fromDB(user_id, dbase)
    # img = user.getAvatar(app)
    # if not img:
    #     return ""

    # h = make_response(img)
    # h.headers['Content-Type'] = 'image/png'
    # return h
#
# @app.route('/newName/<user_id>', methods=["POST", "GET"])
# # @login_required
# def newName(user_id):
#     newName = request.form['name']
#     dbase.changeUsersName(user_id,newName)
#     return  redirect(url_for('profile'))
# @app.route('/newPsw/<user_id>', methods=["POST", "GET"])
# # @login_required
# def newPsw(user_id):
#     newPsw = request.form['npsw']
#     dbase.changeUsersPsw(user_id,generate_password_hash( newPsw))
#     return  redirect(url_for('profile'))

#
# # Загрузить аватарку
# @app.route('/upload', methods=["POST", "GET"])
# #@login_required
# def upload():
#     if request.method == 'POST':
#         file = request.files['file']
#         #print(file)
#         if file:
#             try:
#                 img = file.read()
#                 res = dbase.updateUserAvatar(img, current_user.get_id())
#                 if not res:
#                     flash("Ошибка обновления аватара 1", "error")
#                 flash("Аватар обновлен", "success")
#             except FileNotFoundError as e:
#                 flash("Ошибка чтения файла", "error")
#         else:
#             flash("Ошибка обновления аватара", "error")
#
#     return redirect(url_for('profile'))

@app.route('/upload_post/<id_post>', methods=["POST", "GET"])
#@login_required
def upload_post(id_post):
    file = request.files.getlist('file')
    #print(file)
    if file:
        for f in file:
            try:
                img = f.read()
                res = dbase.addPFile(img, id_post)
                if not res:
                    flash("Ошибка добавления файла", "error")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
    else:
        flash("Ошибка добавления файла", "error")

    return redirect(url_for('addPost'))

@app.route('/posts_file/<count>', methods=["POST", "GET"])
# @login_required
def posts_file( count):
    #print(count)
    img = dbase.getFile(count)
    if not img:
        return ""
    #print("тест")
    #print(img)
    return img['p_file']

if __name__ == "__main__":
    app.run(debug=True)
