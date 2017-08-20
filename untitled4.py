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

CLOUDINARY = {
    'cloud_name': 'dkfj0v8ow',
    'api_key': '273221192322658',
    'api_secret': '-_qA6YexmfCRJnpcA_DiFJ_v2wY',
}

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='abrahamkakooza@gmail.com',
    MAIL_PASSWORD='a24.....',
    MAIL_DEFAULT_SENDER='abrahamkakooza@gmail.com',
)

cloudinary.config(cloud_name='dkfj0v8ow', api_key='273221192322658', api_secret='-_qA6YexmfCRJnpcA_DiFJ_v2wY')

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


class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    name = StringField('name', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80),
                                                     EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('confirmpassword', validators=[InputRequired()])


@login_manager.user_loader
def load_user(user_id):
    return session.query(Users).get(int(user_id))


@app.route('/')
def index():
    events = session.query(Events).all()
    return render_template('index.html', events=events)


@app.route('/home')
@login_required
def home():
    events = session.query(Events).all()
    return render_template('home.html', events=events)


@app.route('/event')
@login_required
def event():
    events = session.query(Events).order_by(desc(Events.id))
    return render_template('event.html', events=events)

@app.route('/dra')
def draft():
    return render_template('draft.html')


@app.route('/send-mail/')
def send_mail():
    msg = Message(subject='Registration',
                  body='Thanks for registering with Kennedy Family Recipes!',
                  recipients=['patkennedy79@gmail.com'])
    mail.send(msg)
    return 'Mail sent'


# @app.route('/home', methods=['GET','POST'])
# @login_required
# def home():
#     events = session.query(Events).all()
#     return render_template('about.html', events=events)


@app.route('/image', methods=['GET', 'POST'])
def upload_file():
    upload_result = None
    thumbnail_url1 = None
    thumbnail_url2 = None
    if request.method == 'POST':
        file_to_upload = request.files['file']
        if file_to_upload:
            upload_result = upload(file_to_upload)
            thumbnail_url1, options = cloudinary_url(upload_result['public_id'], format="jpg", crop="fill", width=100,
                                                     height=100)
            thumbnail_url2, options = cloudinary_url(upload_result['public_id'], format="jpg", crop="fill", width=200,
                                                     height=100, radius=20, effect="sepia")
    return render_template('upload_form.html', upload_result=upload_result, thumbnail_url1=thumbnail_url1,
                           thumbnail_url2=thumbnail_url2)


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        hashed_password = generate_password_hash(request.form['password'], method='sha256')
        if session.query(Users).filter_by(email=request.form['email']).first():
            flash('Email already exists')
            return redirect(url_for('signup'))
        if session.query(Users).filter_by(name=request.form['name']).first():
            flash('Username already exists.')
            return redirect(url_for('signup'))
        if request.form['password'] == request.form['confirmpassword']:
            user = Users(name=request.form['name'], password=hashed_password, email=request.form['email'])
            session.add(user)
            session.commit()
            flash('User successfully registered')
            return redirect(url_for('login'))
        flash('Passwords do not match')
        return redirect(url_for('signup'))
    return render_template('signup.html')


@app.route('/create/', methods=['GET', 'POST'])
@login_required
def createEvent():
    if request.method == 'POST':
        time = str(request.form['time']).split(':')
        time = datetime.time(int(time[0]), int(time[1]))
        date = str(request.form['date']).split('-')
        date = datetime.date(int(date[0]), int(date[1]), int(date[2]))
        upload_result = None
        thumbnail_url1 = None
        thumbnail_url2 = None
        if request.files['file']:
            file_to_upload = request.files['file']
            upload_result = upload(file_to_upload)
            thumbnail_url1, options = cloudinary_url(upload_result['public_id'], format="jpg", crop="fill", width=100,
                                                     height=100)
        events = Events(name=request.form['name'], fee=request.form['fee'], date=date, time=time,
                        location=request.form['location'],
                        organisers=request.form['organisers'], description=request.form['description'],
                        category=request.form['category'], privacy=request.form['privacy'], pictures=thumbnail_url1)
        session.add(events)
        session.commit()
        flash('New Event Created')
        return redirect(url_for('event'))
    return render_template('createEvent.html')


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
