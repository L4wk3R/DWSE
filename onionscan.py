from stem.control import Controller
from stem import Signal
from threading import Timer
from threading import Event

import codecs
import json
import os
import random
import subprocess
import sys
import time

import sqlite3
import getseedonion as gs

dbname = 'db.sqlite3'
TABLENAME = 'onions_onionsites'

onions         = []
session_onions = []

identity_lock  = Event()
identity_lock.set()

#
# Grab the list of onions from our master list file.
#https://raw.githubusercontent.com/automatingosint/osint_public/master/onionrunner/onionrunner.py

def get_onion_list():
	
	# open the master list
	if os.path.exists("onion_master_list.txt"):
	
		with open("onion_master_list.txt","rb") as fd:

			stored_onions = fd.read().splitlines()	
	else:
		print ("[!] No onion master list. Download it!")
		sys.exit(0)
	
	print ("[*] Total onions for scanning: %d" % len(stored_onions))

	return stored_onions
#
# Stores an onion in the master list of onions.
#
def store_onion(onion):
	
	print ("[++] Storing %s in master list." % onion)
	
	with codecs.open("onion_master_list.txt","ab",encoding="utf8") as fd:
		fd.write("%s\n" % onion)

	return
	
#
# Runs onion scan as a child process.
#		
def run_onionscan(onion):
	
	print ("[*] Onionscanning %s" % onion)
	
	# fire up onionscan
	process = subprocess.Popen(["onionscan","--torProxyAddress=127.0.0.1:9150","--webport=0","--jsonReport","--simpleReport=true",onion],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	#process = subprocess.Popen(["onionscan torProxyAddress 127.0.0.1:9050 --webport=0 --jsonReport --simpleReport=false",onion],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	# start the timer and let it run 5 minutes
	process_timer = Timer(300,handle_timeout,args=[process,onion])
	process_timer.start()

	# wait for the onion scan results
	stdout = process.communicate()[0]

	# we have received valid results so we can kill the timer 
	if process_timer.is_alive():
		process_timer.cancel()
		return stdout

	print ("[!!!] Process timed out!"	)

	return None

#
# Handle a timeout from the onionscan process.
#
def handle_timeout(process,onion):

	global session_onions
	global identity_lock 

	# halt the main thread while we grab a new identity
	identity_lock.clear()

	# kill the onionscan process
	try:
		process.kill()
		print ("[!!!] Killed the onionscan process.")
	except:
		pass

	# Now we switch TOR identities to make sure we have a good connection
	with Controller.from_port(port=9150) as torcontrol:

		# authenticate to our local TOR controller
		torcontrol.authenticate("PythonRocks")

		# send the signal for a new identity
		torcontrol.signal(Signal.NEWNYM)

		# wait for the new identity to be initialized
		time.sleep(torcontrol.get_newnym_wait())

		print ("[!!!] Switched TOR identities.")

	# push the onion back on to the list	
	session_onions.append(onion)
	random.shuffle(session_onions)

	# allow the main thread to resume executing
	identity_lock.set()	

	return


def set_scanflag_1(onion):
	onion = onion.split('.')[0]
	conn = sqlite3.connect(dbname)
	cur = conn.cursor()	
	sql = "update %s set onionscanned = 1 where name like '%%%s%%' ;" % (TABLENAME,onion)
	cur.execute(sql)
	return conn.commit()

def set_onionscanfile(onion,filename):
	onion = onion.split('.')[0]
	conn = sqlite3.connect(dbname)
	cur = conn.cursor()	
	sql = "update %s set onionscanfile = '%s' where name like '%%%s%%' ;" % (TABLENAME,filename,onion)
	cur.execute(sql)
	return conn.commit()


def get_os_update_candi():
	result = []
	conn = sqlite3.connect(dbname)
	cur = conn.cursor()	
	sql = "select name from %s where onionscanned = 0 ;" % (TABLENAME)
	cur.execute(sql)	
	for onion in cur.fetchall():
		result.append(onion[0].encode())
	return result
	
#
# Processes the JSON result from onionscan.
#
def process_results(onion,json_response):
	global onions
	global session_onions

	# create our output folder if necessary
	if not os.path.exists("datas"):
		os.mkdir("datas")

	# write out the JSON results of the scan
#	with open("%s/%s.json" % ("onionscan_results",onion, "wb") as fd:
#	print ("%s\\%s.json" % ("onionscan_results",onion.replace('/','#')))
#	print (json_response)
	with open(os.path.join("datas\\",onion.replace(':',';').replace('/','#')), "wb") as fd:
		fd.write(json_response)
		print("[+]succeed to get data. update db")
		set_scanflag_1(onion)
		set_onionscanfile(onion,onion.replace(':',';').replace('/','#'))
	# look for additional .onion domains to add to our scan list
	#scan_result = ur"%s" % json_response.decode("utf8")
	scan_result = r"%s" % json_response.decode("utf8")
	#print(scan_result)	
	scan_result = json.loads(scan_result)
	
	if scan_result['identifierReport']['linkedOnions'] is not None:
		add_new_onions(scan_result['identifierReport']['linkedOnions'])		
		
	if scan_result['identifierReport']['relatedOnionDomains'] is not None:
		add_new_onions(scan_result['identifierReport']['relatedOnionDomains'])
		
	if scan_result['identifierReport']['relatedOnionServices'] is not None:
		add_new_onions(scan_result['identifierReport']['relatedOnionServices'])
		
	return

def get_MAX(dbname):
	conn = sqlite3.connect(dbname)
	cur = conn.cursor()	
	sql = "select MAX(id) from %s ;" % TABLENAME
	cur.execute(sql)
	return cur.fetchall()[0][0]

def insert_new_to_sqlite(domain,dbname):
	conn = sqlite3.connect(dbname)

	cur = conn.cursor()
	sql = "select name from %s where name like '%%%s%%';" % (TABLENAME,domain)
	cur.execute(sql)
	rows = cur.fetchall()
	if len(rows) == 0:
		id_ = get_MAX(dbname)+1
		sql = "insert into %s values(%d,'%s','','',0,0)" % (TABLENAME,id_,domain)
		try:
			print("[++]insert this domain to db")
			cur.execute(sql)
			conn.commit()
		except():
			pass
	conn.close()	

#
# Handle new onions.
#
def add_new_onions(new_onion_list):

	global onions
	global session_onions

	for linked_onion in new_onion_list:

		if linked_onion not in onions and linked_onion.endswith(".onion"):

			print ("[++] Discovered new .onion => %s" % linked_onion)

			#linked_onion = gs.parse_onion(linked_onion)
			insert_new_to_sqlite(linked_onion,dbname)

			onions.append(linked_onion)
			session_onions.append(linked_onion)
			random.shuffle(session_onions)
			store_onion(linked_onion)
	return





def main():
	# get a list of onions to process
#	onions = get_onion_list()
#	print (onions)

	onions = get_os_update_candi()
#	print (onions)

	# randomize the list a bit
	random.shuffle(onions)
	session_onions = list(onions)

	count = 0

	while count < len(onions):
		#count += 1
		# if the event is cleared we will halt here
		# otherwise we continue executing
		identity_lock.wait()

		# grab a new onion to scan
		print ("[*] Running %d of %d." % (count,len(onions)))
		
		onion  = session_onions.pop()
		onion = onion.decode()
		# test to see if we have already retrieved results for this onion
		#if os.path.exists("onions\\templates\\onions\\oniondata\\%s.json" % onion):
		if os.path.exists("datas\\%s.json" % onion):
			print ("[!] Already retrieved %s. Skipping." % onion)
			count += 1

			continue

		# run the onion scan	
		result = run_onionscan(onion)
		print (result)
		# process the results
		if result is not None:
			
			if len(result):
				process_results(onion,result)		

				count += 1		

if __name__ == '__main__':
	main()