
# https://getbootstrap.com/docs/4.0/components/list-group/
# <link href="http://getbootstrap.com/examples/jumbotron-narrow/jumbotron-narrow.css" rel="stylesheet">

#imports
#from flask import Flask, render_template, json, request, session, redirect, flash
from flask import *
from flask import Flask
#import Flask, render_template, json, request, session, redirect, flash
#import urllib.request
import os
#from werkzeug import generate_password_hash, check_passwordvi appl_hash
#from flask.ext.mysql import MySQL
import sqlite3
from dbp import Database
#from werkzeug.utils import secure_filename
from  datetime import datetime,date,timedelta
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
from openTool import OpenTool
from flask import Flask, render_template, request, session, redirect, url_for
from webscr import Webscr # Assuming Webscr is in a file like 'scraper.py'




ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




#initialize the flask and SQL Objects
application = Flask(__name__)

#initializa secret key
application.secret_key='This is my secret key'

#configure MYSQL
application.config['MYSQL_DATABASE_USER'] = 'Arjun'
application.config['MYSQL_DATABASE_PASSWORD'] = '1377Hello!'
application.config['MYSQL_DATABASE_DB'] = 'BucketList'
application.config['MYSQL_DATABASE_HOST'] = 'localhost'
#mysql.init_application(application)
UPLOAD_FOLDER = 'c:/uploads'
application.secret_key = "secret key"
application.config['UPLOAD_FOLDER']= UPLOAD_FOLDER
application.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


# you can set key as config
application.config['GOOGLEMAPS_KEY'] = "AIzaSyDbsmr0HAnaDppyq7o1FOqrzNM9D1pbBCE"

# Initialize the extension
GoogleMaps(application)

#GoogleMaps1(application, key="8JZ7i18MjFuM35dJHq70n3Hx4")


#helper function
def check_password(acc_pass, provided_pass):
	#provided_pass = generate_password_hash(provided_pass)
	if provided_pass==acc_pass:
		return True
	return False
	
@application.route("/map")
def mapview():
    # creating a map in the view
    mymap = Map(
        identifier="view-side",
        lat=37.4419,
        lng=-122.1419,
        markers=[(37.4419, -122.1419)]
    )
    sndmap = Map(
        identifier="sndmap",
        lat=37.4419,
        lng=-122.1419,
        markers=[
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
             'lat': 37.4419,
             'lng': -122.1419,
             'infobox': "<b>Hello World</b>"
          },
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
             'lat': 37.4300,
             'lng': -122.1400,
             'infobox': "<b>Hello World from other place</b>"
          }
        ]
    )
    return render_template('example.html', mymap=mymap, sndmap=sndmap)

#define methods for routes (what to do and display)
@application.route("/")
def main():
	return render_template('index.html')

@application.route("/main")
def return_main():
	return render_template('index.html')

@application.route('/showSignUp')
def showSignUp():
	return render_template('signup.html')

@application.route('/showSignIn')
def showSignIn():
	return render_template('signin.html')

@application.route('/wishlist')
def wishlist():
	return render_template('wishlist.html')

@application.route('/genData')
def genData():
	return render_template('genData.html')

@application.route('/nadData')
def nadData():
    return render_template('nadData.html')

@application.route('/userHome')
def showUserHome():
	#check that someone has logged in correctly
	if session.get("user"):
		return render_template('userHome.html', username=session.get("user")[1])
	else:
		return render_template('error.html', error = "Invalid User Credentials")

@application.route('/logout')
def logout():
	session.pop('user', None)
	return redirect('/')


@application.route('/validateLogin', methods=['POST'])
def validate():
	try:
		_username = request.form['inputEmail']
		_password = request.form['inputPassword']
		print("Username:", _username, "\n Password:", _password)

		#create MySQL Connection
		#conn = mysql.connect()
		db=Database('BucketList.db')

		#create a cursor to query the stored procedure
		#conn = sqlite3.connect(db)
		#cursor = conn.cursor()
		print("successfully connected to mysql!")

		#get users with this username (should only be one)
		#cursor.callproc('sp_validateLogin', (_username,))
		users = db.fetchUser(_username)  #cursor.fetchall()
		print("called process")
		#acctually validate these users
	
		if len(users)>0:
			if check_password(users[0][3], _password):
				session['user']=users[0]
				return redirect('/userHome')
			else:
				return render_template('error.html', error="incorrect username or password")
		else:
			return render_template('error.html', error= "incorrect username or password")

	except Exception as ex:
		print("Error getting username and password, Error:", ex)
		return render_template('error.html', error = 'Missing Email Adress or Password')

	#finally:
		#disconnect from mysql database
		#cursor.close()
		#conn.close()

