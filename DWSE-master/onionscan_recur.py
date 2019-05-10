import subprocess
import os, sys
import time




def main():

	command = "python onionscan.py"
	for i in range(10):
		popen1 = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		time.sleep(1)
		popen2 = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		time.sleep(1)
		popen3 = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		time.sleep(1)
		popen4 = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		time.sleep(1)
		popen5 = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		
		time.sleep(420)
	
		popen1.kill()
		time.sleep(1)
		popen2.kill()
		time.sleep(1)
		popen3.kill()
		time.sleep(1)
		popen4.kill()
		time.sleep(1)
		popen5.kill()

if __name__ == '__main__':
	main()