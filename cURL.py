#assuming that the program is started and then they input the curl statement

message = input("Enter curl or web browser: ")


if (message[0:message.find(' ')] == 'curl') and (message[message.find(' ') + 1:message.find(' ', message.find(' ')+1)] == '-u'):
	username = message[message.find(' ', message.find(' ') + 1) + 1: message.find(':')]
	password = message[message.find(':') + 1: message.find(' ', message.find(':'))]
	http = message[message.find(' ', message.find(':')) + 1:]

	ipadd = http[http.find('/') + 2: http.find(':', http.find('/') + 2)]
	portnum = http[http.find(':', http.find('/') + 2) + 1: http.find('/', http.find('/') + 2)]

	if (http[http.find('/', http.find('/') + 2) + 1: http.find('?')] == 'LED'):
		#Status, color and intensity
		command = http[http.find('=') + 1: http.find('-')] #on or off
		color = http[http.find('-', http.find('=')) + 1: http.find('-', http.find('-') + 1)]
		intensity = http[http.find('-', http.find('-') + 1) + 1:]
	
	#canvas filename
	else:
		file = http[http.find('=') + 1:]


else:
	print("in here")