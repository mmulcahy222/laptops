import os, sys, traceback
import collections
from .laptop_helper import *




#########################
#
#    Catch all exceptions for methods
#
#########################
def catch_exception(func):
	def func_wrapper(self,*args,**kwargs):
		try:
			# raise ValueError('A very specific bad thing happened')
			data = func(self,*args,**kwargs)
			return data
		except Exception:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			exc_text = str(exc_type) + ' ' + str(exc_obj) + ' ' + str(exc_tb.tb_lineno)
			# print("Exception for %s ----> %s" % ('',exc_text))
			#
			# MORE DETAILED
			#
			traceback.print_exc()
			# 
			return False
	return func_wrapper






#########################
#
#    A decorator that returns a file that exists already, or saves it in a folder so it won't have to be called again
#
#########################
def data_file_exists_decorator(func):
	def func_wrapper(self,*args,**kwargs):
		query = kwargs.get("model_number","none")
		file_path = 'C:/makeshift/files/laptops/data/%s_data.txt' % query
		#get contents from file if it exists
		if(os.path.isfile(file_path) == True):
			data = file_get_contents(file_path)
			print("%s characters read from %s" % (len(data),file_path))
			return data
		#actually run function
		data = func(self,*args,**kwargs)
		#write to file
		bytes_written = file_put_contents(file_path,data)
		print("%s bytes has been written to %s" % (bytes_written,file_path))
		return data
	return func_wrapper

#########################
#
#    BASE SCRAPER CLASS
#
#########################
class Scraper():
	site_data_dict = {}
	spec_url = ''
	def get_data(self,query):
		pass
	def organize_data(self):
		pass
	def convert_data(self):
		pass
	format = 'ModelUrl,Url,Category,SubCategory,SubSubCategory,Name,Product Name,Product Number,Microprocessor,Memory,Memory Max,Video Graphics,Display,Hard Drive,Wireless Connectivity,Sound,Keyboard,Pointing Device,External Ports,Dimensions,Weight,Power,ID Mech Description,Network Card,Camera,Microprocessor Cache,PC Card Slots,Whats In The Box,Expansion slots,Minimum dimensions (W x D x H),Power supply type,Battery type,Webcam,Audio features,Operating system,HP apps,Pre-installed software,Software included,Software - Productivity & finance,WWAN,Network interface,Flash cache,Multimedia Drive'
	def convert_to_row(self,data):
		format_list = self.format.replace(' ','_').lower().split(',')
		csv_row = []
		for attribute in format_list:
			try:
				csv_row.append(data[attribute])
			except e:
				csv_row.append("convert row error")
		return csv_row
	#########################
	#    SCRAPER (FOR CUSTOM COLUMNS!!!!)
	#########################
	def arrange_row(self,data):
		fields = collections.OrderedDict([
			("row",''),
			("brand_name",dvkp(data,'category').strip()),
			("series",regex_except_contains(dvkp(data,'category').strip(),dvkp(data,'name'))),
			("item_model_number",dvkp(data,'model_number')),
			("hardware_platform",''),
			("operating_system",regex_first('windows|android|apple',dvkp(data,'operating_system'),"n/a")),
			("operating_system_version",regex_get_number(dvkp(data,'operating_system'))),
			("operating_system_bits",regex_get_value('bit',dvkp(data,'operating_system'))),
			("color",dvkp(data,'color')),
			("screen",''),
			("display_type",dvkp(data,'display_type')),
			("screen_resolution",dvkp(data,'display_resolution')),
			("screen_size",dvkp(data,'screen_size')),
			("touch_screen",
			("item_weight",dvkp(data,'weight')),
			("product_dimensions",dvkp(data,'dimensions')),
			("cpu",dvkp(data,'cpu_sub_brand')),
			("processor",dvkp(data,'cpu')),
			("processor_brand",get_chunk(dvkp(data,'cpu'),0)),
			("model_processor",dvkp(data,'cpu_model')),
			("generation_processor",dvkp(data,'cpu_generation')),
			("processor_min_count",dvkp(data,'cpu_speed_min')),
			("processor_max_count",dvkp(data,'cpu_speed_max')),
			("processor_caches",dvkp(data,'cache')),
			("processor_core",regex_get_value_unit("core",dvkp(data,'cpu'))),
			("memory_ram",dvkp(data,'ram_memory')),
			("memory_generation",dvkp(data,'ram_technology')),
			("computer_memory_type",dvkp(data,'hard_drive_type')),
			("memory_speed",dvkp(data,'ram_speed')),
			("memory_slot_1",regex_first('SD[\s|,]',dvkp(data,'expansion_slots'))),
			("memory_slot_2",regex_first('SDXC[\s|,]',dvkp(data,'expansion_slots'))),
			("hard_drive_interface",regex_first_contains('sata|sshd',dvkp(data,'hard_drive'))),
			("hard_drive_capacity",regex_get_value_unit('TB|GB',dvkp(data,'hard_drive'))),
			("hard_drive_revolution",regex_get_value_unit('rpm',dvkp(data,'hard_drive'))),
			("chipset_brand",get_chunk(dvkp(data,'cpu'),0)),
			("video_graphics",dvkp(data,'graphics_card') + ' ' + dvkp(data,'graphic_type')),
			("graphic_memory",dvkp(data,'graphics_card')),
			("graphic_card_description",''),
			("wireless_connectivity",dvkp(data,'wireless')),
			("expansion_slots",dvkp(data,'expansion_slots')),
			("optical_drive_type",dvkp(data,'optical')),
			("usb_3.0_port",regex_exists("usb 3.0",dvkp(data,'external'))),
			("no._of_usb_3.0_ports",''),
			("hdmi_port",regex_exists("hdmi",dvkp(data,'external'))),
			("no._of_hdmi_port",''),
			("audio",dvkp(data,'audio')),
			("microphone_port",regex_exists('microphone',dvkp(data,'microphone'))),
			("no._of_microphone_port",''),
			("keyboard",''),
			("backlit_keyboard",regex_exists('backlit',dvkp(data,'keyboard'))),
			("pointing_device",dvkp(data,'pointing_device')),
			("webcam",'No' if dvkp(data,'webcam',None) == None else dvkp(data,'webcam')),
			("webcam_type",dvkp(data,'webcam')),
			("power_source",regex_except_exact('\d+,?|w|wh',dvkp(data,'power_source'))),
			("battery_type",regex_except_contains('cell',dvkp(data,'power_source'))),
			("battery_watt/hour",regex_first_contains('wh|watt',dvkp(data,'battery'))),
			("no._of_battery_cell",regex_first_contains('cell',dvkp(data,'battery')))
				])
		fields = [clean_cell(v) for k,v in fields.items()]
		return fields

	#########################
	#    FOR MANUAL ROWS. PRETTY MUCH A FACADE OMITTING FIRST STEP
	#########################
	def get_csv_by_url(self,url):
		html = self.get_html(url).strip()
		organized_data = self.organize_data(html)
		converted_data = self.convert_data(organized_data)
		converted_data = list(map(lambda x: x.replace(',','/'),converted_data))
		converted_data = ','.join(converted_data)
		return converted_data
