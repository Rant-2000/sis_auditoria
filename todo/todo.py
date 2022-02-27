from flask import (
	Blueprint,flash,g,redirect,render_template,request,url_for,abort,send_file,jsonify
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash
from todo.auth import login_required,solo_admin,solo_ar,solo_es,solo_prof
from todo.db import get_db
from werkzeug.utils import secure_filename
import os
import datetime
from pathlib import Path,PurePath
from io import BytesIO
from flask_wtf.file import FileField
from wtforms import SubmitField
from flask_wtf import Form
import mysql.connector
import xlrd
import pandas as pd
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
	print('Entra al method')
	if  g.user['fk_rol']==1:
		
		db,c=get_db()
		c.execute(
		"SELECT * from grupo")
		grupos=c.fetchall()
		return render_template('estudiante/register.html',grupos=grupos)
	else:
		return abort(403)

@bp.route('/consulta_motivos')
@login_required
def cons_mot():
	print('Entra al method')
	if  g.user['fk_rol']==1:
		db,c=get_db()
		c.execute(
		"SELECT * from motivo")
		r=c.fetchall()
		return render_template('super/cons_motivos.html',r=r)
	else:
		return abort(403)

@bp.route('/registro_motivo')
@login_required
def reg_mot():
	print('Entra al method')
	if  g.user['fk_rol']==1:
		return render_template('super/new_motivo.html')
	else:
		return abort(403)

@bp.route('/mot_agregado',methods=['GET','POST'])
@login_required
def motivo_agregado():
	
	if  g.user['fk_rol']==1:
		if request.method == 'POST':
			
			des=request.form['content']
			db,c=get_db()
			c.execute(
			"INSERT INTO motivo(descripcion) values(%s);",(des,))
			db.commit()
			flash("Agregado Exitosamente!",'success')
		else:
			flash("ERROR",'warning')
		return render_template('super/new_motivo.html')
	else:
		return abort(403)
@bp.route('/<int:idm>/<mot>/edit_mot',methods=['GET','POST'])
@login_required
def edit_mot(idm,mot):
	
	if  g.user['fk_rol']==1:
		if request.method == 'POST':
			
			return render_template('super/edit_motivo.html',mot=mot,idm=idm)
		else:
			flash("ERROR",'warning')
		return render_template('super/cons_mot.html')
	else:
		return abort(403)
@bp.route('/<int:idmot>/motivo_modificado',methods=['GET','POST'])
@login_required
def motivo_modificado(idmot):
	
	if  g.user['fk_rol']==1:
		if request.method == 'POST':
			#SQL
			des=request.form['content']
			db,c=get_db()
			c.execute( "UPDATE motivo set descripcion=%s where idmotivo=%s",(des,idmot))
			db.commit()


			##
			flash("Modificado Correctamente",'success')
			return render_template('super/admin.html')
		else:
			flash("ERROR",'warning')
		return render_template('super/cons_mot.html')
	else:
		return abort(403)

@bp.route('/registro_prof')
@login_required
def reg_prof():
	if  g.user['fk_rol']==1:
		db,c=get_db()
		c.execute(
			"SELECT * from grupo")
		grupos=c.fetchall()
		return render_template('profesor/register_prof.html',grupos=grupos)
	else :
		return abort(403)

@bp.route('/nuevo_grupo')
@login_required
def nuevo_grupo():
	if  g.user['fk_rol']==1:
		return render_template('grupo/new_grupo.html')
	else:
		return abort(403)

@bp.route('/nuevo_anuncio')
@login_required
def nuevo_anuncio():
	if  g.user['fk_rol']==1:
		return render_template('anuncios/new_anuncio.html')
	else:
		return abort(403)

@bp.route('/nueva_activi')
@login_required
def nueva_activi():
	if  g.user['fk_rol']==1:
		db,c=get_db()
		c.execute(
		"SELECT * from grupo")
		grupos=c.fetchall()
		return render_template('super/nueva_Act.html',grupos=grupos)
	else:
		return abort(403)

@bp.route('/new_anun')
@login_required
def new_anun():
	if  g.user['fk_rol']==1:
		db,c=get_db()
		c.execute(
		"SELECT * from grupo")
		grupos=c.fetchall()
		return render_template('super/new_anuncio.html',grupos=grupos)
	else:
		return abort(403)

@bp.route('/admin')
@login_required
def admin():
	if  g.user['fk_rol']==1:
		return render_template('super/admin.html')
	else:

		return abort(403)


	
@bp.route('/pupilo',methods=['GET','POST'])
@login_required
def est_page():
	if  g.user['fk_rol']==3:
		db,c=get_db()
		c.execute("""
			SELECT a.* FROM anuncio a
			inner join grupo g on a.fk_grupo=g.gru_id
			inner join estudiante e on e.fkgrupo=g.gru_id
			inner join user u on u.user_id=e.fkuser
			where u.username=%s;
			""",(g.user['username'],))
		anun=c.fetchall()
		return render_template('estudiante/est_page.html',anun=anun)
	else:

		return abort(403)
	

@bp.route('/rev_actividades',methods=['GET','POST'])
@login_required
def act_pen():
	if  g.user['fk_rol']==3:
		db,c=get_db()
		c.execute(
		"""
		SELECT  a.titulo 'titulo',a.descripcion 'descripcion',e.es_nom 'nom',e.es_apellidos 'app',
		ea.entregado 'estado' ,a.act_id 'acid',a.visible 'vis',a.f_limite 'flim' from es_ac ea
		inner join actividad a on ea.fk_ac=a.act_id
		inner join estudiante e on ea.fk_es=e.nc
		inner join user u on e.fkuser=u.user_id
		where u.username=%s AND ea.entregado=0;
		""",(g.user['username'],))
		activity=c.fetchall()
		currentDateTime = datetime.datetime.now()
					
		fsin = currentDateTime.date()
		fe=datetime.datetime(fsin.year, fsin.month, fsin.day)


		return render_template('estudiante/vis_ac_p.html',activity=activity,fe=fe)
	else:

		return abort(403)
	

@bp.route('/act_pas',methods=['GET','POST'])
@login_required
def act_pas():
	if  g.user['fk_rol']==3:


		db,c=get_db()
		c.execute("""SELECT  a.titulo 'titulo',a.descripcion 'descripcion',e.es_nom 'nom',e.es_apellidos 'app',
			ea.entregado 'estado' ,a.act_id 'acid',ea.puntuacion 'pun' from es_ac ea
			inner join actividad a on ea.fk_ac=a.act_id
			inner join estudiante e on ea.fk_es=e.nc
			inner join user u on e.fkuser=u.user_id
			where u.username=%s AND ea.entregado=%s
			""",(g.user['username'],1))
		activity=c.fetchall()
		return render_template('estudiante/vis_ac_ter.html',activity=activity)
	else:
		abort(403)

@bp.route('/consulta_general_estudiantes',methods=['GET','POST'])
@login_required
def cons_gral_es():
	if  g.user['fk_rol']==1:
		db,c=get_db()
		c.execute(
			"""SELECT * from carrera""")
		grupos=c.fetchall()
		return render_template('super/cons_gral_est.html',grupos=grupos)
	else:
		abort(403)

@bp.route('/bus_es',methods=['GET','POST'])
@login_required
def bus_es():
	if  g.user['fk_rol']==1:
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
	else:
		abort(403)
		#elif gc:
		#	c.execute(
		#	"""SELECT * from carrera""")
		#elif cc:
		#	c.execute(
		#	"""SELECT * from carrera""")
		
			
		#return render_template('todo/cons_gral_est.html',res=res)

@bp.route('/subir_plantilla',methods=['POST'])
@login_required
def subir_plantilla():
	if request.method == 'POST':
		if  g.user['fk_rol']==2:
			try:
				currentDateTime = datetime.datetime.now()
				date = currentDateTime.date()
				year = date.strftime("%Y")
				f = request.files['file']
				ruta=crea_dir_docs(year,g.user['username'])

				f.save(os.path.join(ruta, f.filename))
				rutabd=os.path.join(ruta, f.filename)
	      		#Lo guardas en la bd
				nruta=year+"/"+g.user['username']+"/"+secure_filename(f.filename)
				print("Ruta para n ",nruta)
				print("Ruta para bd ",rutabd)
				print(request.files['file'])
				#f = request.files['file']
				data_xls = pd.read_excel(f)
				print(data_xls)
				##Sirve
				
				#db,c=get_db()
				#c.execute('CALL alta_es_ac(%s,%s,%s,%s)',(g.user['username'],acid,comment,nruta))
				#db.commit()
				flash('Hecho','success')
				return redirect(url_for('todo.prof_page'))
			except mysql.connector.Error as err:
				#flash('Error','danger')
				abort(404)
			
		else:
			abort(403)
					#SIRVE

@bp.route('/<int:acid>/<name>/<gr>/<titulo>/<last>/up',methods=['POST'])
@login_required
def uploader(acid,name,gr,last,titulo):
	if request.method == 'POST':
		if  g.user['fk_rol']==3:

			comment=request.form['comment']
			
	        

			currentDateTime = datetime.datetime.now()
			date = currentDateTime.date()
			year = date.strftime("%Y")

			app=last
			try:
				f = request.files['file']
				ruta=crea_dir(year,gr,name,app,titulo)

				f.save(os.path.join(ruta, f.filename))
				rutabd=os.path.join(ruta, f.filename)
	      		#Lo guardas en la bd
				nruta=year+"/"+gr+"/"+name+"/"+app+"/"+titulo+"/"+secure_filename(f.filename)
				print("Ruta para bd ",nruta)

				##Sirve
				db,c=get_db()
				c.execute('CALL alta_es_ac(%s,%s,%s,%s)',(g.user['username'],acid,comment,nruta))
				db.commit()
				flash('Hecho','success')
				return redirect(url_for('todo.est_page'))
			except mysql.connector.Error as err:
				#flash('Error','danger')
				abort(404)
			
		else:
			abort(403)
					#SIRVE
ALLOWED_EXTENSIONS = set(['pdf'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/<int:acid>/<nc>/revisado',methods=['POST'])
@login_required
def revisado(acid,nc):
	if request.method == 'POST':
		if g.user['fk_rol']==1 or g.user['fk_rol']==2:

			pun=request.form['sel']
			comment=request.form['comment']
			print("Puntuacion es: "+pun)
			print("Comentario "+comment)
			db,c=get_db()
			c.execute("UPDATE es_ac SET puntuacion = %s,prof_comment=%s WHERE (fk_ac = %s AND fk_es=%s)",(pun,comment,acid,nc))
			db.commit()
			return redirect(url_for('todo.prof_page'))
		else:
			abort(404)

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
	if g.user['fk_rol']==2:
		db,c=get_db()
		
		c.execute("SELECT g.gru_clave 'Grupo',c.codigo 'Carrera',g.gru_id 'gc' from grupo g inner join carrera c on g.fk_carrera=c.car_id  inner join profesor p on g.fk_tutor=p.prof_id inner join user u on u.user_id=p.fkuser where u.username=%s;",(g.user['username'],))
		activity=c.fetchall()
		return render_template('profesor/prof_page.html',activity=activity)
	else:
		abort(404)

@bp.route('/upd_est', methods=['GET','POST'])
@login_required
def upd_est():
	if request.method=='POST':
		if g.user['fk_rol']==1:
			nom=request.form['nom']
			app=request.form['app']
			
			if request.form['conpin']:
				conpin=generate_password_hash(request.form['conpin'])
			else:
				conpin=None
			#Para checkbox
			ddb=request.form.get('ddb')
			
			if ddb== None:
				ddb=1
			else:
				ddb=0
			#print("DDB es ",ddb)
			usu=request.form['usu2']
			#car=request.form['car']
			gr=request.form['gr']
			cor=request.form['cor']
			gg=request.form['gg']
			ncc=request.form['nc']
			##SQL
			#print("Datos: ",nom,app,conpin,usu,gr,gg)
			db, c=get_db()
																#(enom varchar(45), epp varchar(45), uses varchar(25), uspass longtext,eug  varchar(7),gg varchar(5),ncc varchar(8),ecor varchar(40))
			c.execute("CALL mod_estudiante(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(nom,app,usu,conpin,gr,gg,ncc,cor,ddb))
			db.commit()

			dato=None
			flash("Actualizado Correctamente",'success')
			return render_template('super/edit_estudiante.html',dato=dato)
		else:
			abort(403)
	else:
			abort(403)

@bp.route('/upd_pr', methods=['GET','POST'])
@login_required
def upd_pr():
	if request.method=='POST':
		if g.user['fk_rol']==1:
			nom=request.form['nom']
			app=request.form['app']
			
			if request.form['conpin']:
				conpin=generate_password_hash(request.form['conpin'])
			else:
				conpin=None
			#Para checkbox
			
			usu=request.form['usu2']
			
			cor=request.form['cor']
		
			ncc=request.form['nc']
			##SQL
			#print("Datos: ",nom,app,conpin,usu,gr,gg)
			db, c=get_db()
										#(nnom varchar(45),napp varchar(45),ncor varchar(40),nuser varchar(25),ncon longtext, vnc varchar(8))
			c.execute("CALL mod_profesor(%s,%s,%s,%s,%s,%s)",(nom,app,cor,usu,conpin,ncc))
			db.commit()

			dato=None
			flash("Actualizado Correctamente",'success')
			return render_template('super/edit_profesor.html',dato=dato)
		else:
			abort(403)
	else:
			abort(403)

@bp.route('/modi_es')
@login_required
def modi_es():
	if g.user['fk_rol']==1:
		dato=None
		
		return render_template('super/edit_estudiante.html',dato=dato)
	else:
		abort(403)
@bp.route('/modi_p')
@login_required
def modi_p():
	if g.user['fk_rol']==1:
		dato=None
		
		return render_template('super/edit_profesor.html',dato=dato)
	else:
		abort(403)

@bp.route('/<ncc>/elim_es', methods=['POST','GET'])
@login_required
def elim_es(ncc):
	if g.user['fk_rol']==1:
		
		if ncc== 0:
			dato=None
			print("Dato vacio")
			return render_template('super/edit_estudiante.html',dato=dato)
		else:
			print('NC es '+ncc)
			dato=None
			#SQL
			db, c=get_db()
			c.execute("CALL del_est(%s)",(ncc,))
			db.commit()
			return render_template('super/edit_estudiante.html',dato=dato)
		
		
		#{{ url_for('todo.elim_es',ncc=dato['nc']) }}
		return render_template('super/edit_estudiante.html',dato=dato)
	else:
		abort(403)
@bp.route('/bus_indiv_mod',methods=['GET','POST'])
@login_required
def bus_indiv_es_mod():
	if g.user['fk_rol']==1:
		if request.method=='POST':
			usu=request.form['usu']
			code=request.form['code']

			db, c=get_db()
			dato=None
			grupos=None
			
			
			

			if usu:
				c.execute("""SELECT e.nc,e.es_nom 'nom',e.es_apellidos 'app',u.username 'usu',g.gru_clave 'gc',c.titulo 'car',e.es_correo 'cor',e.es_generacion 'gg',e.visible 'visi'
				from estudiante e
				inner join user u on e.fkuser=u.user_id
				inner join grupo g on e.fkgrupo=g.gru_id
				inner join carrera c on g.fk_carrera=c.car_id
				where u.username=%s;
				""",(usu,))
				dato=c.fetchone()
				
				c.execute("SELECT gru_clave 'gv' from grupo")
				grupos=c.fetchall()

			

			if code:
				c.execute("""SELECT e.nc,e.es_nom 'nom',e.es_apellidos 'app',u.username 'usu',g.gru_clave 'gc',c.titulo 'car',e.es_correo 'cor'
				,e.es_generacion 'gg',e.visible 'visi'
				from estudiante e
				inner join user u on e.fkuser=u.user_id
				inner join grupo g on e.fkgrupo=g.gru_id
				inner join carrera c on g.fk_carrera=c.car_id
				where e.nc=%s;
				""",(code,))
				dato=c.fetchone()
				c.execute("SELECT gru_clave 'gv' from grupo")
				grupos=c.fetchall()
			
			if usu and code:
				c.execute("""SELECT e.nc,e.es_nom 'nom',e.es_apellidos 'app',u.username 'usu',g.gru_clave 'gc',c.titulo 'car',e.es_correo 'cor'
				,e.es_generacion 'gg',e.visible 'visi'
				from estudiante e
				inner join user u on e.fkuser=u.user_id
				inner join grupo g on e.fkgrupo=g.gru_id
				inner join carrera c on g.fk_carrera=c.car_id
				where e.nc=%s;
				""",(code,))
				dato=c.fetchone()
				c.execute("SELECT gru_clave 'gv' from grupo")
				grupos=c.fetchall()
				
				#passw=check_password_hash(user['password'],password)



			return render_template('super/edit_estudiante.html',dato=dato,grupos=grupos)
	else:
		abort(403)
@bp.route('/bus_mod_p',methods=['GET','POST'])
@login_required
def bus_mod_p():
	if g.user['fk_rol']==1:
		if request.method=='POST':
			
			code=request.form['code']

			
			dato=None
			if code:
				db, c=get_db()
				c.execute("""
					CALL bus_in_p(%s)
				""",(code,))
				dato=c.fetchone()
			else:
				flash("Debes de ingresar un dato")
			

			return render_template('super/edit_profesor.html',dato=dato)
	else:
		abort(403)
@bp.route('/bus_in_es')
@login_required
def bus_in_es():
	if g.user['fk_rol']==1:
		dato=None
		return render_template('super/bus_in_es.html',dato=dato)
	else:
		abort(403)	
@bp.route('/bus_in_p')
@login_required
def bus_in_p():
	if g.user['fk_rol']==1:
		dato=None
		return render_template('super/bus_in_prof.html',dato=dato)
	else:
		abort(403)	
@bp.route('/bus_indiv_es',methods=['GET','POST'])
@login_required
def bus_indiv_es():
	if g.user['fk_rol']==1:
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


			return render_template('super/bus_in_es.html',dato=dato)
	else:
		abort(403)
	

@bp.route('/bus_indiv_prof',methods=['GET','POST'])
@login_required
def bus_indiv_prof():
	if g.user['fk_rol']==1:
		if request.method=='POST':
			
			code=request.form['code']

			db, c=get_db()
			dato=None
	

			if code:
				c.execute("""
					CALL bus_in_p(%s)
				""",(code,))
				dato=c.fetchone()
			else:
				flash("Debes agregar un numero de control")
					 



			return render_template('super/bus_in_prof.html',dato=dato)
	else:
		abort(403)

@bp.route('/<gr>/new_act',methods=['GET','POST'])
@login_required
def nueva_actividad(gr):
	if g.user['fk_rol']==1 or g.user['fk_rol']==2:
		return render_template('profesor/new_actividad.html',gr=gr)
	else:
		abort(403)
	

@bp.route('/<int:acid>/<int:gc>/revision_ac_gru',methods=['GET','POST'])
@login_required
def revi_gru(acid,gc):
	if g.user['fk_rol']==1 or g.user['fk_rol']==2:
		if request.method=="POST":
			db, c=get_db()
			titulo=request.form['title']
			c.execute('CALL get_alum_ac(%s,%s)',(gc,acid))
			todo=c.fetchall()
			
			return render_template('profesor/rev_gru_actividades.html',tt=titulo,todo=todo,gc=gc,acid=acid)
	else:
		abort(403)


@bp.route('/<gc>/activ_pendientes',methods=['GET'])
@login_required
def rev_actividad(gc):
	#CALL get_Ac_grupo('rantoso',2);
	if g.user['fk_rol']==1 or g.user['fk_rol']==2:
		db,c=get_db()
		c.execute(
			"CALL get_Ac_grupo(%s,%s);",(g.user['username'],gc))
		activity=c.fetchall()
		#return render_template('todo/est_page.html',activity=activity)
		return render_template('profesor/rev_actividades.html',gc=gc,activity=activity)
	else:
		abort(403)

@bp.route('/added',methods=['POST'])
@login_required
def actividad_novo():
	if request.method=='POST':
		#intentar declarar el grupo de otra manera
		grupo=request.form['group']
		title=request.form['title']
		content=request.form['content']
		#if visible=request.form.get['visi']:
		if request.form.get('visi'):

			visible=1
		else:
			visible=0
		fEntrega=request.form['ffinal']
		
		db, c=get_db()
		
		c.execute('CALL alta_actividad(%s,%s,%s,%s,%s,%s)',(grupo,g.user['username'],title,content,fEntrega,visible))
		db.commit()
		#print("Fecha fEntrega ",fEntrega," Visible ",visible)

		flash("Se ha agregado la actividad",'info')
		return redirect(url_for('todo.prof_page'))

@bp.route('/anuncio_agregado',methods=['POST','GET'])
@login_required
def anuncio_agregado():
	if request.method=='POST':
		#intentar declarar el grupo de otra manera
		grupo=request.form['group']
		title=request.form['title']
		content=request.form['content']
		#if visible=request.form.get['visi']:
		if request.form.get('visi'):

			visible=1
		else:
			visible=0
		
		
		db, c=get_db()
								#(nt varchar(40), nd mediumtext, vis tinyint(1), gr varchar(7))
		c.execute('CALL new_anuncio(%s,%s,%s,%s)',(title,content,visible,grupo))
		db.commit()
		#print("Fecha fEntrega ",fEntrega," Visible ",visible)

		flash("Se ha agregado el anuncio",'info')
		return redirect(url_for('todo.new_anun'))

@bp.route('/<nc>/<int:acid>/rev_ind',methods=['POST'])
@login_required
def rev_ind(nc,acid):
	if request.method=='POST':
		#intentar declarar el grupo de otra manera
		
		db, c=get_db()
		
		c.execute('CALL getAct_ind(%s,%s)',(acid,nc))
		revision=c.fetchone()
		
		ruta=revision['ruta']
		print(ruta)

		return render_template('profesor/vis_cal_actividad.html',revision=revision,ruta=ruta)
@bp.route('/guia_pdf')
@login_required
def ver_guia_pdf():
	return render_template('estudiante/ver_guia.html')


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
			e.es_apellidos 'app',a.titulo 'titulo',a.descripcion,
            g.gru_clave 'gc',a.f_limite 'flim' 
			from es_ac ea
			inner join actividad a on ea.fk_ac=a.act_id
			inner join estudiante e on e.nc=ea.fk_es
			inner join user u on e.fkuser=u.user_id
			inner join grupo g on e.fkgrupo=g.gru_id
			where a.act_id=%s and u.username=%s;
			""",(acid,g.user['username']))
		ac=c.fetchone()
		currentDateTime = datetime.datetime.now()
					
		fsin = currentDateTime.date()
		fe=datetime.datetime(fsin.year, fsin.month, fsin.day)

		return render_template('estudiante/vis_ac_completa.html',ac=ac,form=form,fe=fe)


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

def crea_dir(anho,gru,nom,app,act):
	
	directorio = PurePath(Path.cwd(),'todo/static/files')
	print(directorio)
	Path(directorio).mkdir(exist_ok=True)
    
    #directorio = PurePath(Path.cwd(),'Archivos_PDF')
	#print(directorio)
	#Path(directorio).mkdir(exist_ok=True)

	directorio=PurePath(directorio,anho)
	print(directorio)
	Path(directorio).mkdir(exist_ok=True)

	directorio=PurePath(directorio,gru)
	print(directorio)
	Path(directorio).mkdir(exist_ok=True)

	directorio=PurePath(directorio,nom)
	print(directorio)
	Path(directorio).mkdir(exist_ok=True)

	directorio=PurePath(directorio,app)
	print(directorio)
	Path(directorio).mkdir(exist_ok=True)

	directorio=PurePath(directorio,act)
	print(directorio)
	Path(directorio).mkdir(exist_ok=True)

	return directorio
def crea_dir_docs(anho,user):
	
	directorio = PurePath(Path.cwd(),'todo/static/docs')
	print(directorio)
	Path(directorio).mkdir(exist_ok=True)


	directorio=PurePath(directorio,anho)
	print(directorio)
	Path(directorio).mkdir(exist_ok=True)

	
	directorio=PurePath(directorio,user)
	print(directorio)
	Path(directorio).mkdir(exist_ok=True)

	return directorio

class UploadForm(Form):
    file = FileField()
    submit = SubmitField("submit")
    download = SubmitField("download")