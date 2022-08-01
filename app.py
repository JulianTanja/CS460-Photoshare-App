######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

from email.mime import base
import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login
from datetime import datetime

#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Ziping22677*'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')

@app.route("/register2", methods=['GET'])
def register2():
	return render_template('register2.html')

@app.route("/friendslist", methods=['GET'])
@flask_login.login_required
def friendslist():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT U.first_name, U.last_name, U.email FROM Users U, (SELECT F.user_id2 FROM Users U, Friends F WHERE U.user_id = '{0}' AND U.user_id = F.user_id1) AS AllF WHERE U.user_id = AllF.user_id2".format(uid))
	conn.commit()
	return render_template('friendslist.html', names = cursor.fetchall())

@app.route("/album", methods=['GET'])
@flask_login.login_required
def browse():
	return render_template('album.html')

@app.route("/album", methods = ['POST'])
def createalbum():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	name = request.form.get('name')
	cursor = conn.cursor()
	date = datetime.now()
	cursor.execute("INSERT INTO Albums (name, date, user_id) VALUES ('{0}', '{1}', '{2}')".format(name, date, uid))
	conn.commit()
	return render_template('album.html')

@app.route("/browseA", methods=['GET'])
def browseA():
	cursor = conn.cursor()
	cursor.execute("SELECT A.name, A.date, A.albums_id FROM Albums A")
	conn.commit()
	return render_template('browseA.html', names = cursor.fetchall())

@app.route("/browseA", methods = ['POST'])
def selectA():
	try:
		term = request.form.get('name')
	except:
		print("couldn't find all tokens") 
		return flask.redirect(flask.url_for('browseA'))

	cursor = conn.cursor()
	cursor.execute("SELECT P.data, P.photo_id, P.caption FROM Photos P, Albums A WHERE A.albums_id = P.albums_id AND A.albums_id = '{0}'".format(term))
	cursor2 = conn.cursor()
	cursor2.execute("SELECT C.text, C.date, U.first_name FROM Comments C, Photos P, Users U, Albums A WHERE A.albums_id = P.albums_id AND A.albums_id = '{0}' AND P.photo_id = C.photo_id AND C.user_id = U.user_id".format(term))
	cursor3 = conn.cursor()
	cursor3.execute("SELECT COUNT(L.user_id) FROM LIKES L, Albums A, Photos P WHERE L.photo_id = P.photo_id AND A.albums_id = P.albums_id AND A.albums_id = '{0}' GROUP BY L.photo_id".format(term))
	return render_template('photoA.html', photos = cursor.fetchall(), base64=base64, comments = cursor2.fetchall(), likes = cursor3.fetchall(), album = term)

@app.route("/photoA", methods=['GET'])
def photoA():
	return render_template('photoA.html')

@app.route("/leaveComment/", methods=['POST'])
def leaveComment():
	try:
		comment = request.form.get('comment')
		photoid = request.form.get('id')
		term = request.form.get('albumid')
	except:
		print("couldn't find all tokens") 
	uid = getUserIdFromEmail(flask_login.current_user.id)
	date = datetime.now()
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Comments (user_id, photo_id, text, date) VALUES ('{0}', '{1}', '{2}', '{3}')".format(uid, photoid, comment, date))
	conn.commit()
	cursor4 = conn.cursor()
	cursor4.execute("SELECT P.data, P.photo_id, P.caption FROM Photos P, Albums A WHERE A.albums_id = P.albums_id AND A.albums_id = '{0}'".format(term))
	cursor2 = conn.cursor()
	cursor2.execute("SELECT C.text, C.date, U.first_name FROM Comments C, Photos P, Users U, Albums A WHERE A.albums_id = P.albums_id AND A.albums_id = '{0}' AND P.photo_id = C.photo_id AND C.user_id = U.user_id".format(term))
	cursor3 = conn.cursor()
	cursor3.execute("SELECT COUNT(L.user_id) FROM LIKES L, Albums A, Photos P WHERE L.photo_id = P.photo_id AND A.albums_id = P.albums_id AND A.albums_id = '{0}' GROUP BY L.photo_id".format(term))
	return render_template('photoA.html', photos = cursor4.fetchall(), base64=base64, comments = cursor2.fetchall(), likes = cursor3.fetchall(), album = term)

