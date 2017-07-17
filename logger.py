from os.path import basename, splitext

class loglevel:
	ALL = 6
	DEBUG = 5
	INFO = 4
	WARN = 3
	ERROR = 2
	FATAL = 1

class logheader:
	NOHDR = ""
	PASS = "[PASS]"
	FAIL = "[FAIL]"

class logger():
	def __init__(self, logname, failedlogname = "", passedlogname = ""):
		self.logname = logname
		self.failedlogname = failedlogname
		self.passedlogname = passedlogname



		if failedlogname == "":
			self.failedlogname = basename(logname) + "_failed" + splitext(logname)[1]
		if passedlogname == "":
			self.passedlogname = basename(logname) + "_passed" + splitext(logname)[1]

		self.loghdl = open(logname, "w")
		self.failedloghdl = open(self.failedlogname, "w")
		self.passedloghdl = open(self.passedlogname, "w")

		self.loglevel = loglevel.ALL

	def set_level(self, level):
		self.loglevel = level

	def set_logname(self, logname):
		if self.loghdl:
			self.loghdl.close()
		self.logname = logname
		self.loghdl = open(logname, "w")

	def init_log_msg(self, msg, ispassed = True):
		output = "%s %s \n"
		if ispassed:
			output = output % (logheader.PASS, msg)
		else:
			output = output % (logheader.FAIL, msg)
		return output

	def write_log(self, msg, level, ispassed = True):
		if level <= self.loglevel:
			self.loghdl.write(self.init_log_msg(msg, ispassed))
			if ispassed:
				self.passedloghdl.write(msg + "\n")
			else:
				self.failedloghdl.write(msg + "\n")

if __name__ == "__main__":
	logger = logger("test_logger.txt")
	logger.write_log("Hello", 6 )
	logger.write_log("World", 6, False )