import os
#import mysql.connector

from flask import Flask

def create_app():
	app=Flask(__name__)
	#app.run(host="localhost", port=3306, debug=True)
	app.config.from_mapping(
			SECRET_KEY="llavesita",
			DATABASE_HOST=os.environ.get("FLASK_DATABASE_HOST"),
			DATABASE_PASSWORD=os.environ.get("FLASK_DATABASE_PASSWORD"),
			DATABASE_USER=os.environ.get("FLASK_DATABASE_USER"),
			DATABASE=os.environ.get("FLASK_DATABASE")
		#	UPLOAD_FOLDER=os.environ.get("UPLOAD_FOLDER")
		#	PUERTO=os.environ.get("FLASK_RUN_PORT")			
	)
	#app.config['UPLOAD_FOLDER'] = './Archivos PDF'


	from . import db
	db.init_app(app)

	from . import auth 
	from . import todo 
	app.register_blueprint(auth.bp)
	app.register_blueprint(todo.bp)
	@app.route('/hola')
	def hola():
		return "Chacho felizx"
	return app