@app.route("/likePhoto/", methods=['POST'])
def likePhoto():
	try:
		photoid = request.form.get('id')
		term = request.form.get('albumid')
	except:
		print("cound't find all tokens")
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Likes (photo_id, user_id) VALUES ('{0}', '{1}')".format(photoid, uid))
	conn.commit()
	cursor4 = conn.cursor()
	cursor4.execute("SELECT P.data, P.photo_id, P.caption FROM Photos P, Albums A WHERE A.albums_id = P.albums_id AND A.albums_id = '{0}'".format(term))
	cursor2 = conn.cursor()
	cursor2.execute("SELECT C.text, C.date, U.first_name FROM Comments C, Photos P, Users U, Albums A WHERE A.albums_id = P.albums_id AND A.albums_id = '{0}' AND P.photo_id = C.photo_id AND C.user_id = U.user_id".format(term))
	cursor3 = conn.cursor()
	cursor3.execute("SELECT COUNT(L.user_id) FROM LIKES L, Albums A, Photos P WHERE L.photo_id = P.photo_id AND A.albums_id = P.albums_id AND A.albums_id = '{0}' GROUP BY L.photo_id".format(term))
	return render_template('photoA.html', photos = cursor4.fetchall(), base64=base64, comments = cursor2.fetchall(), likes = cursor3.fetchall(), album = term)

@app.route("/userA", methods=['GET'])
@flask_login.login_required
def userA():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT A.albums_id, A.name, A.date FROM Albums A WHERE A.user_id = '{0}'".format(uid))
	conn.commit()
	return render_template('userA.html', names = cursor.fetchall())

@app.route("/userA", methods = ['POST'])
def selectuserA():
	try:
		name = request.form.get('name')
	except:
		print("couldn't find all tokens") 
		return flask.redirect(flask.url_for('userA'))
	cursor = conn.cursor()
	cursor.execute("SELECT P.data, P.photo_id, P.caption FROM Photos P, Albums A WHERE A.albums_id = P.albums_id AND A.albums_id = '{0}'".format(name))
	conn.commit()
	return render_template('userP.html', photos = cursor.fetchall(), base64=base64)

@app.route("/deleteAlbum/", methods = ['POST'])
def deleteAlbum():
	name = request.form.get('id')
	cursor = conn.cursor()
	cursor.execute('''DELETE FROM Albums WHERE albums_id = %s''',(name))
	conn.commit()
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT A.albums_id, A.name, A.date FROM Albums A WHERE A.user_id = '{0}'".format(uid))
	conn.commit()
	return render_template('userA.html', names = cursor.fetchall())

@app.route("/userP", methods=['GET'])
@flask_login.login_required
def userP():
	return render_template('userP.html')

@app.route("/deletePhoto/", methods = ['POST'])
def deletePhoto():
	name = request.form.get('id')
	cursor = conn.cursor()
	cursor.execute('''DELETE FROM Photos WHERE photo_id = %s''',(name))
	conn.commit()
	return render_template('userP.html')

@app.route("/searchC", methods=['GET'])
@flask_login.login_required
def searchC():
	return render_template('searchC.html')

@app.route("/searchC", methods = ['POST'])
def searchComment():
	comment = request.form.get('comment')
	cursor = conn.cursor()
	cursor.execute("SELECT U.first_name, U.last_name, U.email, C.text, COUNT(*) AS idcount FROM Users U, Comments C WHERE C.text REGEXP '{0}' AND C.user_id = U.user_id GROUP BY U.user_id ORDER BY idcount DESC".format(comment))
	conn.commit()
	return render_template('searchC.html', ret = cursor.fetchall())

@app.route("/recommendation", methods=['GET'])
@flask_login.login_required
def recommendation():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT U.first_name, U.last_name, U.email, COUNT(*) AS idcount FROM Friends F1, Friends F2, Users U WHERE F1.user_id1 = '{0}' AND F1.user_id2 = F2.user_id1 AND F2.user_id2 = U.user_id GROUP BY U.user_id ORDER BY idcount DESC".format(uid))
	return render_template('recommendation.html', ret = cursor.fetchall())

@app.route("/topusers", methods=['GET'])
def topusers():
	cursor = conn.cursor()
	cursor.execute("SELECT U.first_name, U.last_name, U.email, COUNT(*) AS countall FROM Users U, Comments C, Photos P WHERE U.user_id = C.user_id AND C.user_id = P.user_id GROUP BY U.user_id ORDER BY countall DESC LIMIT 10")
	return render_template('topusers.html', ret = cursor.fetchall())

@app.route("/createtag", methods=['GET'])
@flask_login.login_required
def tag():
	return render_template('createtag.html')

@app.route("/createtag", methods=['POST'])
def createtag():
	try:
		name = request.form.get('name')
	except:
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('createtag'))
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Tags (name) VALUES ('{0}')".format(name))
	conn.commit()
	return render_template('createtag.html')

@app.route("/tagphoto", methods=['GET'])
@flask_login.login_required
def tagaphoto():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT T.name, T.tag_id FROM Tags T")
	return render_template('tagphoto.html', photos=getUsersPhotos(uid), tags = cursor.fetchall(),base64=base64)

