from flask import (
	Blueprint,flash,g,redirect,render_template,request,url_for,abort,send_file
)
from werkzeug.exceptions import abort
from todo.auth import login_required,solo_admin,solo_ar,solo_es,solo_prof
from todo.db import get_db
from werkzeug.utils import secure_filename
import os

from pathlib import Path,PurePath
from io import BytesIO
from flask_wtf.file import FileField
from wtforms import SubmitField
from flask_wtf import Form
bp=Blueprint('todo',__name__)

@bp.route('/')
@login_required
def index():
	db,c=get_db()
	c.execute(
		"SELECT a.descripcion 'descripcion',p.prof_nombre 'titular',a.titulo 'titulo' from actividad a inner join profesor p on a.titular=prof_id inner join estudiante e on e.fkgrupo=a.fk_grupo inner join user u on e.fkuser=u.user_id where u.username=%s",(g.user['username'],))
	todos=c.fetchall()
	return render_template('todo/index.html',todos=todos)

@bp.route('/registro_es')
@login_required
def reg_es():
	db,c=get_db()
	c.execute(
		"SELECT * from grupo")
	grupos=c.fetchall()
	return render_template('auth/register.html',grupos=grupos)
@bp.route('/registro_prof')
@login_required
def reg_prof():
	db,c=get_db()
	c.execute(
		"SELECT * from grupo")
	grupos=c.fetchall()
	return render_template('auth/register_prof.html',grupos=grupos)
@bp.route('/admin')
@login_required
def admin():
	return render_template('todo/admin.html')
@bp.route('/pupilo',methods=['GET','POST'])
@login_required
def est_page():
	return render_template('todo/est_page.html')

@bp.route('/rev_actividades',methods=['GET','POST'])
@login_required
def act_pen():
	db,c=get_db()
	c.execute(
		"""
		SELECT  a.titulo 'titulo',a.descripcion 'descripcion',e.es_nom 'nom',e.es_apellidos 'app',
		ea.entregado 'estado' ,a.act_id 'acid' from es_ac ea
		inner join actividad a on ea.fk_ac=a.act_id
		inner join estudiante e on ea.fk_es=e.nc
		inner join user u on e.fkuser=u.user_id
		where u.username=%s AND ea.entregado=0;
		""",(g.user['username'],))
	activity=c.fetchall()
	return render_template('todo/vis_ac_p.html',activity=activity)

@bp.route('/act_pas',methods=['GET','POST'])
@login_required
def act_pas():
	db,c=get_db()
	c.execute("""SELECT  a.titulo 'titulo',a.descripcion 'descripcion',e.es_nom 'nom',e.es_apellidos 'app',
		ea.entregado 'estado' ,a.act_id 'acid',ea.puntuacion 'pun' from es_ac ea
		inner join actividad a on ea.fk_ac=a.act_id
		inner join estudiante e on ea.fk_es=e.nc
		inner join user u on e.fkuser=u.user_id
		where u.username=%s AND ea.entregado=%s
		""",(g.user['username'],1))
	activity=c.fetchall()
	return render_template('todo/vis_ac_ter.html',activity=activity)

@bp.route('/consulta_general_estudiantes',methods=['GET','POST'])
@login_required
def cons_gral_es():
	db,c=get_db()
	c.execute(
		"""SELECT * from carrera""")
	grupos=c.fetchall()
	return render_template('todo/cons_gral_est.html',grupos=grupos)

@bp.route('/bus_es',methods=['GET','POST'])
@login_required
def bus_es():
	form = SearchForm(request.form)
	if request.method == 'POST'and form.validate():
		nc=request.form['nc']
		gc=request.form['gc']
		cc=request.form['cc']
		
		db,c=get_db()
		if nc :
			c.execute(
			"SELECT e.* from estudiante e where e.nc=%s",(nc,))
			res=c.fetchall()
			return redirect(url_for('todo/cons_gral_est.html',res=res))
		flash('No entraste','danger')
		#elif gc:
		#	c.execute(
		#	"""SELECT * from carrera""")
		#elif cc:
		#	c.execute(
		#	"""SELECT * from carrera""")
		
			
		#return render_template('todo/cons_gral_est.html',res=res)


