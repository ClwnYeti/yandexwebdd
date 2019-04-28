from flask import Flask, render_template, redirect, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField, SelectField, FileField
from flask_wtf.file import FileRequired, FileAllowed
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea
from werkzeug.utils import secure_filename
from flask import make_response


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['Encoding'] = 'UTF-8'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


class YandexLyceumStudent(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password = db.Column(db.String(80), unique=False, nullable=False)
	name = db.Column(db.String(80), unique=False, nullable=False)
	surname = db.Column(db.String(80), unique=False, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	im = db.Column(db.String(256), unique=False, nullable=False)
	teacherid = db.Column(db.Integer,
	                      db.ForeignKey('yandex_lyceum_teacher.id'),
	                      nullable=False)
	teacher = db.relationship('YandexLyceumTeacher',
	                          backref=db.backref('YandexLyceumStudent',
	                                             lazy=True))
	year = db.Column(db.Integer, unique=False, nullable=False)
	
	def __repr__(self):
		return '<YandexLyceumStudent {} {} {} {}>'.format(
			self.id, self.username, self.name, self.surname)


class YandexLyceumTeacher(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password = db.Column(db.String(80), unique=True, nullable=False)
	name = db.Column(db.String(80), unique=False, nullable=False)
	surname = db.Column(db.String(80), unique=False, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	
	def __repr__(self):
		return '<YandexLyceumTeacher {} {} {} {}>'.format(
			self.id, self.username, self.name, self.surname)


class Admin(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password = db.Column(db.String(80), unique=True, nullable=False)
	
	def __repr__(self):
		return '<Admin {} {}>'.format(
			self.id, self.username)
	



class SolutionAttempt(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	task = db.Column(db.String(80), unique=False, nullable=False)
	code = db.Column(db.String(1000), unique=False, nullable=False)
	status = db.Column(db.String(50), unique=False, nullable=False)
	student_id = db.Column(db.Integer,
	                       db.ForeignKey('yandex_lyceum_student.id'),
	                       nullable=False)
	student = db.relationship('YandexLyceumStudent',
	                          backref=db.backref('SolutionAttempts',
	                                             lazy=True))
	
	def __repr__(self):
		return '<SolutionAttemp {} {} {}>'.format(
			self.id, self.task, self.status)
	
	
class MessageForU(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	message = db.Column(db.String(1000), unique=False, nullable=False)
	student_id = db.Column(db.Integer,
		                   db.ForeignKey('yandex_lyceum_student.id'),
		                   nullable=False)
	student = db.relationship('YandexLyceumStudent',
		                          backref=db.backref('MessageForU',
		                                             lazy=True))
	teacher_id = db.Column(db.Integer, nullable=False)
	who = db.Column(db.String(50), unique=False, nullable=False)
	
	def __repr__(self):
		return '<MessageForU {} {} {}>'.format(
			self.id, self.student.username, self.student_id)


class MessageForTask(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	message = db.Column(db.String(1000), unique=False, nullable=False)
	student_id = db.Column(db.Integer,
	                       db.ForeignKey('yandex_lyceum_student.id'),
	                       nullable=False)
	task = db.relationship('SolutionAttempt',
	                          backref=db.backref('MessageForTask',
	                                             lazy=True))
	task_id = db.Column(db.Integer,
	                       db.ForeignKey('solution_attempt.id'),
	                       nullable=False)
	teacher_id = db.Column(db.Integer, nullable=False)
	who = db.Column(db.String(50), unique=False, nullable=False)
	
	def __repr__(self):
		return '<MessageForTask {} {} {}>'.format(
			self.id, self.task.task, self.task_id)
	

db.create_all()
db.session.commit()
if Admin.query.all() == []:
	admin = Admin(username='admin', password='admin')
	db.session.add(admin)
if YandexLyceumTeacher.query.all() == []:
	admint = YandexLyceumTeacher(username='admin', password='admin',
	                             name='admin', surname='admin', email='admin')
	db.session.add(admint)
db.session.commit()


class Change(FlaskForm):
	code = TextAreaField('Код', validators=[DataRequired()], render_kw={"rows": 50, "cols": 120})
	submit = SubmitField('Подтвердить')
	
	
class Task(FlaskForm):
	code = SelectField('Решение', coerce=int, choices=[(1, 'Зачтено'), (2, 'На доработку')])
	submit = SubmitField('Подтвердить')
	
	
class LoginForm(FlaskForm):
	username = StringField('Логин', validators=[DataRequired()])
	password = PasswordField('Пароль', validators=[DataRequired()])
	remember_me = BooleanField('Запомнить меня')
	submit = SubmitField('Войти')


class RegisterFormSt(FlaskForm):
	username = StringField('Логин', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired()])
	name = StringField('Имя', validators=[DataRequired()])
	surname = StringField('Фамилия', validators=[DataRequired()])
	a = YandexLyceumTeacher.query.all()
	a = [(i.id, i.name + ' ' + i.surname) for i in a]
	teacher = SelectField('Учитель', coerce=int, choices=a)
	year = SelectField('Год', coerce=int, choices=[(1, 'Первый'), (2, 'Второй')])
	password = PasswordField('Пароль', validators=[DataRequired()])
	submit = SubmitField('Зарегистрироваться')


class RegisterFormTe(FlaskForm):
	username = StringField('Логин', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired()])
	name = StringField('Имя', validators=[DataRequired()])
	surname = StringField('Фамилия', validators=[DataRequired()])
	password = PasswordField('Пароль', validators=[DataRequired()])
	submit = SubmitField('Зарегистрироваться')


class AddTForm(FlaskForm):
	title = StringField('Задание', validators=[DataRequired()])
	content = TextAreaField('Код', validators=[DataRequired()], render_kw={"rows": 50, "cols": 120})
	submit = SubmitField('Добавить')
	
	
class Message(FlaskForm):
	message = TextAreaField('Отправить сообщение', validators=[DataRequired()], render_kw={"rows": 5, "cols": 100})
	submit1 = SubmitField('Отправить')
	
	
class AddFForm(FlaskForm):
	title = StringField('Задание', validators=[DataRequired()])
	content = FileField('Файл с задачей', validators=[FileRequired()])
	submit = SubmitField('Добавить')
	
	
class AddPForm(FlaskForm):
	content = FileField('Картинка', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
	submit = SubmitField('Выбрать')


@app.errorhandler(404)
def not_found(error):
	return render_template('404.html')


@app.route('/')
@app.route('/main', methods=['GET', 'POST'])
def main():
	if 'class' in session:
		return redirect('/' + session['class'] + '/' + str(session['user_id']))
	return render_template('main.html', title='Main')


@app.route('/login/<classer>', methods=['GET', 'POST'])
def login(classer):
	if classer == 'student':
		form = LoginForm()
		if form.validate_on_submit():
			user_name = form.username.data
			password = form.password.data
			a = YandexLyceumStudent.query.filter_by(username=user_name, password=password).all()
			if a != []:
				a = a[0]
				session['username'] = user_name
				session['class'] = 'YandexLyceumStudent'
				session['user_id'] = a.id
				return redirect("/")
			else:
				a = YandexLyceumStudent.query.filter_by(username=user_name).all()
				if a == []:
					form.username.errors = list(form.username.errors)
					form.username.errors.append('Пользователь не существует')
				else:
					form.password.errors = list(form.password.errors)
					form.password.errors.append('Пароль не соответствует')
		return render_template('login.html', title='Авторизация', form=form, classer='student')
	elif classer == 'admin':
		form = LoginForm()
		if form.validate_on_submit():
			user_name = form.username.data
			password = form.password.data
			a = Admin.query.filter_by(username=user_name, password=password).all()
			if a != []:
				a = a[0]
				session['username'] = user_name
				session['class'] = 'Admin'
				session['user_id'] = a.id
				return redirect("/admin")
			else:
				a = Admin.query.filter_by(username=user_name).all()
				if a == []:
					form.username.errors = list(form.username.errors)
					form.username.errors.append('Пользователь не существует')
				else:
					form.password.errors = list(form.password.errors)
					form.password.errors.append('Пароль не соответствует')
		return render_template('loginadmin.html', title='Авторизация', form=form)
	elif classer == 'teacher':
			form = LoginForm()
			if form.validate_on_submit():
				user_name = form.username.data
				password = form.password.data
				a = YandexLyceumTeacher.query.filter_by(username=user_name, password=password).all()
				if a != []:
					a = a[0]
					session['username'] = user_name
					session['class'] = 'YandexLyceumTeacher'
					session['user_id'] = a.id
					return redirect("/")
				else:
					a = YandexLyceumTeacher.query.filter_by(username=user_name).all()
					if a == []:
						form.username.errors = list(form.username.errors)
						form.username.errors.append('Пользователь не существует')
					else:
						form.password.errors = list(form.password.errors)
						form.password.errors.append('Пароль не соответствует')
			return render_template('login.html', title='Авторизация', form=form, classer='teacher')


@app.route('/register/student', methods=['GET', 'POST'])
def reg():
	a = YandexLyceumTeacher.query.all()
	a = [(i.id, i.name + ' ' + i.surname) for i in a]
	RegisterFormSt.teacher = SelectField('Учитель', coerce=int, choices=a)
	form = RegisterFormSt()
	if form.validate_on_submit():
		username = form.username.data
		password = form.password.data
		name = form.name.data[0].upper() + form.name.data[1:].lower()
		surname = form.surname.data[0].upper() + form.surname.data[1:].lower()
		email = form.email.data
		teacher = YandexLyceumTeacher.query.filter_by(id=form.teacher.data).first()
		year = form.year.data
		user = YandexLyceumStudent.query.filter_by(username=username).all()
		if email.find('@') == -1 or email.find('@') == 0 or  email.find('@') == len(email) - 1\
			or email.find('.') == -1 or email.find('.') == 0 or  email.find('.') == len(email) - 1 \
			or email.find('.') - email.find('@') < 2:
			form.username.errors = list(form.username.errors)
			form.email.errors.append('Email некорректен')
			return render_template('reg.html', title='Авторизация', form=form)
		if user != []:
			form.username.errors = list(form.username.errors)
			form.username.errors.append('Логин занят')
			return render_template('reg.html', title='Авторизация', form=form)
		user = YandexLyceumStudent.query.filter_by(email=email).all()
		if user != []:
			form.username.errors = list(form.username.errors)
			form.email.errors.append('Email занят')
			return render_template('reg.html', title='Авторизация', form=form)
		student = YandexLyceumStudent(username=username,
									  email=email,
									  name=name,
									  surname=surname,
									  password=password,
									  year=year,
		                              im='')
		teacher.YandexLyceumStudent.append(student)
		db.session.commit()
		session['username'] = username
		session['class'] = 'YandexLyceumStudent'
		session['user_id'] = student.id
		return redirect("/")
	return render_template('reg.html', title='Авторизация', form=form, classer='student')


@app.route('/register/teacher', methods=['GET', 'POST'])
def re():
	form = RegisterFormTe()
	if form.validate_on_submit():
		username = form.username.data
		password = form.password.data
		name = form.name.data[0].upper() + form.name.data[1:].lower()
		surname = form.surname.data[0].upper() + form.surname.data[1:].lower()
		email = form.email.data
		user = YandexLyceumTeacher.query.filter_by(username=username).all()
		if email.find('@') == -1 or email.find('@') == 0 or  email.find('@') == len(email) - 1\
			or email.find('.') == -1 or email.find('.') == 0 or  email.find('.') == len(email) - 1 \
			or email.find('.') - email.find('@') < 2:
			form.username.errors = list(form.username.errors)
			form.email.errors.append('Email некорректен')
			return render_template('regteacher.html', title='Авторизация', form=form)
		if user != []:
			form.username.errors = list(form.username.errors)
			form.username.errors.append('Логин занят')
			return render_template('regteacher.html', title='Авторизация', form=form)
		if user != []:
			form.username.errors = list(form.username.errors)
			form.email.errors.append('Email занят')
			return render_template('regteacher.html', title='Авторизация', form=form)
		student = YandexLyceumTeacher(username=username,
									  email=email,
									  name=name,
									  surname=surname,
									  password=password,
		                              )
		db.session.add(student)
		db.session.commit()
		session['username'] = username
		session['class'] = 'YandexLyceumTeacher'
		session['user_id'] = student.id
		return redirect("/")
	return render_template('regteacher.html', title='Авторизация', form=form, classer='teacher')


@app.route('/admin', methods=['GET', 'POST'])
def adm():
	if 'username' not in session:
		return redirect('/')
	if session['class'] != 'Admin' or session['user_id'] != 1:
		return redirect('/')
	a = YandexLyceumTeacher.query.all()
	a = [(YandexLyceumStudent.query.filter_by(teacherid=i.id).all(), i) for i in a]
	x = []
	for i in a:
		k = len(i[0])
		p = 0
		n = 0
		for j in i[0]:
			v = SolutionAttempt.query.filter_by(student_id=j.id).all()
			for l in v:
				if l.status == 'Check':
					n += 1
				else:
					p += 1
		x.append([k, p, n, i[1]])
	return render_template('admin.html', username=session['username'],
	                       all=x)


@app.route('/logout')
def logout():
	session.pop('username', 0)
	session.pop('class', 0)
	session.pop('user_id', 0)
	return redirect('/')


@app.route('/YandexLyceumStudent/<int:s>', methods=['GET', 'POST'])
def index(s):
	if 'username' not in session:
		return redirect('/')
	if (session['user_id'] != s or session['class'] == 'YandexLyceumTeacher') and not (session['class'] == 'Admin'):
		return redirect('/')
	attempts = SolutionAttempt.query.filter_by(student_id=session['user_id']).all()
	user = YandexLyceumStudent.query.filter_by(id=session['user_id']).first()
	
	return render_template('index.html', user=user,
	                       all=attempts, id=int(session['user_id']))


@app.route('/YandexLyceumStudent/<int:s>/add', methods=['GET', 'POST'])
def ss(s):
	return redirect('/YandexLyceumStudent/' +str(s) + '/add/text')


@app.route('/YandexLyceumStudent/<int:s>/add/text', methods=['GET', 'POST'])
def request(s):
	if 'username' not in session:
		return redirect('/login')
	if session['user_id'] != s or session['class'] != 'YandexLyceumStudent':
		return redirect('/')
	form = AddTForm()
	if form.validate_on_submit():
		title = form.title.data
		code = form.content.data
		user = YandexLyceumStudent.query.filter_by(id=s).first()
		attempt = SolutionAttempt(task=title,
		                          code=code,
		                          status='Check')
		user.SolutionAttempts.append(attempt)
		db.session.commit()
		content = form.content.data
		return redirect("/")
	return render_template('add.html', title='Добавление новости',
	                       form=form, username=session['username'], inp='file', id=s)


@app.route("/YandexLyceumStudent/<int:s>/tasks/<int:k>/")
def ta(s, k):
	return redirect(f"/YandexLyceumStudent/{s}/tasks/{k}/text")


@app.route("/YandexLyceumStudent/<int:s>/tasks/<int:k>/text", methods=['GET', 'POST'])
def t(s, k):
	if 'username' not in session:
		return redirect('/login')
	if (session['user_id'] != s or session['class'] != 'YandexLyceumStudent') or session['class'] == 'Admin':
		return redirect("/")
	form2 = Message()
	a = MessageForTask.query.filter_by(task_id=k).all()
	user = YandexLyceumStudent.query.filter_by(id=s).first()
	task = SolutionAttempt.query.filter_by(id=k).first()
	if form2.validate_on_submit():
		data = form2.message.data
		attempt = MessageForTask(message=data, teacher_id=user.teacherid, who='S', student_id=s)
		task.MessageForTask.append(attempt)
		db.session.commit()
		return redirect(f'/YandexLyceumStudent/{s}/tasks/{k}/text')
	return render_template('task.html', title='Новости', user_id=s, task=task, k=a, form2=form2)


@app.route("/YandexLyceumStudent/<int:s>/tasks")
def ter(s):
	if 'username' not in session:
		return redirect('/login')
	if session['user_id'] != s or session['class'] != 'YandexLyceumStudent':
		return redirect("/")
	return redirect('/YandexLyceumStudent/' + str(s))


@app.route("/YandexLyceumStudent/<int:s>/tasks/<int:k>/change/text", methods=['GET', 'POST'])
def te(s, k):
	if 'username' not in session:
		return redirect('/login')
	if session['user_id'] != s or session['class'] != 'YandexLyceumStudent':
		return redirect("/")
	form = Change()
	if form.validate_on_submit():
		code = form.code.data
		a = SolutionAttempt.query.filter_by(id=k).first()
		f = MessageForTask.query.filter_by(task_id=k).all()
		user = YandexLyceumStudent.query.filter_by(id=s).first()
		attempt = SolutionAttempt(task=a.task,
		                          code=code,
		                          status='Check')
		user.SolutionAttempts.append(attempt)
		for i in f:
			r = MessageForTask(message=i.message, student_id=i.student_id, teacher_id=i.teacher_id, who=i.who)
			attempt.MessageForTask.append(r)
		for i in f:
			db.session.delete(i)
		db.session.delete(a)
		db.session.commit()
		return redirect('/' + session['class'] + '/' + str(session['user_id']))
	return render_template('textedit.html', form=form)


@app.route("/YandexLyceumStudent/<int:s>/tasks/<int:k>/delete")
def terk(s, k):
	if 'username' not in session:
		return redirect('/login')
	if session['user_id'] != s or session['class'] != 'YandexLyceumStudent':
		return redirect('/' + session['class'] + '/' + str(session['user_id']))
	f = MessageForTask.query.filter_by(task_id=k).all()
	for i in f:
		db.session.delete(i)
	a = SolutionAttempt.query.filter_by(id=k).first()
	db.session.delete(a)
	db.session.commit()
	return redirect('/' + session['class'] + '/' + str(session['user_id']))


@app.route('/YandexLyceumTeacher/<int:s>', methods=['GET', 'POST'])
def indext(s):
	if 'username' not in session:
		return redirect('/')
	if (session['user_id'] != s or session['class'] == 'YandexLyceumStudent') and not (session['class'] == 'Admin'):
		return redirect('/' + session['class'] + '/' + str(session['user_id']))
	students = YandexLyceumStudent.query.filter_by(teacherid=session['user_id']).all()
	students = [(SolutionAttempt.query.filter_by(student_id=i.id), i) for i in students]
	x = []
	for i in students:
		r = []
		s = 0
		e = 0
		c = 0
		for j in i[0]:
			if j.status == 'OK':
				s += 1
			elif j.status == 'Check':
				c += 1
				r.append(j)
			else:
				e += 1
		x.append([c, s, e, i[1], r])
	students = x.copy()
	user = YandexLyceumTeacher.query.filter_by(id=session['user_id']).first()
	return render_template('indext.html', user=user,
	                       all=students, id=int(session['user_id']))


@app.route('/YandexLyceumTeacher/<int:s>/students/<int:k>', methods=['GET', 'POST'])
def st(s, k):
	if 'username' not in session:
		return redirect('/')
	if (session['user_id'] != s or session['class'] == 'YandexLyceumStudent') and not (session['class'] == 'Admin'):
		return redirect('/' + session['class'] + '/' + str(session['user_id']))
	attempts = SolutionAttempt.query.filter_by(student_id=k).all()
	user = YandexLyceumStudent.query.filter_by(id=k).first()
	return render_template('st.html', user=user,
	                       all=attempts, id=s)


@app.route('/YandexLyceumTeacher/<int:s>/students/<int:k>/tasks/<int:f>/text', methods=['GET', 'POST'])
def stt(s, k, f):
	if 'username' not in session:
		return redirect('/')
	if (session['user_id'] != s or session['class'] == 'YandexLyceumStudent') and not (session['class'] == 'Admin'):
		return redirect('/' + session['class'] + '/' + str(session['user_id']))
	form = Task()
	if form.validate_on_submit():
		a = SolutionAttempt.query.filter_by(id=f).first()
		user = YandexLyceumStudent.query.filter_by(id=s).first()

		c = SolutionAttempt()
		b = YandexLyceumStudent.query.filter_by(id=k).first()
		if form.code.data == 1:
			a.status = 'OK'
			c = SolutionAttempt(task=a.task, status=a.status, code=a.code)
			b.SolutionAttempts.append(c)
		else:
			a.status = 'Error'
			c = SolutionAttempt(task=a.task, status=a.status, code=a.code)
			b.SolutionAttempts.append(c)
		f = MessageForTask.query.filter_by(task_id=f).all()
		for i in f:
			r = MessageForTask(message=i.message, student_id=i.student_id, teacher_id=i.teacher_id, who=i.who)
			c.MessageForTask.append(r)
		for i in f:
			db.session.delete(i)
		db.session.delete(a)
		db.session.commit()
		return redirect('/YandexLyceumTeacher/' + str(s) + '/students/' + str(k))
	form2 = Message()
	a = MessageForTask.query.filter_by(task_id=f).all()
	user = YandexLyceumStudent.query.filter_by(id=k).first()
	task = SolutionAttempt.query.filter_by(id=f).first()
	if form2.validate_on_submit():
		data = form2.message.data
		attempt = MessageForTask(message=data, teacher_id=s, who='T', student_id=k)
		task.MessageForTask.append(attempt)
		db.session.commit()
		return redirect(f'/YandexLyceumTeacher/{s}/students/{k}/tasks/{f}/text')
	return render_template('taskt.html', title='Новости', user_id=s,
	                       task=task, form=form, k=a, form2=form2)


@app.route('/YandexLyceumStudent/<int:s>/add/message', methods=['GET', 'POST'])
def ms(s):
	if 'username' not in session:
		return redirect('/login')
	if session['user_id'] != s or session['class'] != 'YandexLyceumStudent':
		return redirect('/')
	form = Message()
	a = MessageForU.query.filter_by(student_id=s).all()
	user = YandexLyceumStudent.query.filter_by(id=s).first()
	if form.validate_on_submit():
		data = form.message.data
		attempt = MessageForU(message=data, teacher_id=user.teacherid, who='S')
		user.MessageForU.append(attempt)
		db.session.commit()
		return redirect(f'/YandexLyceumStudent/{s}/add/message')
	return render_template('mеssage.html', title='Общение',
	                       form=form, username=session['username'], inp='file', id=s, k=a,
	                       other=YandexLyceumTeacher.query.filter_by(id=user.teacherid).first())


@app.route('/YandexLyceumTeacher/<int:s>/students/<int:k>/add/message', methods=['GET', 'POST'])
def mt(s, k):
	if 'username' not in session:
		return redirect('/login')
	if session['user_id'] != s or session['class'] != 'YandexLyceumTeacher':
		return redirect('/')
	form = Message()
	a = MessageForU.query.filter_by(student_id=s).all()
	student = YandexLyceumStudent.query.filter_by(id=k).first()
	if form.validate_on_submit():
		data = form.message.data
		attempt = MessageForU(message=data, teacher_id=s, who='T')
		student.MessageForU.append(attempt)
		db.session.commit()
		return redirect(f'/YandexLyceumTeacher/{s}/students/{k}/add/message')
	return render_template('mеssage.html', title='Общение',
	                       form=form, username=session['username'], inp='file', id=s, k=a,
	                       other=student)


if __name__ == '__main__':
	app.run(port=8080, host='127.0.0.1')
