import functools

from flask import Blueprint,flash,g,render_template,request,url_for,session,redirect,abort
from werkzeug.security import check_password_hash, generate_password_hash

from todo.db import get_db

bp = Blueprint('auth',__name__,url_prefix='/auth')
@bp.route('/register',methods=['GET','POST'])
def register():
	if request.method=='POST':
		if g.user['fk_rol']==1:
			name=request.form['name']
			lastname=request.form['lastname']
			nc=request.form['nc']
			group=request.form['group']
			generacion=request.form['generacion']
			email=request.form['email']

			username=request.form['username']
			password=request.form['password']
			db, c= get_db()
			error = None
			c.execute('select user_id from user where username = %s',(username,))
			if not username:
				error='Username es requerido'
			if not password:
				error='Password es requerido'
			elif c.fetchone() is not None:
				error= 'Usuario {} se encuentra registrado'.format(username)

			if error is None:
				#c.execute('insert into user(username,password) values (%s,%s)',(username,generate_password_hash(password)))
				c.execute('call altaEstudiante(%s,%s,%s,%s,%s,%s,%s,%s)',(nc,name,lastname,group,generacion,email,username,generate_password_hash(password)))
				
				db.commit()
				#return redirect(url_for('auth.login'))
				return redirect(url_for('todo.admin'))
			flash(u'Invalid password provided', 'error')

	else:
		abort(403)
	

@bp.route('/register_prof',methods=['GET','POST'])
def register_prof():
	if request.method=='POST':
		if g.user['fk_rol']==1:
			name=request.form['name']
			lastname=request.form['lastname']
			nc=request.form['nc']
			email=request.form['email']

			username=request.form['username']
			password=request.form['password']
			db, c= get_db()
			error = None
			c.execute('select user_id from user where username = %s',(username,))
			if not username:
				error='Username es requerido'
			if not password:
				error='Password es requerido'
			elif c.fetchone() is not None:
				error= 'Usuario {} se encuentra registrado'.format(username)

			if error is None:
				#c.execute('insert into user(username,password) values (%s,%s)',(username,generate_password_hash(password)))
				c.execute('call alta_profesor(%s,%s,%s,%s,%s,%s)',(nc,name,lastname,email,username,generate_password_hash(password)))
				
				db.commit()
				return redirect(url_for('auth.login'))
			flash(error)
		return render_template('auth/register_prof.html')
	else:
		abort(403)
@bp.route('/register_root',methods=['GET','POST'])
def register_root():
	if request.method=='POST':
		if g.user['fk_rol']==1:
			username=request.form['username']
			password=request.form['password']
			db, c= get_db()
			error = None
			c.execute('select user_id from user where username = %s',(username,))
			if not username:
				error='Username es requerido'
			if not password:
				error='Password es requerido'
			elif c.fetchone() is not None:
				error= 'Usuario {} se encuentra registrado'.format(username)

			if error is None:
				#c.execute('insert into user(username,password) values (%s,%s)',(username,generate_password_hash(password)))
				c.execute('INSERT INTO user(username,password,fk_rol) values(%s,%s,%s)',(username,generate_password_hash(password),1))
				
				db.commit()
				return redirect(url_for('auth.login'))
			flash(error)
		return render_template('auth/register_root.html')
	else :
		abort(403)
		

@bp.route('/login',methods=['GET','POST'])
def login():
	if request.method=='POST':
		username=request.form['username']
		password=request.form['password']
		db,c=get_db()
		error=None
		c.execute('SELECT * FROM user WHERE username = %s',(username,))
		user=c.fetchone()

		if user is None:
			error='Usuario y o contraseña invalida'
		elif not check_password_hash(user['password'],password):
			error= 'Usuario y/o contraseña invalida'
		if error is None:
			session.clear()
			session['user_id']=user['user_id']
			c.execute('SELECT get_rolid(%s)',(user['username'],))
			usu=user['username']
			rol=c.fetchone()
			tipo_user=rol["get_rolid('"+usu+"')"]
			
			if tipo_user==1:
				flash('Has logueado exitosamente','success')
				return redirect(url_for('todo.admin'))
			elif tipo_user==2:
				flash('Has logueado exitosamente','success')
				return redirect(url_for('todo.prof_page'))
			elif tipo_user==3:
				flash('Has logueado exitosamente','success')
				return redirect(url_for('todo.est_page'))


			

		flash(error,'danger')

	return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
	user_id=session.get('user_id')

	if user_id is None:
		g.user=None
	else:
		db, c=get_db()
		c.execute(
			'select u.username,u.fk_rol from user u where user_id=%s',(user_id,)
		)
		g.user=c.fetchone()
#		get_grupos(user_id)
#def get_grupos(user_id):
	#db, c=get_db()
	#c.execute('CALL getGrupos_prof_usid(%s)',(user_id,))
	#g.gru_clave=c.fetchall()

def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			return redirect(url_for('auth.login'))
		return view(**kwargs)

	return wrapped_view

@bp.route('/logout')
def logout():
	session.clear()
	flash('Has salido','warning')
	return redirect(url_for('auth.login'))