@bp.route('/<int:acid>/up',methods=['POST'])
@login_required
def uploader(acid):
	if request.method == 'POST':
		comment=request.form['comment']
		
        ##Sirve
		db,c=get_db()
		c.execute('CALL alta_es_ac(%s,%s,%s)',(g.user['username'],acid,comment))
		db.commit()
		flash('Hecho','success')
		return redirect(url_for('todo.est_page'))
					#SIRVE



@bp.route('/<int:acid>/<nc>/revisado',methods=['POST'])
@login_required
def revisado(acid,nc):
	if request.method == 'POST':
		pun=request.form['sel']
		comment=request.form['comment']
		print("Puntuacion es: "+pun)
		print("Comentario "+comment)
		db,c=get_db()
		c.execute("UPDATE es_ac SET puntuacion = %s,prof_comment=%s WHERE (fk_ac = %s AND fk_es=%s)",(pun,comment,acid,nc))
		db.commit()
		return redirect(url_for('todo.prof_page'))

@bp.route('/<int:acid>/<nc>/subirblob',methods=['POST'])
@login_required
def subirblob(acid,nc):
	form = UploadForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			file_name = form.file.data
            #database(name=file_name.filename, data=file_name.read() )
            

			comment="comentario equis"
			
			print("Comentario "+comment)
			
			db,c=get_db()
			c.execute("UPDATE es_ac SET data = %s WHERE (fk_ac = %s AND fk_es=%s)",(file_name.read(),acid,nc))
			db.commit()
			return redirect(url_for('todo.prof_page'))

	
@bp.route('/tutor',methods=['GET','POST'])
@login_required
def prof_page():
	db,c=get_db()
	
	c.execute("SELECT g.gru_clave 'Grupo',c.codigo 'Carrera',g.gru_id 'gc' from grupo g inner join carrera c on g.fk_carrera=c.car_id  inner join profesor p on g.fk_tutor=p.prof_id inner join user u on u.user_id=p.fkuser where u.username=%s;",(g.user['username'],))
	activity=c.fetchall()
	return render_template('todo/prof_page.html',activity=activity)

@bp.route('/bus_in_es')
@login_required
def bus_in_es():
	dato=None
	return render_template('todo/bus_in_es.html',dato=dato)

@bp.route('/bus_indiv_es',methods=['GET','POST'])
@login_required
def bus_indiv_es():
	if request.method=='POST':
		usu=request.form['usu']
		code=request.form['code']

		db, c=get_db()
		dato=None
		if usu:
			c.execute("""SELECT e.nc,e.es_nom 'nom',e.es_apellidos 'app',u.username 'usu',g.gru_clave 'gc',c.titulo 'car',e.es_correo 'cor'
			from estudiante e
			inner join user u on e.fkuser=u.user_id
			inner join grupo g on e.fkgrupo=g.gru_id
			inner join carrera c on g.fk_carrera=c.car_id
			where u.username=%s;
			""",(usu,))
			dato=c.fetchone()
			

		if code:
			c.execute("""SELECT e.nc,e.es_nom 'nom',e.es_apellidos 'app',u.username 'usu',g.gru_clave 'gc',c.titulo 'car',e.es_correo 'cor'
			from estudiante e
			inner join user u on e.fkuser=u.user_id
			inner join grupo g on e.fkgrupo=g.gru_id
			inner join carrera c on g.fk_carrera=c.car_id
			where e.nc=%s;
			""",(code,))
			dato=c.fetchone()
				 

		if usu and code:
			c.execute("""SELECT e.nc,e.es_nom 'nom',e.es_apellidos 'app',u.username 'usu',g.gru_clave 'gc',c.titulo 'car',e.es_correo 'cor'
			from estudiante e
			inner join user u on e.fkuser=u.user_id
			inner join grupo g on e.fkgrupo=g.gru_id
			inner join carrera c on g.fk_carrera=c.car_id
			where e.nc=%s;
			""",(code,))
			dato=c.fetchone()


		return render_template('todo/bus_in_es.html',dato=dato)
	


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

