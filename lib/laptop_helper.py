import time
import random
from .cdb_v2 import cdb
import urllib
import traceback
import urllib.parse
import operator
from bs4 import BeautifulSoup
import requests
import json
import re
import os
import sys
import selenium
import itertools
from selenium import webdriver
import urllib.request
import html.parser
import requests
from requests.exceptions import HTTPError
from socket import error as SocketError
from http.cookiejar import CookieJar



#########################
#
#	 structure of laptop table is
#	 
#    #part_number - model_number - sub_family - source 
#    
#########################



def sanitize(word):
	return ''.join([x for x in str(word) if ord(x) < 128])
def get_item(iterable, index, default=''):
	try:
		return operator.getitem(iterable, index)
	except:
		return default
def file_put_contents(filename,data):
	f = open(filename, 'w')
	data = sanitize(data)
	w = f.write(data)
	f.close()
	return w
def file_put_image(image_link,file_name):
	f = open(file_name, 'wb')
	w = f.write(requests.get(image_link, timeout=10).content)
	f.close()
	return w
def file_get_contents(filename):
	f = open(filename, 'r')
	r = f.read()
	r = sanitize(r)
	f.close()
	return r
def dvkp(dict, key_part, default=''):
	try:
		return [value for key,value in dict.items() if key_part in key][0]
	except:
		return default
def inch_reformulator(value):
	number =  [chunk for chunk in value.split() if re.search('[A-Za-z]',chunk) == None][0]
	number = float(number)
	if 'mm' in value:
		number /= 25.4
		number = round(number,2)
		return str(number) + '"'
	if 'cm' in value:
		number /= 2.54
		number = round(number,2)
		return str(number) + '"'
	return value
def clean_cell(value):
	value = str(value)
	value = re.sub('\s+',' ',value)
	value = re.sub(',+',',',value)
	return value.strip()
def get_inside_parentheses(value):
	try:
		return re.findall('(?<=\().*?(?=\))',value)[0]
	except:
		return ''
def empty( variable ):
	if not variable:
		return True
	return False
def conditional_format(string_percent, value, default = ''):
	if not value:
		return default
	return string_percent % value
def new_row_print(val):
	print('\n\n\n##########################\n#\n#\t%s\n#\n##########################\n\n\n' % val)
def clean(obj,default=""):
	try:
		return obj
	except:
		return default	
#########################
#PYTHON WEB REQUEST
#########################
def get_html(url):
	try:
		req=urllib.request.Request(url, None, {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; G518Rco3Yp0uLV40Lcc9hAzC1BOROTJADjicLjOmlr4=) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3','Accept-Language': 'en-US,en;q=0.8','Connection': 'keep-alive'})
		cj = CookieJar()
		opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
		response = opener.open(req)
		raw_response = response.read().decode('utf8', errors='ignore')
		response.close()
		raw_response = ''.join([x for x in str(raw_response) if ord(x) < 128])
		raw_response = raw_response.replace("<!DOCTYPE html>","").replace("\n","")
		return(raw_response)
	except urllib.request.HTTPError as inst:
		output = format(inst)
		print(output)
def range_from_tuples(tuples):
	return list(itertools.chain.from_iterable([list(range(t[0],t[1]+1)) for t in tuples]))
#########################
#SELENIUM
#########################
def get_selenium_html(url):
	driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
	driver.get(url)
	html = driver.find_element_by_tag_name('html').get_attribute('outerHTML')
	return res
#########################
#CHROME DEBUG
#########################
def get_chrome_html(url,wait_time=4):
	cdbo = cdb()
	ws = cdbo.get_first_tab_web_socket()
	response = cdbo.go_to_page(ws,url)
	time.sleep(wait_time)
	html = cdbo.run_javascript(ws,"document.documentElement.innerHTML")
	html = sanitize(html)
	return html
#########################
#    REGEX
#########################
def regex_first(regex,phrase,default=""):
	return get_item(re.findall(regex.lower(),phrase.lower()),0,default)
def regex_first_contains(regex,phrase,default="n/a"):
	return regex_first("\w*" + regex + "\w*",phrase.lower(),default)
def regex_except_exact(regex,phrase,default=""):
	return ' '.join([chunk for chunk in phrase.lower().split(" ") if not re.search("^("+regex.lower()+")$", chunk)])
def regex_except_contains(regex,phrase,default=""):
	return ' '.join([chunk for chunk in phrase.lower().split(" ") if not re.search("("+regex.lower()+")", chunk)])
def regex_get_value(regex,phrase,default="n/a"):
	return get_item(regex_first("([\d|.]+)[-|\s*x?\s*]*("+regex.lower()+")",phrase.lower()),0,default)
def regex_get_text_left(regex,phrase,default="n/a"):
	return get_item(regex_first("(\w+)[-|\s*x?\s*]*("+regex.lower()+")",phrase.lower()),0,default)
def regex_get_value_right(regex,phrase,default="n/a"):
	return get_item(regex_first("("+regex.lower()+")(-|\s*x?\s*)(\d+,?)",phrase.lower()),-1,default)
def regex_get_value_unit(regex,phrase,default=""):
	matched_groups = get_item(re.findall("([\d|.]+)(\s*x?\s*|-)("+regex.lower()+")",phrase.lower()),0)
	matched_string = ''.join(map(str,matched_groups))
	return matched_string
def regex_get_number(phrase,default="n/a"):
	return regex_first('([\d|.|"]+)',phrase.lower(),default)
def regex_exists(regex,phrase):
	value = regex_first(regex.lower(),phrase.lower(),default=None)
	if value != None:
		return "YES"
	else:
		return "NO"
#########################
#    More
#########################
def get_chunk(phrase,value = 0):
	return get_item(phrase.split(" "),value)
#########################
#    DO THIS IF GIVEN A NEW COLUMN SCHEMA
#########################
def csv_to_dict(comma_string):
	for t in comma_string.split(","):
		print('("%s",dvkp(data,\'\')),' % t.strip().lower().replace(" ","_"))
#for reorient
def csv_neat(comma_string):
	l = []
	for term in comma_string.split(","):
		l.append(term.strip().lower().replace(" ","_"))
	return (''.join([" " + v + " ," for v in l])).rstrip(',')
#make into a variable
def header_variable(text):
	return text.strip().lower().replace(" ","")

