from flask import (
	Blueprint,flash,g,redirect,render_template,request,url_for
)
from werkzeug.exceptions import abort
from todo.auth import login_required
from todo.db import get_db
from werkzeug.utils import secure_filename
import os

bp=Blueprint('todo',__name__)

@bp.route('/')
@login_required
def index():
	db,c=get_db()
	c.execute(
		"SELECT a.descripcion 'descripcion',p.prof_nombre 'titular',a.titulo 'titulo' from actividad a inner join profesor p on a.titular=prof_id inner join estudiante e on e.fkgrupo=a.fk_grupo inner join user u on e.fkuser=u.user_id where u.username=%s",(g.user['username'],))
	todos=c.fetchall()
	return render_template('todo/index.html',todos=todos)

@bp.route('/pupilo',methods=['GET','POST'])
@login_required
def est_page():
	db,c=get_db()
	c.execute(
		"SELECT a.descripcion 'descripcion',p.prof_nombre 'tiular',a.titulo 'titulo', g.gru_clave 'Clave',e.es_nom 'nom',e.es_apellidos 'app' from actividad a inner join profesor p on a.titular=prof_id inner join estudiante e on e.fkgrupo=a.fk_grupo  inner join grupo g on e.fkgrupo=g.gru_id inner join user u on e.fkuser=u.user_id where u.username=%s",(g.user['username'],))
	activity=c.fetchall()
	return render_template('todo/est_page.html',activity=activity)
@bp.route('/up',methods=['POST'])
@login_required
def uploader():
	if request.method == 'POST':
		grupo=request.form['codeg']
		esname=request.form['esname']
		eslast=request.form['eslast']
		title=request.form['title']
		fullname=esname+"_"+eslast
		print('FULL: ',fullname)
		crea_dir(2021,grupo,fullname,title)
	  # obtenemos el archivo del input "archivo"
		f = request.files['archivo']
		filename = secure_filename(f.filename)
	  # Guardamos el archivo en el directorio "Archivos PDF"
		ruta='C:\\Users\\Admin\\Documents\\pyt\\tutoria\\todo\\Archivos_PDF\\2021\\INF1A\\Reyson_Antonio'
		f.save(os.path.join(ruta, filename))
	  # Retornamos una respuesta satisfactoria
		return redirect(url_for('todo.est_page'))
@bp.route('/tutor',methods=['GET','POST'])
@login_required
def prof_page():
	db,c=get_db()
	
	c.execute("SELECT g.gru_clave 'Grupo',c.codigo 'Carrera',g.gru_id 'gc' from grupo g inner join carrera c on g.fk_carrera=c.car_id  inner join profesor p on g.fk_tutor=p.prof_id inner join user u on u.user_id=p.fkuser where u.username=%s;",(g.user['username'],))
	activity=c.fetchall()
	return render_template('todo/prof_page.html',activity=activity)

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

@bp.route('/<int:gc>/new_act',methods=['GET','POST'])
@login_required
def nueva_actividad(gc):
	return render_template('todo/new_actividad.html',gc=gc)

@bp.route('/added',methods=['POST'])
@login_required
def actividad_novo():
	if request.method=='POST':
		#intentar declarar el grupo de otra manera
		grupo=request.form['group']
		title=request.form['title']
		content=request.form['content']

		
		db, c=get_db()
		c.execute('SELECT prof_id from profesor where fkuser=%s',(g.user['user_id'],))
		prof=c.fetchone()
		c.execute('insert into actividad(titular,fk_grupo,titulo,descripcion) values(%s,%s,%s,%s)',(prof['prof_id'],grupo,title,content))
		db.commit()
		flash("Se ha agregado la actividad")
		return redirect(url_for('todo.prof_page'))
	
	

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

def crea_dir(anho,gru,nom,act):
	#directorio = "Archivos_PDF\\"+anho
	try:
	    #os.mkdir(directorio)
	    os.mkdir.join(directorio,anho)
	except OSError:
	    print("La creación del directorio %s falló" % directorio)
	else:
	    print("Se ha creado el directorio: %s " % directorio)

	directorio = "Archivos_PDF\\"+anho+"\\"+gru
	try:
	    os.mkdir(directorio)
	except OSError:
	    print("La creación del directorio %s falló" % directorio)
	else:
	    print("Se ha creado el directorio: %s " % directorio)

	directorio = "Archivos_PDF\\"+anho+"\\"+gru+"\\"+nom
	try:
	    os.mkdir(directorio)
	except OSError:
	    print("La creación del directorio %s falló" % directorio)
	else:
	    print("Se ha creado el directorio: %s " % directorio)

	directorio = "Archivos_PDF\\"+anho+"\\"+gru+"\\"+nom+"\\"+act
	try:
	    os.mkdir(directorio)
	except OSError:
	    print("La creación del directorio %s falló" % directorio)
	else:
	    print("Se ha creado el directorio: %s " % directorio)
	