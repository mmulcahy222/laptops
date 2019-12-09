# Freelance Laptop Project

In 2017 I was tasked to get all the laptop specifications for a various list of Laptops I was given, which would be used in the Laptop store https://www.agintechllc.com.

I had to get the images & data from various sources, so I used the template design pattern to separate the various sources (HP/IceCat/Asus/etc). Those classes are in the lib folder.

The HTML was saved locally on my own computer, and then data was extracted in different ways which was why they were separated into different classes.

Look at the file cdb_v2.py

Sometimes when you get the HTML of a page, you don't get the full HTML in something like the requests package in Python.

Enter Chrome Remote Debugger to automate this and GET me the entire HTML.

By refactoring the code into various sources, I could choose the order it would read to get the laptop specifications instead of having a convoluted mess.

cdb_v2.py

```python
import sys, lxml, json, urllib, re, time
import urllib.request
import websocket
from threading import Thread

#
#	CLASS
#

#
#	NOTE: FOR THE MAJORITY OF THESE FUNCTIONS, YOU CAN PASS IN EITHER AN ACTUAL WEB SOCKET OR THE TITLE OF THE WEB PAGE!!! Typically it would be listed as "ws" as the parameter
#
class cdb:
	web_sockets = []
	def __init__(self):
		self.initialize_web_sockets()
	def get_json_by_url(self):
		url = 'http://localhost:9222/json'
		raw_response = urllib.request.urlopen(url)
		response_string = raw_response.read().decode(raw_response.info().get_param('charset') or 'utf-8')
		chrome_json = json.loads(response_string)
		return chrome_json
	#this function is only ran once, making a list of dictionaries with web sockets & title (multidimensional)
	def initialize_web_sockets(self):
		chrome_list = self.get_json_by_url()
		for node in chrome_list:
			type = node['type']
			title = node['title']
			#to see if the key is in dictionary, use this syntax
			if type == 'page' and 'webSocketDebuggerUrl' in node:
				ws_url = node['webSocketDebuggerUrl']
				#self explanatory, but builds
				self.web_sockets.append({'connection':websocket.create_connection(ws_url),'title':title})
	def free_sockets(self):
		for socket in self.web_sockets:
			socket.close()
	#parameter substring is the TITLE of the url in lower case
	#returns the web socket from localhost:9222/json
	#parameter: substring of title of site
	#returns: actual web socket
	def get_ws_by_name(self,substring):
		array = self.web_sockets
		#if in string
		for node in array:
			title_lower_case = node['title'].lower()
			if substring in title_lower_case:
				return node['connection']
		return 0
	def get_first_tab_web_socket(self):
		return self.web_sockets[1]['connection']
	#this is what really does the work
	def low_level_call(self,web_socket,cri_parameters):
		#dumps makes it into the string type
		function_call_as_json_string = json.dumps(cri_parameters)
		dom = web_socket.send(function_call_as_json_string)
		response = web_socket.recv()
		#loads turn string into an object/data structure/list/dict/etc
		data = json.loads(response)
		return data
	#add new Chrome Remote Debugger directives in here (call function uses this)
	def get_parameter(self,name, params = {}):
		dict_of_dicts = {
			'reload': {"method": "Page.reload", "id": 1, "params": params},
			'document': {"method": "DOM.getDocument", "id": 1, "params": params},
			'navigate': {"method": "Page.navigate", "id": 1, "params": params},
			'evaluate': {"method": "Runtime.evaluate", "id": 1, "params": params}
		}
		return dict_of_dicts[name]
	#
	#
	#WS CAN BE THE WEB SOCKET OR THE TITLE NAME!!!
	#
	#
	#command is a name (like 'reload', where the dicts are in get_parameter function)
	#example: cri_1.call('wesnoth','reload')
	#or cdb.call('wesnoth',{"method": "Page.reload", "id": 1, "params": {}})
	#or cdb.call("database",'navigate',params={'url':'http://www.goonery.com'})
	def call(self,ws,command,params = {}):
		#if the command is NOT a typical dictionary directive to google and if it's TEXT, use the function called get parameter
		if bool(re.match("^[A-Za-z]*$", str(command))):
			command = self.get_parameter(command,params)
		if isinstance(ws,websocket._core.WebSocket):
			web_socket = ws
		else:
			web_socket = self.get_ws_by_name(ws)
		response = self.low_level_call(web_socket,command)
		return response
	def sanitize(self,string):
		return ''.join([x for x in string if ord(x) < 128])
	def get_html(self,ws):
		self.call(ws,{"method": "DOM.enable", "id": 1, "params": {}})
		response_document = self.call(ws,'document')
		print(response_document)
		node_id = response_document['result']['root']['nodeId']
		print(node_id)
		response_outer_html = self.call(ws,{"method": "DOM.getOuterHTML", "id": 1, "params": {'nodeId':node_id}})
		outer_html = response_outer_html['result']['outerHTML']
		outer_html = self.sanitize(outer_html)
		self.call(ws,{"method": "DOM.disable", "id": 1, "params": {}})
		return outer_html
	def run_javascript(self, ws, expression):
		response = self.call(ws,{"method": "Runtime.evaluate", "id": 1, "params": {'expression':expression}})
		if 'value' in response['result']['result']:
			return response['result']['result']['value']
		else:
			return response
	def go_to_page(self,ws,url):
		response = self.call(ws,{"method": "Page.navigate", "id": 1, "params": {'url':url}})
		return response
```