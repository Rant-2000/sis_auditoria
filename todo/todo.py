from flask import (
	Blueprint,flash,g,redirect,render_template,request,url_for
)
from werkzeug.exceptions import abort
from todo.auth import login_required
from todo.db import get_db

bp=Blueprint('todo',__name__)

@bp.route('/')
@login_required
def index():
	db,c=get_db()
	c.execute(
		"SELECT a.descripcion 'descripcion',p.prof_nombre 'titular',a.titulo 'titulo' from actividad a inner join profesor p on a.titular=prof_id inner join estudiante e on e.fkgrupo=a.fk_grupo inner join user u on e.fkuser=u.user_id where u.username=%s",(g.user['username'],))
	todos=c.fetchall()
	return render_template('todo/index.html',todos=todos)

@bp.route('/estudent',methods=['GET','POST'])
@login_required
def est_page():
	db,c=get_db()
	c.execute(
		"SELECT a.descripcion 'descripcion',p.prof_nombre 'titular',a.titulo 'titulo' from actividad a inner join profesor p on a.titular=prof_id inner join estudiante e on e.fkgrupo=a.fk_grupo inner join user u on e.fkuser=u.user_id where u.username=%s",(g.user['username'],))
	todos=c.fetchall()
	return render_template('todo/est_page.html',todos=todos)

@bp.route('/create',methods=['GET','POST'])
@login_required
def create():
	if request.method=='POST':
		description=request.form['description']
		error=None
		if not description:
			error='Descripcion es requerido'
		if error is not None:
			flash(error)
		else:
			db,c=get_db()
			c.execute('insert into todo(description,completed,created_by) values(%s,%s,%s)',(description,False,g.user['id']))
			db.commit()
			return redirect(url_for('todo.index'))

	return render_template('todo/create.html')
def get_todo(id):
	db, c=get_db()
	c.execute('SELECT t.id,t.description,t.completed,t.created_by,t.created_at,u.username from todo t join user u on t.created_by=u.id where t.id=%s',(id,))
	todo=c.fetchone()
	if todo is None:
		abort(404,'EL todo de ID {0} no existe'.format(id))
	return todo
@bp.route('/<int:id>/update',methods=['GET','POST'])
@login_required
def update(id):
	todo= get_todo(id)
	if request.method=='POST':
		description=request.form['description']
		completed=True if request.form.get('completed')=='on' else False
		error=None

		if not description:
			error='La Descripcion es requerida'
		if error is not None:
			flash(error)
		else:
			db,c=get_db()
			c.execute('update todo set description=%s,completed=%s where id=%s and created_by=%s',(description,completed,id,g.user['id']))
			db.commit()
			return redirect(url_for('todo.index'))

	return render_template('todo/update.html',todo=todo)
	#return ''
@bp.route('/<int:id>/delete',methods=['POST'])
@login_required
def delete(id):
	db,c=get_db()
	c.execute('delete from todo where id=%s and created_by=%s',(id,g.user['id']))
	db.commit()
	return redirect(url_for('todo.index'))

	#return render_template('todo/create.html',todo=todo)
	return ''