@app.route("/tagphoto", methods=['POST'])
def tagphoto():
	try:
		tagid = request.form.get('tagid')
		photoid = request.form.get('photoid')
	except:
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('tagphoto'))
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Tagged (tag_id, photo_id) VALUES ('{0}', '{1}')".format(tagid, photoid))
	conn.commit()

	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor2 = conn.cursor()
	cursor2.execute("SELECT T.name, T.tag_id FROM Tags T")
	return render_template('tagphoto.html', photos=getUsersPhotos(uid), tags = cursor2.fetchall(),base64=base64)

@app.route("/viewtagged", methods=['GET'])
@flask_login.login_required
def viewtagged():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT T.name, T.tag_id FROM Tags T")
	return render_template('viewtagged.html', tags = cursor.fetchall())

@app.route("/viewtaggedU", methods=['POST'])
@flask_login.login_required
def viewtaggedU():
	tagid = request.form.get('tagid')
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT P.data, P.photo_id, P.caption FROM Photos P, Tagged T WHERE P.photo_id = T.photo_id AND T.tag_id = '{1}' AND P.user_id = '{0}'".format(uid, tagid))
	return render_template('viewtaggedU.html', photos = cursor.fetchall(), tid = tagid, base64 = base64)

@app.route("/viewtaggedE", methods=['POST'])
@flask_login.login_required
def viewtaggedE():
	tagid = request.form.get('tagid')
	cursor = conn.cursor()
	cursor.execute("SELECT P.data, P.photo_id, P.caption FROM Photos P, Tagged T WHERE P.photo_id = T.photo_id AND T.tag_id = '{0}'".format(tagid))
	return render_template('viewtaggedE.html', photos = cursor.fetchall(), base64=base64, tid = tagid)

@app.route("/populartags", methods=['GET'])
@flask_login.login_required
def populartags():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT Ts.name, Ts.tag_id, COUNT(*) AS counted FROM Tagged T, Tags Ts WHERE T.tag_id = Ts.tag_id GROUP BY T.tag_id ORDER BY counted DESC")
	return render_template('populartags.html', tags = cursor.fetchall())

@app.route("/searchbytag", methods=['GET'])
@flask_login.login_required
def searchbytag():
		return render_template('searchbytag.html')

@app.route("/searchbytag", methods = ['POST'])
def searchtag():
	tag = request.form.get('tag')
	cursor = conn.cursor()
	cursor.execute("SELECT P.data, P.photo_id, P.caption FROM Photos P, Tagged T, Tags Ts WHERE Ts.name REGEXP '{0}' AND Ts.tag_id = T.tag_id AND P.photo_id = T.photo_id".format(tag))
	conn.commit()
	return render_template('searchbytag.html', photos = cursor.fetchall(), base64 = base64)




@app.route("/search", methods=['GET'])
@flask_login.login_required
def search():
	return render_template('search.html')

@app.route("/search", methods = ['POST'])
def search_users():
	try:
		term = request.form.get('search')
	except:
		print("couldn't find all tokens") 
		return flask.redirect(flask.url_for('search'))
	cursor = conn.cursor()
	cursor.execute("SELECT U.first_name, U.last_name, U.email, U.user_id FROM Users U WHERE U.email REGEXP '{0}'".format(term))
	conn.commit()
	return render_template('search.html', names = cursor.fetchall())

@app.route("/addfriend/", methods = ['POST'])
def addfriend():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	otherid = request.form.get('id')
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Friends (user_id1, user_id2) VALUES ('{0}', '{1}')".format(uid, otherid))
	conn.commit()
	return render_template('search.html', names = cursor.fetchall())

@app.route("/register", methods=['POST'])
def register_user():
	try:
		firstname=request.form.get('firstname')
		lastname=request.form.get('lastname')
		birthday=request.form.get('birthday')
		email=request.form.get('email')
		password=request.form.get('password')
		hometown=request.form.get('hometown')
		gender=request.form.get('gender')
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test = isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO Users (first_name, last_name, email, birth_date, hometown, gender, password) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(firstname, lastname, email, birthday, hometown, gender, password)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else:
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('register2'))

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT data, photo_id, caption FROM Photos WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]	

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

@app.route('/profile')
@flask_login.login_required
def protected():
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile")

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		albumid = request.form.get('album')
		photo_data =imgfile.read()
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Photos (caption, data, albums_id, user_id) VALUES (%s, %s, %s, %s)''', (caption, photo_data, albumid, uid))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid),base64=base64)
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		cursor = conn.cursor()
		cursor.execute("SELECT A.albums_id, A.name, A.date FROM Albums A WHERE A.user_id = '{0}'".format(uid))
		conn.commit()
		return render_template('upload.html', names = cursor.fetchall())
#end photo uploading code


#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welcome to Photoshare')


if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
