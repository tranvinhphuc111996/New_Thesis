from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import urlparse
import sqlite3
import cgi

DATABASE_FILE = 'database.db'

def connectdb():
	conn = sqlite3.connect(DATABASE_FILE, isolation_level = None)
	return conn

def querydb(conn, query, v = tuple()):
	c = conn.cursor()
	c.execute(query, v)
	return c.fetchall()

class GetHandler(BaseHTTPRequestHandler):
	'''Helper funcitons'''
	def r(self, length):
		return self.rfile.read(length)

	def w(self, d):
		return self.wfile.write(d)

	def status404(self):
		self.send_response(404)
		self.end_headers()

	def response(self, data):
		self.send_response(200)
		self.send_header('content-length', len(data))
		self.end_headers()
		self.w(data)

	'''Them nhan vien moi'''
	def add_employee_get_handler(self):
		conn = connectdb()
		r = querydb(conn, r"SELECT * FROM UnRegistered")

		response_data = 'UnRegistered CardID:\n'
		print r
		if len(r) > 0:
			for row in r:
				response_data += row[0] + '\n'
		else:
			response_data = 'There is no UnRegistered card'
		self.response(response_data)

	'''list all employees'''
	def statistic_get_handler(self):
		'''connect to database'''
		conn = connectdb()
		r = querydb(conn, r"SELECT * FROM Employee")

		response_data = ''
		for row in r:
			response_data += 'Name: %s\n' % row[0]
			response_data += 'CardID: %s\n' % row[1]
			response_data += 'BirthDate: %s\n' % row[2]
			response_data += '====================\n'
		self.response(response_data)

	'''Nhan vien scan the'''
	def entry_get_handler(self):
		'''Lay CardID'''
		data_length = int(self.headers.getheader('content-length'))
		CardID = self.r(data_length)

		'''Debug'''
		print 'CardID:', CardID

		'''connect to database'''
		conn = connectdb()
		r = querydb(conn, r"SELECT * FROM Employee WHERE CardID=?", (CardID, ))

		if len(r) > 0:
			'''User da dang ky'''
			response_data = '1'
			print 'Registered user'
			'''Ghi record vao bang Work'''
			querydb(conn, r"INSERT INTO Work(CardID, EntryTime) VALUES (?, DATE('now'))", (CardID, ))

		else:
			'''User chua dang ky'''
			response_data = '0'
			print 'UnRegistered user'
			'''Ghi record vao bang UnRegistered'''
			try:
				querydb(conn, r"INSERT INTO UnRegistered(CardID) VALUES (?)", (CardID, ))
			except:
				pass
		self.response(response_data)
		conn.commit()
		conn.close()

	def do_GET(self):
		parsed_path = urlparse.urlparse(self.path)
		GET_HANDLERS = {'/add': self.add_employee_get_handler, '/statistic': self.statistic_get_handler}
		GET_HANDLERS.get(parsed_path.path, self.status404)()
	
	def add_post_handler(self):
		content_length = int(self.headers.getheader('content-length'))
		postvars = cgi.parse_qs(self.r(content_length), keep_blank_values = 1)
		
		if not postvars['CardID'][0]:
			self.response('Invalid request')
			return 
		CardID = postvars['CardID'][0]

		if not postvars['EmployeeName'][0]:
			self.response('Invalid request')
			return 
		EmployeeName = postvars['EmployeeName'][0]

		if not postvars['EmployeeBirthDate'][0]:
			self.response('Invalid request')
			return 
		EmployeeBirthDate = postvars['EmployeeBirthDate'][0]

		conn = connectdb()
		r = querydb(conn, r"INSERT INTO Employee(EmployeeName, CardID, EmployeeBirthDate) VALUES(?,?,DATE(?))", (EmployeeName, CardID, EmployeeBirthDate))
		self.response('')

	def do_POST(self):
		parsed_path = urlparse.urlparse(self.path)
		POST_HANDLERS = {	'/entry': self.entry_get_handler, 
							'/add': self.add_post_handler
						}
		POST_HANDLERS.get(parsed_path.path, self.status404)()
		
class ThreadedServer(SocketServer.ThreadingMixIn, HTTPServer):
		daemon_threads = True
		allow_reuse_address = True

		def __init__(self, server_address, RequestHandlerClass):
				HTTPServer.__init__(self, server_address, RequestHandlerClass)

if __name__ == '__main__':
	server = ThreadedServer(('0.0.0.0', 8080), GetHandler)
	print 'Starting server, use <Ctrl-C> to stop'
	server.serve_forever()
