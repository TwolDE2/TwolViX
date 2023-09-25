import time

from Tools.Directories import resolveFilename, SCOPE_CONFIG

PERCENTAGE_START = 0
PERCENTAGE_END = 100

profile_start = time.time()

profile_data = {}
total_time = 1
profile_file = None

try:
	f = open(resolveFilename(SCOPE_CONFIG, "profile"), "r")
	profile_old = f.readlines()
	f.close()

	t = None
	for line in profile_old:
		(t, id) = line[:-1].split('\t')
		t = float(t)
		total_time = t
		profile_data[id] = t
except:
	print("[Profile] no profile data available")

try:
	profile_file = open(resolveFilename(SCOPE_CONFIG, "profile"), "w")
except IOError:
	print("[Profile] WARNING: couldn't open profile file!")


def profile(id):
	now = time.time() - profile_start

	(dev, fmt) = ("/proc/progress", "%d \n")

	if profile_file:
		profile_file.write("%7.3f\t%s\n" % (now, id))

		if id in profile_data:
			t = profile_data[id]
			if total_time:
				perc = t * (PERCENTAGE_END - PERCENTAGE_START) // total_time + PERCENTAGE_START
			else:
				perc = PERCENTAGE_START
			try:
				f = open(dev, "w")
				f.write(fmt % perc)
				f.close()
			except IOError:
				pass


def profile_final():
	global profile_file
	if profile_file is not None:
		profile_file.close()
		profile_file = None
