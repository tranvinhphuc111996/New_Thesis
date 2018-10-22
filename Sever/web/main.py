# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, render_template, session, redirect, escape
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import sqlite3
from flask_socketio import SocketIO, emit
DATABASE_FILE = 'database.db'
app = Flask(__name__, static_url_path='/static')
app.secret_key = os.urandom(12)
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = './static/image'
socketio = SocketIO( app, async_mode=None)
def connectdb():
	conn = sqlite3.connect(DATABASE_FILE, isolation_level = None)
	return conn

def querydb(conn, query, v = tuple()):
	c = conn.cursor()
	c.execute(query, v)
	return c.fetchall()

def logged_in():
	if not session.get('logged_in'):
		return 0
	return 1

@app.route('/')
def index():
	if logged_in():
		return render_template('index.html')
	else:
		return redirect('/dang_nhap')

@app.route('/dang_nhap', methods=['GET', 'POST'])
def dang_nhap():
	if request.method == 'GET':
		return render_template('dang_nhap.html')
	else:
		username = request.form.get('username')
		password = request.form.get('password')

		conn = connectdb()
		r = querydb(conn, r"SELECT * FROM Administrator WHERE username=? AND password=?", (username, password))
		if r:
			session['logged_in'] = True
			return redirect('/')
		else:
			return render_template('dang_nhap.html')


@app.route('/dang_xuat')
def dang_xuat():
	session.clear()
	return redirect('/dang_nhap') 

@app.route('/static/<filename>')
def static_file(filename):
	return app.send_static_file(filename)

@app.route('/thong_ke')
def thong_ke():
	if not logged_in():
		return redirect('/dang_nhap')
	return render_template('/thong_ke.html')


@app.route('/json/scan_the', methods=['POST'])
def scan_the():
	'''Lay CardID'''
	json_post_data 	= request.get_json()
	CardID 			= json_post_data['CardID']
	DeviceID 		= json_post_data['DeviceID']
	FingerID		= json_post_data['FingerID']
	ImageID			= json_post_data['ImageID']


	'''Debug'''

	print 'CardID:', CardID
	socketio.emit('my_response', json_post_data , namespace='/tracking')
	conn = connectdb()
	r = querydb(conn, r"SELECT * FROM Employee WHERE CardID=?", (CardID, ))
	if len(r) > 0:
		'''User da dang ky'''
		r = {'status': 1}
		print r
		'''Ghi record vao bang Work'''
		querydb(conn, r"INSERT INTO Work(DeviceID,CardID,FingerID,ImageID,EntryTime) VALUES (?,?,?,?, DATE('now'))", (DeviceID,CardID,FingerID,ImageID, ))
	else:
		'''User chua dang ky'''
		r = {'status': 0}
		print r
		'''Ghi record vao bang UnRegistered'''
		try:
			querydb(conn, r"INSERT INTO UnRegistered(CardID) VALUES (?)", (CardID, ))
		except:
			pass
	conn.commit()
	conn.close()
	return jsonify(r)



@app.route('/Tracking', methods=['POST', 'GET'])
def tracking():
	return render_template('Tracking.html')




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/rev_image', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return 'Success'
    return 'Success'



@app.route('/the_moi', methods=['POST', 'GET'])
def the_moi():
	#not implemented
	if not logged_in():
		return redirect('/dang_nhap')
	if request.method == 'GET':
		return render_template('the_moi.html')
	else:
		post_data 			= request.form
		'''TODO
		kiểm tra mã thẻ hợp lệ
		'''
		CardID 				= post_data['mathe'] 
		EmployeeName 		= escape(post_data['hoten'])
		EmployeeBirthDate 	= datetime.strptime(post_data['ngaysinh'], '%d-%m-%Y')
		conn 				= connectdb()
		r 					= querydb(conn, r"INSERT INTO Employee(EmployeeName, CardID, EmployeeBirthDate) VALUES(?,?,?)", (EmployeeName, CardID, EmployeeBirthDate))
		return render_template('the_moi.html')
