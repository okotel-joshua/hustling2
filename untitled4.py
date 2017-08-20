from flask import Flask, render_template, request, redirect, jsonify, url_for, session, flash, abort, g
from sqlalchemy import create_engine,desc
from sqlalchemy.orm import sessionmaker
from data import Base, Users, Events, User
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm.exc import NoResultFound
from flask_wtf import Form
from wtforms import SubmitField, StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length, Regexp, EqualTo
from flask_wtf import FlaskForm
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from flask_mail import Mail, Message
import cloudinary.api

app = Flask(__name__)
mail = Mail(app)


app.config['SECRET_KEY'] = 'deVElpPasswordkey1!'
engine = create_engine('sqlite:///handler.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# user = User()

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'




# log in page
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usernam = request.form['username']
        passw = request.form['password']
        try:
            usernw = session.query(Users).filter_by(email=usernam).first()
            if check_password_hash(usernw.password, request.form['password']):
                login_user(usernw)
                flash('Logged in successfully')
                return redirect(url_for('home'))
            else:
                flash('Invalid Credentials')
                return redirect(url_for('login'))
        except NoResultFound:
            flash('Invalid Credentials')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/myEvents/')
@login_required
def myEvents():
    events = session.query(Events).all()
    return render_template('myEvents.html', events=events)


@app.route('/search')
@login_required
def search():
    if request.method=='POST':
        sia = request.form['search']
        saa = session.query(Events).filter_by(name=sia).all()
        if saa:
            return render_template('result.html',events=saa)
        return redirect(url_for('event'))
    return redirect(url_for('event'))

@app.route('/result')
@login_required
def result():
    return render_template('result.html')



# editing event
@login_required
@app.route('/event/<int:event_id>/', methods=['GET', 'POST'])
def edit(event_id):
    enow = session.query(Events).filter_by(id=event_id).one()
    if request.method == 'POST':
        if request.form['name']:
            enow.name = request.form['name']
        if request.form['description']:
            enow.description = request.form['description']
        if request.form['fee']:
            enow.fee = request.form['fee']
        if request.form['date']:
            enow.date = request.form['date']
        if request.form['time']:
            enow.time = request.form['time']
        if request.form['organisers']:
            enow.organisers = request.form['organisers']
        if request.form['category']:
            enow.category = request.form['category']
        session.add(enow)
        session.commit()
        return redirect(url_for('event'))

    else:
        return render_template('editevent.html', enow=enow, event_id=event_id)


# deleting an event
@login_required
@app.route('/delete/<int:event_id>/', methods=['GET', 'POST'])
def delete(event_id):
    enow = session.query(Events).filter_by(id=event_id).one()
    if request.method == 'POST':
        session.delete(enow)
        session.commit()
        return redirect(url_for('event'))
    return render_template('deleteEvent.html', enow=enow)


# logging out
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged Out')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.debug = True
    app.run()
