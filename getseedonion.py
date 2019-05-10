#-*- coding: utf-8 -*-
import os, sys
import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import sqlite3
CURRENT_PATH = os.getcwd()
LIB_PATH = CURRENT_PATH+"\lib"
QUERY = "aaaa"
SEARCH_QUERY = 'hidden+link'
TIME_LIMIT = 'month'	
TABLENAME = 'onions_onionsites'
URL_TO_SEARCH = []
ONION_DICT = []

"""
def div_url_reddit(url):


	p = re.compile("https?://\w+[.]onion") # onion link 
	q = re.compile()
	if onion site : 
		ONION_DICT.append(url)
	elif 게시판 글 : 
		URL_TO_SEARCH.append(url)
"""

def find_onion_link_to_dict(text) : 
	p = re.compile("https?://\w+[.]onion") # onion link 
	#print (p.findall(text))
	onions = p.findall(text)
	for onion in onions:
		if onion not in ONION_DICT:
			ONION_DICT.append(onion)
			print ("[+]found onion site: %s" % onion)
			onion = parse_onion(onion)
			if "onion" in onion:
				insert_new_to_sqlite(onion,'db.sqlite3')

	#print "a"
	#exit(0)
	#print onion_candi


def save(filename,text):
	f = open(filename,'w')
	f.write(text)
	f.close()

def get_MAX(dbname):
	conn = sqlite3.connect(dbname)
	cur = conn.cursor()	
	sql = "select MAX(id) from %s ;" % TABLENAME
	cur.execute(sql)
	return cur.fetchall()[0][0]

def insert_new_to_sqlite(domain,dbname):
	conn = sqlite3.connect(dbname)

	cur = conn.cursor()
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

def main():
	options = webdriver.ChromeOptions()
	options.add_argument('headless')
	options.add_argument('window-size=1920x1080')
	options.add_argument('disable-gpu')
	options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
	#options.add_argument("proxy-server=localhost:8080")
	#options.add_argument('--disable-gpu')

	driver = webdriver.Chrome(LIB_PATH+'\chromedriver.exe', chrome_options=options)

	url = 'https://www.reddit.com/search?q='+SEARCH_QUERY+'&t='+TIME_LIMIT


	driver.get(url)
	driver.implicitly_wait(3)
	#driver.get_screenshot_as_file('naver_main_headless.png')

	html = driver.page_source
	soup = BeautifulSoup(html,'html.parser')

	title = soup.find('title')
	#print (title)
	html_ascii = html.encode('ascii','ignore')

	checksum = False 
	for link in soup.find_all('a'):
		try : 
			link_addr = link.get('href').encode('ascii','ignore').decode()
		except : 
			link_addr = ''
		#앞의 쓸모없는 것들 버리기 \
		if 'reddit.com/wiki/search' in link_addr :
			checksum = True
		if checksum == False : 
			continue

		# /r /u로 시작하는 거 처리	
		if link_addr[0]=="/":
			link_addr = "https://www.reddit.com"+link_addr
		#주소가 아닌 것 버리기
		if "http" not in link_addr : 
			continue

		#분류. 주소가 onion인건 바로 넣고, 아니면 들어가서 다시 찾아봄
		if ".onion" in link_addr : 
			ONION_DICT.append(link_addr)
			onion = parse_onion(link_addr)
			if "onion" in onion:
				insert_new_to_sqlite(onion,'db.sqlite3')

		else : 
			URL_TO_SEARCH.append(link_addr)

		"""
		1) http://*.onion 
		2) Search result : /r/~~~ -> 들어가줘야 댐  
		"""


	for link in URL_TO_SEARCH : 
		driver.get(link)
		html = driver.page_source
		#soup = BeautifulSoup(html,'html.parser')
#		print (link)
		find_onion_link_to_dict(html)
	#save('result_notime.html',html_ascii)

	driver.quit()
	print("[+]found %d onion sites in reddit for a month. update database" % len(ONION_DICT))
	"""
	이제, DB에 넣음
	근데, 파싱먼저 하자. http나 https:// 빼고, asdf.onion만 들어가게. 마지막 / 있음 그것도 뺴고 깔끔하게 (뒤에 파일저장문제)
	
	for onion in ONION_DICT:
		onion = parse_onion(onion)
		if "onion" in onion:
			insert_new_to_sqlite(onion,'db.sqlite3')
	"""
if __name__ == '__main__':
	main()