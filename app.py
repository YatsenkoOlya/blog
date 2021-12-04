import sqlite3
import os
from flask import Flask, render_template, request, g, flash, abort, redirect, url_for, make_response
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash

# конфигурация
DATABASE = '/tmp/main.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path,'main.db')))

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
    return render_template('index.html', posts=dbase.getPostsAnonce())

@app.route("/all_posts", methods=["POST", "GET"])
def show_all_posts():
    db = get_db()
    dbase = FDataBase(db)
    posts = dbase.get_all_posts()

    return render_template('posts.html', posts=posts)
#
# @app.route("/add_post", methods=["POST", "GET"])
# def add_post():
#     db = get_db()
#     dbase = FDataBase(db)
#     posts = dbase.get_all_posts()
#     if request.method == "POST":
#         res1 = dbase.add_post(request.form['topic'], request.form['post'], request.form['url'], request.form['auth'], request.form['topic'])
#         if not (res1):
#             flash('Ошибка добавления статьи', category='error')
#         else:
#             flash('Информация добавлена успешно', category='success')
#             # return render_template('employee.html', empl=employee)
#     return render_template('add_post.html', posts=posts, title="Добавление информации о пoсте")
@app.route("/add_post", methods=["POST", "GET"])
def add_post():
    db = get_db()
    dbase = FDataBase(db)
    posts = dbase.get_all_posts()
    if request.method == "POST":
        id_a = dbase.get_id_author(request.form['auth'])
        id_t = dbase.get_id_topic(request.form['topic'])
        if not id_a:
            dbase.add_auth(request.form['auth'])
            id_a = dbase.get_id_author(request.form['auth'])
        if not id_t:
            dbase.add_topic(request.form['topic'])
            id_t = dbase.get_id_topic(request.form['topic'])
            #print(id_t)

        res1 = dbase.add_post(request.form['name'], request.form['post'], id_a, id_t)
        if not (res1):
            flash('Ошибка добавления статьи 95', category='error')
        else:
            flash('Информация добавлена успешно', category='success')
            # return render_template('employee.html', empl=employee)
    return render_template('add_post.html', posts=posts, title="Добавление информации о статье")



@app.route("/delete_post/<id_post>/<id_auth>", methods=["POST", "GET"])
def delete_post(id_post, id_auth):
    db = get_db()
    dbase = FDataBase(db)
    post = dbase.get_post_by_id(id_post)
    dbase.delete_post(id_post)
    # dbase.get_author_by_id(id)
    posts_author = dbase.get_posts_by_author(id_auth)

    if (not posts_author):
        dbase.delete_auth(id_auth)
    posts = dbase.get_all_posts()
    return render_template('posts.html', posts=posts)


@app.route("/change_post/<id_post>/<id_auth>", methods=["POST", "GET"])
def change_post(id_post, id_auth):

    db = get_db()
    dbase = FDataBase(db)
    post = dbase.get_post_by_id(id_post)
    author = dbase.get_author_by_id(id_auth)

    if request.method == "POST":
        res1 = dbase.update_post(id_post, request.form['title'], request.form['text'])
        post = dbase.get_post_by_id(id_post)

        if not (res1):
            flash('Ошибка добавления статьи', category='error')
        else:
            flash('Информация добавлена успешно', category='success')
            return render_template('post.html', post=post, author=author)
    return render_template('change_post.html', post=post, author=author)


@app.route("/show_authors/", methods=["POST", "GET"])
def show_authors():
    db = get_db()
    dbase = FDataBase(db)
    authors = dbase.get_all_authors()
    return render_template('authors.html', authors=authors)

@app.route("/show_authors_2/<id>", methods=["POST", "GET"])
def show_authors_2(id):
    db = get_db()
    dbase = FDataBase(db)
    authors = dbase.get_all_authors()
    posts_a = dbase.get_posts_by_author(id)
    if not posts_a:
        return render_template('authors.html', authors=authors)
    # for p in posts_a:
    #     print(p[5])
    return render_template('authors_2.html', authors=authors, posts=posts_a, a_id=posts_a[0][5])

@app.route("/show_topics/", methods=["POST", "GET"])
def show_topics():
    db = get_db()
    dbase = FDataBase(db)
    topics = dbase.get_all_topics()
    return render_template('topics.html', topics=topics)