@socketio.on('Ping')
def handle_ping(msg):
	print('Ping !!!' + str(msg.data))
@app.route('/them_nhan_vien', methods=['POST', 'GET'])
def them_nhan_vien():
	if not logged_in():
		return redirect('/dang_nhap')

	if request.method == 'GET':
		return render_template('them_nhan_vien.html')
	else:
		post_data 			= request.form
		'''TODO
		kiểm tra mã thẻ hợp lệ
		'''
		CardID 				= post_data['mathe'] 
		EmployeeName 		= escape(post_data['hoten'])
		EmployeeBirthDate 	= datetime.strptime(post_data['ngaysinh'], '%d-%m-%Y')
		conn 				= connectdb()
		r 					= querydb(conn, r"INSERT INTO Employee(EmployeeName, CardID, EmployeeBirthDate) VALUES(?,?,?)", (EmployeeName, CardID, EmployeeBirthDate))
		return render_template('them_nhan_vien.html')

@app.route('/json/xoa_nhan_vien', methods=['POST'])
def xoa_nhan_vien():
	if not logged_in():
		return redirect('/dang_nhap')

	json_post_data 		= request.get_json()
	CardID 				= json_post_data['mathe']
	conn 				= connectdb()
	r 					= querydb(conn, r"DELETE FROM Employee WHERE CardID=?", (CardID,))
	return jsonify({'status': 1})

@app.route('/json/sua_thong_tin_nhan_vien', methods=['POST'])
def sua_thong_tin_nhan_vien():
	if not logged_in():
		return redirect('/dang_nhap')

	json_post_data 		= request.get_json()
	CardID 				= json_post_data['mathe'] 
	EmployeeName 		= escape(json_post_data['hoten'])
	EmployeeBirthDate 	= datetime.strptime(json_post_data['ngaysinh'], '%d-%m-%Y')
	conn 				= connectdb()
	r 					= querydb(conn, r"UPDATE Employee SET EmployeeName=?,EmployeeBirthDate=? WHERE CardID=?", (EmployeeName, EmployeeBirthDate, CardID))
	return jsonify({'status': 1})

@app.route('/them_thiet_bi', methods=['POST', 'GET'])
def them_thiet_bi():
	if not logged_in():
		return redirect('/dang_nhap')

	if request.method == 'GET':
		return render_template('them_thiet_bi.html')
	else:
		post_data 	= request.form
		DeviceID  	= post_data['deviceid']
		description = escape(post_data['description'])
		conn 		= connectdb()
		r 			= querydb(conn, r"INSERT INTO Device(DeviceID, Description) VALUES(?,?)", (DeviceID, description))
		return render_template('them_thiet_bi.html')

@app.route('/danh_sach_nhan_vien', methods=['GET'])
def danh_sach_nhan_vien():
	if not logged_in():
		return redirect('/dang_nhap')
	'''connect to database'''
	conn 			= connectdb()
	r 				= querydb(conn, r"SELECT EmployeeName, CardID, strftime('%d-%m-%Y', EmployeeBirthDate) FROM Employee")
	ds_nhanvien 	= []
	for row in r:
		ds_nhanvien.append({'hoten': row[0], 'mathe': row[1], 'ngaysinh': row[2]})
	return render_template('danh_sach_nhan_vien.html', ds_nhanvien=ds_nhanvien)

@app.route('/danh_sach_thiet_bi')
def danh_sach_thiet_bi():
	if not logged_in():
		return redirect('/dang_nhap')

	'''connect to database'''
	conn 			= connectdb()
	r 				= querydb(conn, r"SELECT * FROM Device")
	ds_thietbi 		= []
	for row in r:
		ds_thietbi.append({'deviceid': row[0], 'description': row[1]})
	return render_template('danh_sach_thiet_bi.html', ds_thietbi=ds_thietbi)
@app.route('/danh_sach_tag_ID')
def danh_sach_tag_ID():
	return render_template('danh_sach_tag_ID.html')