@application.route('/signUp', methods=['POST'])
def signUp():
	"""
	method to deal with creating a new user in the MySQL Database
	"""
	print("signing up user...")
	#create MySQL Connection
	db=Database('BucketList.db')
	#conn = sqlite3.connect(db)
	#create a cursor to query the stored procedure
	#cursor = conn.cursor()

	try:
		#read in values from frontend
		_name = request.form['inputName']
		_email = request.form['inputEmail']
		_password = request.form['inputPassword']

		#Make sure we got all the values
		if _name and _email and _password:
			print("Email:", _email, "\n", "Name:", _name, "\n", "Password:", _password)
			#hash passowrd for security
			_hashed_password = 'TESTHASH' #generate_password_hash(_password)
			print("Hashed Password:", _hashed_password)

			#call jQuery to make a POST request to the DB with the info
			#cursor.callproc('sp_createUser', (_name, _email, _password))
			db.insert(_name, _email, _password)
			print("Successfully called sp_createUser")
			#check if the POST request was successful
			data = db.fetchUser(_email)
			numberdata=len(data)
			if numberdata!=0:
			#	conn.commit()
				print('signup successful!')
				return 'User created successfuly!'+str(data[numberdata-1])
			else:
				print('error')
				return str(data[numberdata-1])

		else:
			print('fields not submitted')
			return 'Enter the required fields'

	except Exception as ex:
		print('got an exception: ', ex)
		return json.dumps({'error':str(ex)})

	finally:
		print('ending...')
#		cursor.close()
#		conn.close()

@application.route('/addWish',methods=['POST'])
def addWish():
	print("in addWIsh")
	db=Database('BucketList.db')
	try:
		if session.get('user'):
			_projname = request.form['inputTitle']
			_projdescription = request.form['inputDescription']
			_probundle = request.form['inputBundle']
			_user = session.get('user')[2]
			print("Project Name:",_projname,"\n Project description:",_projdescription,"\n user:",_user,"\n Bundle:",_probundle)
		#    conn = sqlite3.connect(db)
		#    cursor = conn.cursor()
		   # cursor.callproc('sp_addWish',(_title,_description,_user))
		   # data = cursor.fetchall()
			db.insertProject(_projname,_projdescription,_probundle,_user)
			data = db.fetchUserSpecificProject(_user,_projname)
			numberdata=len(data)
			if numberdata!=0:
				#conn.commit()
				print("finished executing addWish")
				return redirect('/userHome')
			else:
				return render_template('error.html',error = 'An error occurred!')
 
		else:
			return render_template('error.html',error = 'Unauthorized Access')
	except Exception as e:
		print("in exception for AddWish")
		return render_template('error.html',error = str(e))

@application.route('/addGen',methods=['POST'])
def addGen():
	print("in addGen")
	try:
			_projdescription = request.form['inputDescription']
			_user = session.get('user')[2]
			print(" Project description:",_projdescription,"\n user:",_user)
			# check if the post request has the files part
			if 'files[]' not in request.files:
				flash('No file part')
				return redirect(request.url)
			files = request.files.getlist('files[]')
			for file in files:
				if file and allowed_file(file.filename):
					#filename =  str(datetime.datetime.now().microsecond)+'_'+str(_projdId)+'_'+str(_taskDefId)+'_'+secure_filename(file.filename)
					filename =  str(datetime.now().microsecond)+'_'+file.filename
					file.save(os.path.join(application.config['UPLOAD_FOLDER'],filename))
			flash('File(s) successfully uploaded')
			
			inst1=OpenTool()
			print("this is the desc: \n",_projdescription)
			rep= inst1.raiseQuestion("./ds-files",_projdescription)
			print ("The response is:\n",rep)
			return render_template('genData.html',error = str(rep))
		
	except Exception as e:
		print("in exception for addGen")
		return render_template('error.html',error = str(e))

