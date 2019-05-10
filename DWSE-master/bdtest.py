import requests
import json
import sqlite3
import multiprocessing
import subprocess
import time
import eventlet
TABLENAME = 'onions_onionsites'
dbname = "db.sqlite3"

proxies = {
    'http': 'socks5h://127.0.0.1:9150',
    'https': 'socks5h://127.0.0.1:9150'
}


#print(data)

def get_bd_update_candi():
	conn = sqlite3.connect(dbname)
	cur = conn.cursor()	
	sql = "select name from %s where bodyscanned = 0 ;" % (TABLENAME)
	cur.execute(sql)	
	onions = []
	for onion in cur.fetchall():
		onions.append(onion[0])
	return onions

def set_dataflag_1(onion):
	onion = onion.split('.')[0]
	conn = sqlite3.connect(dbname)
	cur = conn.cursor()	
	sql = "update %s set bodyscanned = 1 where name like '%%%s%%' ;" % (TABLENAME,onion)
	cur.execute(sql)
	return conn.commit()

def set_dataflag_m1(onion):
	onion = onion.split('.')[0]
	conn = sqlite3.connect(dbname)
	cur = conn.cursor()	
	sql = "update %s set bodyscanned = -1 where name like '%%%s%%' ;" % (TABLENAME,onion)
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

def processing(onion):
	#print(onion)
	#eventlet.monkey_patch()
	print("[*]try %s"%onion)
	#with eventlet.Timeout(5):
	data = requests.get("http://"+onion,proxies=proxies,verify=False, timeout=3).text
	print(data[:30])
	"""
	try:
		data = requests.get("http://"+onion,proxies=proxies).text
		print(data[:30])
	except:
		try:
			data = requests.get("https://"+onion,proxies=proxies).text
			print(data[:30])
		except:
			continue
	"""
	#		set_body(onion,data)
	#		print("[+]got body data from %s ."%onion)
	#		set_dataflag_1(onion)
	#		print("[+]set flag")	
	return 1 



def main():
#	onions = get_bd_update_candi()
	onions = ['tutdwuh7mlji5we3.onion','dirnxxdraygbifgc.onion','xmh57jrzrnw6insl.onion']	
	for onion in onions:
		process = multiprocessing.Process(target=processing(onion))
		#p.start()
		process_timer = Timer(30,handle_timeout,args=[process,onion])
		process_timer.start()
	
		stdout = process.communicate()		
		if process_timer.is_alive():
			process_timer.cancel()
			
if __name__ == '__main__':
	main()