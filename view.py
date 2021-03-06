 #encoding=utf-8

from flask import render_template, flash, redirect, session, url_for, request, make_response, g
from StringIO import StringIO
from html_convert import html2text
from config import POST_PRE_PAGE
from data_wrappers import DataWrappers
from blogapp import app
# from admin import admin
import os
import json
import re



date = DataWrappers()

def _html2text(html):
    sio = StringIO()
    html2text.html2text_file(html, sio.write)
    text = sio.getvalue()
    sio.close()
    return text
app.jinja_env.filters['html2text'] = _html2text


def global_map():
    tags = date.get_all_tags()
    links = date.get_all_links()
    map = {
         'tags': tags,
         'links': links,
    }
    return map


@app.before_request
def befor_request():
    g.user = date.get_first_user()


# @app.teardown_request
# def teardown_request():
# #   将mysql链接还给连接池，避免SAE的mysql gone away问题
#     db.session.remove()


@app.route('/')
@app.route('/blog')
@app.route('/blog/<int:page>')
def show_blog(page=1):
    if page < 1:
        page = 1
    p = date.get_entries_by_page(page=page, par_page=POST_PRE_PAGE)
    entries = p.items
    #页数标签
    if not p.total:
        pagination = [0]
    elif p.total % POST_PRE_PAGE != 0:
        pagination = range(1, p.total/POST_PRE_PAGE + 2)
    else:
        pagination = range(1, p.total/POST_PRE_PAGE + 1)

    return render_template('/blog/show_blog.html', entries=entries,
                           p=p, page=page, pagination=pagination,
                            **global_map())


@app.route('/category')
def show_categories():
    categories = date.get_all_categories()
    counts = date.get_entry_by_category(categories=categories)
    return render_template('blog/show_categories.html', categories=categories,
                           counts=counts, **global_map())


@app.route('/category/<int:category_id>')
def show_category(category_id):
    category = date.get_category_by_id(category_id)
    return render_template('/blog/show_category.html', category=category,
                           **global_map())

@app.route('/tag/<int:tag_id>')
def show_tag(tag_id):
    tag = date.get_tag_by_id(tag_id)

    return render_template('/blog/show_tag.html', tag=tag,
                           **global_map())


@app.route('/entry/<int:entry_id>')
def show_entry(entry_id):
    entry = date.get_entry_by_id(entry_id)
    date.increase_view_count(entry, 1)
    return render_template('/blog/show_entry.html', entry=entry,
                            **global_map())

@app.route('/entry/<int:entry_id>/prev')
def prev_entry(entry_id):
    entry = date.get_prev_entry(entry_id)
    if entry is None:
        return redirect(url_for('show_entry', entry_id=entry_id))
    return redirect(url_for('show_entry', entry_id=entry.id))


@app.route('/entry/<int:entry_id>/next')
def next_entry(entry_id):
    entry = date.get_next_entry(entry_id)
    if entry is None:
        return redirect(url_for('show_entry', entry_id=entry_id))
    return redirect(url_for('show_entry', entry_id=entry.id))

@app.route('/comment')
def show_comment():

    return render_template('blog/show_comment.html',
                           **global_map())

@app.route('/about')
def show_about():

    return render_template('blog/show_about.html',
                           **global_map())


@app.route('/login')
def login():
    return url_for('admin.index')



#表单视图
#@app.route('/login', methods = ['GET', 'POST'])
#@oid.loginhandler
#def login():
#    if g.user is not None and g.user.is_authenticated():
#        return redirect(url_for('blog'))
#    form = LoginForm()
#    if form.validate_on_submit():
 #       session['remeber_me'] = form.remember_me.data
#        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
#
#    return render_template('/blog/login.html', title='Sign In',
#                           form=form, providers=app.config['OPENID_PROVIDERS'])
#
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('show_blog'))
#
#
#@lm.user_loader
#def load_user(id):
#    return User.query.get(int(id))
#
#@oid.after_login
#def after_login(resp):
#    if resp.email is None or resp.email == "":
##        flash('Invalid login. Please try again!')
#        return redirect(url_for('login'))
##   if user is None:
 #       nickname = resp.nickname
 #       if nickname is None or nickname == "":
  #          nickname = resp.email.split('@')[0]
  #      user = User(nickname=nickname, email=resp.email, role=ROLE_USER)
  #      db.session.add(user)
  #      db.session.commit()
 #   remember_me = False
## #      session.pop('remember_me', None)
 #   login_user(user, remember=remember_me)
 #   return redirect(request.args.get('next') or url_for('show_blog'))
#用户信息
#@app.route('/user/<nickname>')
#@login_required
#def user(nickname):
#    user = User.query.filter_by(nickname=nickname).first()
 #   if user == None:
 #       flash('user'+nickname+'not found')
 #       return redirect(url_for('show_blog'))
 #   entries = [
 #       {'author': user, 'content': 'Test post #1'},
 ##   ]
  #  return render_template('/blog/user.html', user=user, entries=entries)
#
# @app.route('/edit', methods=['GET', 'POST'])
# @login_required
# def edit():
#     form = EditForm(g.user.nickname)
#     if form.validate_on_submit():
#         g.user.nickname = form.nickname.data
#         g.user.about_me = form.about_me.data
#         db.session.add(g.user)
#         db.session.commit()
#         flash('Your changes have been saved.')
#         return redirect(url_for('edit'))
#     else:
#         form.nickname.data = g.user.nickname
#         form.about_me.data = g.user.about_me
#     return render_template('/blog/edit.html', form=form)


# 错误处理
@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


# 管理视图
@app.route('/login')
def admin_index():
    return render_template('index.html')


