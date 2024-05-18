import os
import requests
import datetime
import json
import hashlib

from flask import render_template, redirect, request, send_file, session, url_for, send_from_directory
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, logout_user, current_user
from flask import Response

from init_app import *
from forms import *
from user import *
from parse import *


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/uploads/<filename>')
@login_required
async def upload_filename(filename):
    path = f'temp/{filename}'

    if not os.path.exists('temp'):
        os.mkdir('temp')
    if not os.path.exists(path):
        with open(path, 'wb') as f:
            f.write(Img.query.filter_by(filename=filename).first().image)

    response = send_file(path, max_age=3600)

    os.remove(path)

    return response


@app.route('/add_card', methods=['POST', 'GET'])
@login_required
async def add_card():
    form = AddCardForm()

    if form.validate_on_submit():
        title = form.title.data
        link = form.link.data
        description = form.description.data
        preview = form.preview.data.read()
        img_name = hashlib.md5(preview).hexdigest()
        card_id = current_user.next_card_index

        cards = json.loads(current_user.cards)

        new_card = Card(
            card_id=card_id,
            owner=current_user.login,
            title=title,
            link=link,
            description=description,
            preview_name=img_name
        )
        db.session.add(new_card)

        cards.append(card_id)
        current_user.cards = json.dumps(cards)
        current_user.next_card_index += 1

        new_img = Img(filename=img_name, image=preview)
        db.session.add(new_img)

        db.session.commit()

        return redirect('/')

    form.title.data = ''
    form.link.data = ''
    form.description.data = ''

    return render_template('add_card.html', form=form)


@app.route('/')
@login_required
async def home():
    print(current_user.profile_pic_name)
    return render_template('home.html', user=current_user,
                           cards=[Card.query.filter_by(
                               card_id=i, owner=current_user.login).first() for i
                                  in json.loads(current_user.cards)])


@app.route('/register', methods=['GET', 'POST'])
async def register():
    form = RegisterForm()

    if form.validate_on_submit():
        password_hash = bcrypt.generate_password_hash(form.password.data)

        image = form.profile_pic.data.read()
        image_name = hashlib.md5(image).hexdigest()

        if not image:
            print('no image')
            image_name = ''
        else:
            new_img = Img(filename=image_name, image=image)
            db.session.add(new_img)

        cards = json.dumps([])

        new_user = User(login=form.login.data, username=form.username.data,
                        password_hash=password_hash, email=form.email.data,
                        profile_pic_name=image_name, next_card_index=0, cards=cards)


        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)

        if 'next' in request.args.keys() and request.args['next'] != '/logout':
            response = redirect(request.args['next'])
        else:
            response = redirect('/')

        cookie_expire_time = datetime.date.today() + datetime.timedelta(days=30)

        response.set_cookie('login', new_user.login, expires=cookie_expire_time)
        response.set_cookie('password_hash', str(new_user.password_hash), expires=cookie_expire_time)

        return response

    return render_template('register.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
async def login():
    if all(key in request.cookies.keys() for key in ('login', 'password_hash')):
        user = User.query.filter_by(login=request.cookies['login']).first()
        if user and str(user.password_hash) == request.cookies['password_hash']:
            login_user(user)
            return redirect('/')

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)

            if 'next' in request.args.keys() and request.args['next'] != '/logout':
                response = redirect(request.args['next'])
            else:
                response = redirect('/')

            cookie_expire_time = datetime.date.today() + datetime.timedelta(days=30)

            response.set_cookie('login', user.login, expires=cookie_expire_time)
            response.set_cookie('password_hash', str(user.password_hash), expires=cookie_expire_time)

            return response

    return render_template('login.html', form=form)


@app.route('/logout', methods=['POST', 'GET'])
@login_required
async def logout():
    logout_user()

    response = redirect(url_for('login'))
    response.delete_cookie(key='login')
    response.delete_cookie(key='password_hash')

    return response


@app.route('/save_data', methods=['POST', 'GET'])
async def save_data():
    if request.method == 'POST':
        login = request.form['username']
        username = request.form['username']
        password = request.form['password']
        password_hash = bcrypt.generate_password_hash(password)
        email = request.form['email']
        profile_pic = request.files['profile_pic'].read()

        if User.query.get(login):
            session['formdata'] = request.form
            return redirect(url_for('register', **request.args))

        new_user = User(login=login,
                        username=username,
                        password_hash=password_hash,
                        email=email,
                        profile_pic=profile_pic
                        )
        image = request.files['image']
        filename = secure_filename('img.png')
        if not os.path.isdir(app.config['UPLOAD_FOLDER']):
            os.mkdir(app.config['UPLOAD_FOLDER'])
        image.save(app.config['UPLOAD_FOLDER'] + '/' + filename)
        try:
            db.session.add(new_user)
            db.session.commit()

            resp = redirect('/')
            resp.set_cookie('login', request.form["username"])
            resp.set_cookie('password', request.form["password"])

            return resp
        except:
            return f'There was an issue'


@app.route('/update/<id>', methods=['GET'])
@login_required
async def update(id):
    card = Card.filter_by(card_id=id, owner=current_user).first()
    url = card.link
    url_hash = card.url_hash

    actual_hash = get_page_hash(url)

    resp = {
        'updated': actual_hash != url_hash,
        'hash': actual_hash
    }
    resp_json = json.dumps(resp)

    return Response(response=resp_json, status=200)


@app.route('/goto/<id>', methods=['GET'])
@login_required
async def goto(id):
    card = Card.filter_by(card_id=id, owner=current_user).first()
    url = card.link

    actual_hash = get_page_hash(url)
    card.url_hash = actual_hash
    db.session.commit()

    if actual_hash:
        return redirect(url)

    return redirect('/')


@app.route('/edit_card/<id>', methods=['GET', 'POST'])
@login_required
async def edit_card(id):
    card = Card.filter_by(card_id=id, owner=current_user).first()
    form = EditCardForm()
    print(form.title.data)

    print(request.method)

    if request.method == 'POST':
        if form.validate_on_submit():
            card.title = form.title.data
            card.link = form.link.data
            card.description = form.description.data
            preview = form.preview.data.read()
            card.preview_name = hashlib.md5(preview).hexdigest()

            new_img = Img(filename=card.preview_name, image=preview)
            db.session.add(new_img)

            db.session.commit()

            return redirect('/')
        
        return redirect(f'/edit_card/{id}')

    form.title.data = card.title
    form.link.data = card.link
    form.description.data = card.description

    return render_template('edit_card.html', form=form, card_id=id)


@app.route('/delete_card/<id>', methods=['DELETE'])
@login_required
async def delete_card(id):
    cards = json.loads(current_user.cards)
    if int(id) not in cards:
        return Response(status=404)

    db.session.delete(Card.filter_by(card_id=id, owner=current_user).first())
    cards.remove(int(id))
    current_user.cards = json.dumps(cards)

    db.session.commit()

    return Response(status=200, response=json.dumps('success'))

if __name__ == '__main__':
    app.run(debug=True)