@application.route('/addNad',methods=['POST'])
def addNad():
	print("in addNad")
	try:
			_inputGush = request.form['inputGush']
			_inputHalka = request.form['inputHalka']
			# Define gush and chelka IDs (you might want to get these from a form submission or database)
			# For now, using hardcoded values as in your scraper example
			i_gush = "6631"
			i_chelka = "215"
			url = "https://www.nadlan.gov.il/?view=kparcel_all&id=" + _inputGush + "-" + _inputHalka + "&page=deals"

			# Create an instance of the Webscr class
			webinc = Webscr(url)
			
			# Call webExe to scrape data
			# Limit max_pages_to_scrape for quick testing, e.g., 2-3 pages
			scraped_results = webinc.webExe(max_pages_to_scrape=3) 

			# Pass the scraped_results to the HTML template
			return render_template('nadData.html', scraped_results=scraped_results)
	except Exception as e:
		print("in exception for addNad")
		return render_template('error.html',error = str(e))

@application.route('/addTask',methods=['POST'])

def addTask():
	print("in addTask")
	if request.method == 'POST':
		_projdId =session.get('ProjectId')
		_taskDefId =session.get('taskDef_id')
		print("in addTask2:",_projdId,_taskDefId)
			# check if the post request has the files part
		if 'files[]' not in request.files:
			flash('No file part')
			return redirect(request.url)
		files = request.files.getlist('files[]')
		for file in files:
			if file and allowed_file(file.filename):
				#filename =  str(datetime.datetime.now().microsecond)+'_'+str(_projdId)+'_'+str(_taskDefId)+'_'+secure_filename(file.filename)
				filename =  str(datetime.now().microsecond)+'_'+str(_projdId)+'_'+str(_taskDefId)+'_'+file.filename
				file.save(os.path.join(application.config['UPLOAD_FOLDER'],filename))
		flash('File(s) successfully uploaded')
	print("in addTask4:")
	db=Database('BucketList.db')
	print("in addTask5:")
	try:
		if session.get('user'):
			print("Test")
			_taskName = request.form['inputTaskName']
			_taskDesc = request.form['inputTaskDesc']
			_taskDone = request.form['inputTaskDone']
			print("in addTask3:",_taskName,_taskDesc,_taskDone)
			_user = session.get('user')[2]
			_projdId =session.get('ProjectId')
			_taskDefId =session.get('taskDef_id')
			_taskId = session.get('task_id')
			if _taskDone != 'on':
				_taskDone='off'
			print("_taskDefId:",_taskDefId,"_taskName:",_taskName,"_taskDesc:",_taskDesc," _projdId:",_projdId,"Task_id:",_taskId,"Task_Done:",_taskDone)
			if _taskDefId !='':
				db.insertTask(_taskDefId,_projdId,_taskName,_taskDesc,_taskDone)
			else:
				db.updateTask(_projdId,_taskId,_taskName,_taskDesc,_taskDone)
			#data = db.fetchProjSpecificTask(_taskDefId,_projdId)
			#numberdata=len(data)
			#if numberdata!=0:
				#conn.commit()
			print("finished executing addTask")
			return redirect('/userHome')
			#else:
				#return render_template('error.html',error = 'An error occurred!')
 
		else:
			return render_template('error.html',error = 'Unauthorized Access')
	except Exception as e:
		print("in exception for addTask")
		return render_template('error.html',error = str(e))

@application.route('/upload')
def upload_form():
	return render_template('upload.html')

@application.route('/upload', methods=['POST'])
def upload_file1():
	if request.method == 'POST':
		# check if the post request has the files part
		if 'files[]' not in request.files:
			flash('No file part')
			return redirect(request.url)
		files = request.files.getlist('files[]')
		for file in files:
			if file and allowed_file(file.filename):
				#filename = secure_filename(file.filename)
				file.save(os.path.join(application.config['UPLOAD_FOLDER'], file.filename))
		flash('File(s) successfully uploaded')
		return redirect('/')
	#finally:
	#    cursor.close()
	#    conn.close()

