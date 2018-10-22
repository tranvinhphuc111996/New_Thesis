from threading import Thread
from time import sleep

class MyThread(Thread):
   def __init__(self,delay):
      Thread.__init__(self)
      self.time = delay
   def run(self):
   	  while True:
   	  	print('AAA')
   	  	sleep(self.time)


phuc = MyThread(1)
phuc.start()

#for i in range(10):
#	print('BBB')
#	
if __name__ == "__main__":
	phuc = MyThread(1)
	phuc.start()
	while True:
		print("BBBBBBBBBBBBBBBBB")
		sleep(2)
	