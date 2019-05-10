import sqlite3
TABLENAME = 'onions_onionsites'
dbname = "db.sqlite3"
#MAXid = 0
def get_MAX(dbname):
	conn = sqlite3.connect(dbname)
	cur = conn.cursor()	
	sql = "select MAX(id) from %s ;" % TABLENAME
	cur.execute(sql)
	return cur.fetchall()[0][0]

def insert_new_to_sqlite(domain,dbname):
	conn = sqlite3.connect(dbname)

	cur = conn.cursor()
#	cur.execute("select * from onions_onionsites;")
#	print(cur.fetchall())
	sql = "select name  from %s where name like '%%%s%%';" % (TABLENAME,domain)
	cur.execute(sql)
	rows = cur.fetchall()
	if len(rows) == 0:
		id_ = get_MAX(dbname)+1
		sql = "insert into %s values(%d,'%s','','',0,0)" % (TABLENAME,id_,domain)
		try:
			cur.execute(sql)
			conn.commit()
		except():
			pass
	conn.close()

def parse_onion(string):
	result = ''
	if "http://" in string:
		result = string[7:]
	elif "https://" in string:
		result = string[8:]
	if "/" in string:
		result = result.split('/')[0]
	return result

def get_os_update_candi(dbname):
	conn = sqlite3.connect(dbname)
	cur = conn.cursor()	
	sql = "select name from %s where onionscanned = 0 ;" % (TABLENAME)
	cur.execute(sql)	
	for onion in cur.fetchall():
		return onion[0]

def set_scanflag_1(onion):
	onion = onion.split('.')[0]
	conn = sqlite3.connect(dbname)
	cur = conn.cursor()	
	sql = "update %s set onionscanned = 1 where name like '%%%s%%' ;" % (TABLENAME,onion)
	cur.execute(sql)
	return conn.commit()

def data_to_string(data):
	string = '01234567890abcdefghijklmnopqrstuvwxyzZBCDEFGHIJKLMNOPQRSTUVWXYZ'
	result = ''

	for s in data:
		if s in string:
			result += s
	return result

def set_body(onion,data):
	onion = onion.split('.')[0]
	data = data_to_string(data)
	conn = sqlite3.connect(dbname)
	cur = conn.cursor()	
	sql = "update %s set body = '%s' where name like '%%%s%%' ;" % (TABLENAME,data,onion)
	cur.execute(sql)
	return conn.commit()

def main():
#	insert_new_to_sqlite('test4.onion','db.sqlite3')
#	get_os_update_candi('db.sqlite3')
#	set_scanflag_1("test3.onion")
	set_body('test3.onion',"'12`1~!@#$%^&*()_+234567890-=][poiuytrewasdfghjkl;'/.,mnbvcxzz`1234567890-=]\POIUYTREWQASDFGFFJKL;'/.,MNBVCXZ'")
if __name__ == '__main__':
	main()