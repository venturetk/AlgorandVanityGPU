import argparse
import time
import signal
import sys
import os
import multiprocessing
from multiprocessing import Process, Queue, Value, Lock
from algosdk import account, mnemonic

def find_address(pattern, queue, count):
	while True:
		with count.get_lock():
			count.value += 1

		# generate the account
		private_key, address = account.generate_account()

		if (count.value % 100000) == 0:
			timeRun = time.time() - start_time
			keyspersec = count.value / timeRun
			## print("Count: " + str(count.value) + " Time: " + str(int(timeRun)) + " Keys/sec: " + str(int(keyspersec)))
			print("Count: " + str(count.value) + " Keys/sec: " + str(int(keyspersec)))

		if address.startswith(pattern):
			queue.put((address, private_key))
			break

# handler for ctrl-c action
def signal_handler(sig, frame):
	print("")
	print("No match in " + str(count.value) + " attempts and " + get_running_time() + " seconds")
	terminate_processes()
	sys.exit(1)

# calculate and format running time
def get_running_time():
	running_time = time.time() - start_time
	running_time_str = str(round(running_time, 2))  #format to string with 2 decimals
	return running_time_str

# cleanup spawned processes
def terminate_processes():
	for p in jobs:
		p.terminate()

if __name__ == '__main__':
	p = argparse.ArgumentParser()
	p.add_argument("pattern", type=str, help="Pattern to look for at the start of an algorand address.")
	pattern = p.parse_args().pattern

	num_processors = multiprocessing.cpu_count()
	print("Detected " + str(num_processors) + " cpu(s)")

	start_time = time.time()
	count = Value('i', 0)
	queue = Queue()
	jobs = []

	# spawn search processes for each processor
	for i in range(num_processors):
		print("Process " + str(i+1) + " started.")
		p = Process(target=find_address, args=(pattern, queue, count))
		jobs.append(p)
		p.start()

	signal.signal(signal.SIGINT, signal_handler)  # capture ctrl_c

	address, private_key = queue.get() #return once one of the spawned processes finds a match
	if(address):
		print("Found a match for " + pattern + " after " + str(count.value) + " tries in " + get_running_time() + " seconds")
		print("Address: ", address)
		print("Private key: ", mnemonic.from_private_key(private_key))

	terminate_processes()