@bp.route('/<gr>/new_act',methods=['GET','POST'])
@login_required
def nueva_actividad(gr):
	
	return render_template('todo/new_actividad.html',gr=gr)
	

@bp.route('/<int:acid>/<int:gc>/revision_ac_gru',methods=['GET','POST'])
@login_required
def revi_gru(acid,gc):
	if request.method=="POST":
		db, c=get_db()
		titulo=request.form['title']
		c.execute('CALL get_alum_ac(%s,%s)',(gc,acid))
		todo=c.fetchall()
		
		return render_template('todo/rev_gru_actividades.html',tt=titulo,todo=todo,gc=gc,acid=acid)


@bp.route('/<gc>/activ_pendientes',methods=['GET'])
@login_required
def rev_actividad(gc):
	#CALL get_Ac_grupo('rantoso',2);
	db,c=get_db()
	c.execute(
		"CALL get_Ac_grupo(%s,%s);",(g.user['username'],gc))
	activity=c.fetchall()
	#return render_template('todo/est_page.html',activity=activity)
	return render_template('todo/rev_actividades.html',gc=gc,activity=activity)

@bp.route('/added',methods=['POST'])
@login_required
def actividad_novo():
	if request.method=='POST':
		#intentar declarar el grupo de otra manera
		grupo=request.form['group']
		title=request.form['title']
		content=request.form['content']

		db, c=get_db()
		
		c.execute('CALL alta_actividad(%s,%s,%s,%s)',(grupo,g.user['username'],title,content))
		db.commit()
		
		flash("Se ha agregado la actividad",'info')
		return redirect(url_for('todo.prof_page'))
	
@bp.route('/<nc>/<int:acid>/rev_ind',methods=['POST'])
@login_required
def rev_ind(nc,acid):
	if request.method=='POST':
		#intentar declarar el grupo de otra manera
		
		db, c=get_db()
		
		c.execute('CALL getAct_ind(%s,%s)',(acid,nc))
		revision=c.fetchone()
		
		

		return render_template('todo/vis_cal_actividad.html',revision=revision)


@bp.route('/<int:acid>/ac_vis_full',methods=['POST'])
@login_required
def ac_vis_full(acid):
	form = UploadForm()
	if request.method=='POST':
		#intentar declarar el grupo de otra manera
		
		db, c=get_db()
		c.execute("""
			SELECT e.nc 'nc',ea.puntuacion 'pun',ea.prof_comment 'pc', 
			ea.entregado 'en' ,a.act_id 'acid',e.es_nom 'nom',
			e.es_apellidos 'app',a.titulo,a.descripcion 
			from es_ac ea
			inner join actividad a on ea.fk_ac=a.act_id
			inner join estudiante e on e.nc=ea.fk_es
			inner join user u on e.fkuser=u.user_id
			where a.act_id=%s and u.username=%s;
			""",(acid,g.user['username']))
		ac=c.fetchone()
		return render_template('todo/vis_ac_completa.html',ac=ac,form=form)


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
    directorio = PurePath(Path.cwd(),'Archivos_PDF')
    print(directorio)
    Path(directorio).mkdir(exist_ok=True)
    
    directorio=PurePath(directorio,anho)
    print(directorio)
    Path(directorio).mkdir(exist_ok=True)

    directorio=PurePath(directorio,gru)
    print(directorio)
    Path(directorio).mkdir(exist_ok=True)

    directorio=PurePath(directorio,nom)
    print(directorio)
    Path(directorio).mkdir(exist_ok=True)

    directorio=PurePath(directorio,act)
    print(directorio)
    Path(directorio).mkdir(exist_ok=True)

    return directorio

class UploadForm(Form):
    file = FileField()
    submit = SubmitField("submit")
    download = SubmitField("download")