@application.route('/getWish')
def getWish():
	print("in getWish")
	db=Database('BucketList.db')
	try:
		if session.get('user'):
			_user = session.get('user')[2]
			print(_user)
			wishes=db.fetchProjects(_user)
			print(_user,wishes.count)
			wishes_dict = []
			for wish in wishes:
				wish_dict = {
						'Id': wish[0],
						'Project_Name': wish[1],
						'Project_Description': wish[2],
						'Project_User': wish[4],
						'Project_Date': wish[5]}
				wishes_dict.append(wish_dict)
			return json.dumps(wishes_dict)
		else:
			return render_template('error.html', error = 'Unauthorized Access')

	except Exception as e:
		return render_template('error.html', error = str(e))

	finally:
		print("Finally")
		#cursor.close()
		#Oren TEST conn.close()

@application.route('/getProjTask/<int:proj_id>')
def getProjTask(proj_id):
	print('ProjId:',proj_id)
	session['ProjectId']=proj_id
	return render_template('projTasks.html', username=session.get("user")[1])

@application.route('/createTask/<int:taskDef_id>/<int:proj_id>')
def createTask(proj_id,taskDef_id):
	print('ProjId:',proj_id,'TaskDefId:',taskDef_id)
	session['ProjectId']=proj_id
	session['taskDef_id']=taskDef_id
	return render_template('newTask.html',username=session.get("user")[1])

@application.route('/displayTask/<int:proj_id>/<int:task_id>/<task_name>/<task_desc>')
def displayTask(proj_id,task_id,task_name,task_desc):
	print('ProjId:',proj_id,'TaskId:',task_id,'TaskName:',task_name,'Task_Desc:',task_desc)
	session['ProjectId']=proj_id
	session['taskDef_id']=''
	session['task_id']=task_id
	return render_template('newTask.html',username=session.get("user")[1],task_name=task_name,task_desc=task_desc)

@application.route('/displayTask/<int:proj_id>/<int:task_id>')
def displayTaskwithout(proj_id,task_id):
	print('ProjId:',proj_id,'TaskId:',task_id)
	session['ProjectId']=proj_id
	session['taskDef_id']=''
	session['task_id']=task_id
	return render_template('newTask.html',username=session.get("user")[1])

@application.route('/getTask')
def getTask():
	print("in getTask")
	db=Database('BucketList.db')
	_user = session.get('user')[2]
	_userProj =  session.get('ProjectId')
	datenow = datetime.today()
	try:
		if _user:
			if _userProj:
				print(_user)
				print(_userProj)
				wishes=db.fetchProjectTasks(_user,_userProj)
				print(_user,wishes.count)
				wishes_dict = []
				for wish in wishes:
					print('in loop')
					print('in loop11',wish[0],wish[1],wish[2],wish[3])
					tasks=db.fetchTasksforTaskDef(wish[0],_userProj)
					wish_dict = {
						'Task_Def_Id': wish[0],
						'Task_Def_Name': wish[1],
						'Task_Def_Description': wish[2],
						'Task_Def_SLA': wish[3],
						'Task_Proj': _userProj}
					wishes_dict.append(wish_dict)
					for task in tasks:
						print('in Task loop')
						print('in loop Task',task[2],task[3],task[4],task[5],task[6])
#						datecust = datetime.date(task[5])
						print ('Print Date:',task[5],' ',datenow)
						if (datenow > task[6]+ timedelta(days=wish[3])):
							print('\n  Date name is greater ')
							passedDue= 'TRUE'
						else:
							print('\n  Date name is smaller ')
							passedDue= 'FALSE'


						task_dict = {
							'Task_Id': task[2],
							'Task_Name': task[3],
							'Task_Description': task[4],
							'Task_Proj': _userProj,
							'Task_Done':task[5],
							'Task_Creation_Date':task[6],
							'Task_Passed_Due':passedDue
							}
						wishes_dict.append(task_dict)
				print('This is last Tasks print:',wishes_dict)
				return json.dumps(wishes_dict)
			else:
				return render_template('error.html', error = 'Unauthorized Access - for User Project')
		else:
			return render_template('error.html', error = 'Unauthorized Access')

	except Exception as e:
		return render_template('error.html', error = str(e))

	finally:
		print("Finally")
		#cursor.close()
		#Oren TEST conn.close()



if __name__ == "__main__":
	application.run()