@app.route("/show_topics_2/<id>", methods=["POST", "GET"])
def show_topics_2(id):
    #print("show_topics_2")
    db = get_db()
    dbase = FDataBase(db)
    topics = dbase.get_all_topics()
    posts_t = dbase.get_posts_by_topic(id)
    if not posts_t:
        return render_template('topics.html', topics=topics)
    # for p in posts_t:
    #     print(p[6])
    return render_template('topics_2.html', topics=topics, posts=posts_t, t_id=posts_t[0][6])

@app.route("/show_post/<id>", methods=["POST", "GET"])
def show_post(id):
    db = get_db()
    dbase = FDataBase(db)
    post = dbase.get_post_by_id(id)
    id_a = post[5]
    #print(id_a)
    author = dbase.get_author_by_id(id_a)
    return render_template('post.html', post=post, author=author)


# @app.route("/add_post", methods=["POST", "GET"])
# def addPost():
#     id_post = "0"
#     if request.method == "POST":
#     #     # user_id = current_user.get_id()
#     #     if len(request.form['name']) > 0 and len(request.form['post']) > 5:
#         res = dbase.addPost(request.form['name'], request.form['post'], request.form['auth'], request.form['topic'])
#     #проверка
#         res2 = dbase.addAuthor(request.form['auth'])
#     #         res2 = dbase.addTopic(request.form['topic'])
#     #         if not (res and res2):
#     #             flash('Ошибка добавления поста', category='error')
#     #         else:
#     #             flash('Пост добавлена успешно', category='success')
#     #             # id_post = dbase.getLastPostId(user_id)['id']
#     #     else:
#     #         flash('Ошибка добавления поста', category='error')
#
#     return render_template('add_post.html', menu=dbase.getMenu(), title="Добавление статьи", id_post=id_post)
#
# @app.route("/showPost/<id>")
# #@login_required
# def showPost(id):
#     #print("showPost")
#     title, post = dbase.getPost_by_id(id)
#     #print(id)
#     if not title:
#         abort(404)
#     text = post.split('\n')
#     #print(text)
#     count = dbase.getCountFiles(id)['COUNT(*)']
#     #print("кол-во фотографий")
#     #print(count)
#     #print(dbase.getFirstFileId(id)['id_file'])
#     return render_template('post.html', menu=dbase.getMenu(), title=title, post=text, post_id=id, count=count, file_id=dbase.getFirstFileId(id)['id_file'])
#
# # Пользователь (писатель постов)
# @app.route("/writer/<alias>")
# # @login_required
# def showWriters(alias):
#     id, name = dbase.getWriter(alias)
#     id_user = 0
#     if current_user.is_authenticated:
#         id_user = current_user.get_is_admin()
#         #print(id_user)
#
#     return render_template('writer.html', menu=dbase.getMenu(), title=name, id=id, posts=dbase.getPostsAnonce1(id), w_id=alias, id_user=id_user)
#
# @app.route('/deleteWriter/<alias>')
# def deleteWriter(alias):
#     dbase.deleteWritersPost(alias)
#     dbase.deleteWriter(alias)
#     return redirect(url_for('index'))
#
# @app.route('/deletePost/<alias>/<id_post>')
# def deletePost(alias, id_post):
#     dbase.deleteWriterPost(id_post)
#     dbase.deletePostFiles(id_post)
#     #dbase.deleteWriter(alias)
#     return redirect(url_for('showWriters', alias=alias))
#
# # Авторизация
# # @app.route("/login", methods=["POST", "GET"])
# # def login():
# #     if current_user.is_authenticated:
# #         return redirect(url_for('profile'))
# #
# #     if request.method == "POST":
# #         user = dbase.getUserByEmail(request.form['email'])
# #         if user and check_password_hash(user['psw'], request.form['psw']):
# #             userlogin = UserLogin().create(user)
# #             rm = True if request.form.get('remainme') else False
# #             login_user(userlogin, remember=rm)
# #             return redirect(request.args.get("next") or url_for("profile"))
# #
# #         flash("Неверная пара логин/пароль", "error")
# #
# #     return render_template("login.html", menu=dbase.getMenu(), title="Авторизация")
#
# # # Регистрация
# # @app.route("/register", methods=["POST", "GET"])
# # def register():
# #     if request.method == "POST":
# #         if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
# #             and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
# #             hash = generate_password_hash(request.form['psw'])
# #             res = dbase.addUser(request.form['name'], request.form['email'], hash, 0)
# #             if res:
# #                 flash("Вы успешно зарегистрированы", "success")
# #                 return redirect(url_for('login'))
# #             else:
# #                 flash("Ошибка при добавлении в БД", "error")
# #         else:
# #             flash("Уже есть пользователь с таким email", "error")
# #
# #     return render_template("register.html", menu=dbase.getMenu(), title="Регистрация")
# #
# # @app.route('/logout')
# # #@login_required
# # def logout():
# #     logout_user()
# #     flash("Вы вышли из аккаунта", "success")
# #     return redirect(url_for('login'))
#
# # Личный кабинет
# @app.route('/profile')
# #@login_required
# def profile():
#     #print('is_admin')
#     #print(current_user.get_is_admin())
#     id_user = 0
#     if current_user.is_authenticated:
#         id_user = current_user.get_is_admin()
#         #print(id_user)
#     return render_template("profile.html", menu=dbase.getMenu(), title="Личный кабинет", posts=dbase.getPostsAnonce1(current_user.get_id()), id_user=id_user)
#
# # # Аватарка авторизированного пользователя
# # @app.route('/userava/<user_id>', methods=["POST", "GET"])
# # # @login_required
# # def userava(user_id):
# #     user = UserLogin().fromDB(user_id, dbase)
# #     img = user.getAvatar(app)
# #     if not img:
# #         return ""
# #
# #     h = make_response(img)
# #     h.headers['Content-Type'] = 'image/png'
# #     return h
#
# # @app.route('/userpost/<user_id>', methods=["POST", "GET"])
# # @login_required
# # def userpost(user_id):
#     # user = UserLogin().fromDB(user_id, dbase)
#     # img = user.getAvatar(app)
#     # if not img:
#     #     return ""
#
#     # h = make_response(img)
#     # h.headers['Content-Type'] = 'image/png'
#     # return h
# #
# # @app.route('/newName/<user_id>', methods=["POST", "GET"])
# # # @login_required
# # def newName(user_id):
# #     newName = request.form['name']
# #     dbase.changeUsersName(user_id,newName)
# #     return  redirect(url_for('profile'))
# # @app.route('/newPsw/<user_id>', methods=["POST", "GET"])
# # # @login_required
# # def newPsw(user_id):
# #     newPsw = request.form['npsw']
# #     dbase.changeUsersPsw(user_id,generate_password_hash( newPsw))
# #     return  redirect(url_for('profile'))
#
# #
# # # Загрузить аватарку
# # @app.route('/upload', methods=["POST", "GET"])
# # #@login_required
# # def upload():
# #     if request.method == 'POST':
# #         file = request.files['file']
# #         #print(file)
# #         if file:
# #             try:
# #                 img = file.read()
# #                 res = dbase.updateUserAvatar(img, current_user.get_id())
# #                 if not res:
# #                     flash("Ошибка обновления аватара 1", "error")
# #                 flash("Аватар обновлен", "success")
# #             except FileNotFoundError as e:
# #                 flash("Ошибка чтения файла", "error")
# #         else:
# #             flash("Ошибка обновления аватара", "error")
# #
# #     return redirect(url_for('profile'))
#
# @app.route('/upload_post/<id_post>', methods=["POST", "GET"])
# #@login_required
# def upload_post(id_post):
#     file = request.files.getlist('file')
#     #print(file)
#     if file:
#         for f in file:
#             try:
#                 img = f.read()
#                 res = dbase.addPFile(img, id_post)
#                 if not res:
#                     flash("Ошибка добавления файла", "error")
#             except FileNotFoundError as e:
#                 flash("Ошибка чтения файла", "error")
#     else:
#         flash("Ошибка добавления файла", "error")
#
#     return redirect(url_for('addPost'))
#
# @app.route('/posts_file/<count>', methods=["POST", "GET"])
# # @login_required
# def posts_file( count):
#     #print(count)
#     img = dbase.getFile(count)
#     if not img:
#         return ""
#     #print("тест")
#     #print(img)
#     return img['p_file']

if __name__ == "__main__":
    app.run(debug=True)
