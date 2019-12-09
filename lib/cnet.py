from .scraper import *
from .laptop_helper import *
import re
import json
from bs4 import BeautifulSoup
import urllib
import urllib.request


class Cnet(Scraper):
	#########################
	#
	#    GET DATA
	#
	#########################
	@data_file_exists_decorator
	def get_data(self,**kwargs):
		model_number = kwargs.get('model_number')
		part_number = kwargs.get('part_number')
		queries = [part_number,model_number]
		for query in queries:
			try:
				cnet_search_url = 'https://www.cnet.com/search/?query=' + query
				print("Searching in %s" % cnet_search_url)
				cnet_search_html = self.get_html(cnet_search_url)
				bs_cnet_search_html = BeautifulSoup(cnet_search_html,'lxml')
				#
				#	DEBUG
				#
				# for a in bs_cnet_search_html.select(".itemInfo a"):
				# 	print("---")
				# 	print(query,part_number,model_number,a.text)
				# 	print('3', re.sub("[\(\)\-\s]","",model_number)[:7].lower())
				# 	print('4', re.sub("[\(\)\-\s]","",a.text).lower())
				product_url = [a['href'] for a in bs_cnet_search_html.select(".itemInfo a") if re.sub("[\(\)\-\s]","",model_number)[:7].lower() in re.sub("[\(\)\-\s]","",a.text).lower()][0]
				product_spec_url = "https://www.cnet.com" + product_url + "specs"
				print("Searching in %s" % product_spec_url)
				self.spec_url = product_spec_url
				return get_html(product_spec_url)
			except:
				traceback.print_exc()
				pass
		raise ValueError('Next')	
	#########################
	#
	#    ORGANIZE DATA
	#
	#########################
	def organize_data(self,data):
		bs = BeautifulSoup(data,'lxml')
		site_data_dict = {}
		#########################
		#    PART NUMBER
		#########################
		try:
			part_number = bs.select(".part-number")[0].text
		except:
			part_number = 'None'
		site_data_dict['part_number'] = part_number
		for li in bs.find(id='productSpecs').findAll('li'):
			#########################
			#    GET PREVIOUS HEADING
			#########################
			heading = ''
			try:
				heading = li.find_parents('ul')[0].findPreviousSiblings('h2')[0].text
			except:
				pass
			#########################
			#    GET THE VALUES FROM THE PAGE
			#########################
			div_1_text = li.findAll('div')[0].text.strip()
			div_2_text = li.findAll('div')[1].text.strip()
			div_1_text = re.sub('\s+',' ',div_1_text)
			div_2_text = re.sub('\s+',' ',div_2_text)
			attribute = (heading + ' ' + div_1_text).replace(' ','_').lower()
			value = div_2_text
			site_data_dict[attribute] = value
		return site_data_dict
	#########################
	#
	#    CONVERT DATA
	#
	#########################
	def convert_data(self,data,**kwargs):
		#memory
		model_number = kwargs.get("model_number")
		fields = {
			'audio_features' : dvkp(data,'video_features'),
			'battery_type' : dvkp(data,'battery_type') + ' ' + dvkp(data,'cells') + ' ' + dvkp(data,'battery_capacity'),
			'camera' : 'Integrated Camera' if empty(dvkp(data,'webcam')) == False else '',
			'category' : dvkp(data,'brand'),
			'dimensions' : '%s x %s x %s' % (inch_reformulator(dvkp(data,'width')),inch_reformulator(dvkp(data,'depth')),inch_reformulator(dvkp(data,'height'))),
			'display' : inch_reformulator(dvkp(data,'diagonal_size')) + ' (%s)' % dvkp(data,'display_resolution'),
			'expansion_slots' : dvkp(data,'flash_memory'),
			'external_ports' : dvkp(data,'expansion_interfaces').replace('2.0','2.0 ').replace('3.0','3.0 ').replace('HDMI','HDMI ').replace('LAN','LAN '),
			'flash_cache' : '',
			'hard_drive' : dvkp(data,'hard_drive_capacity'),
			'hp_apps' : '',
			'id_mech_description' : '',
			'keyboard' : get_item(dvkp(data,'input_type').split(','),0) + ' ' + dvkp(data,'input_features'),
			'memory' : dvkp(data,'installed_size'),
			'memory_max' : dvkp(data,'max_supported'),
			'microprocessor' : dvkp(data,'chipset_cpu'),
			'microprocessor_cache' : dvkp(data,'chipset_cache'),
			'minimum_dimensions_(w_x_d_x_h)' : '%s x %s x %s' % (inch_reformulator(dvkp(data,'width')),inch_reformulator(dvkp(data,'depth')),inch_reformulator(dvkp(data,'height'))),
			'modelurl' : self.spec_url,
			'multimedia_drive' : dvkp(data,'optical_storage_drive_type'),
			'name' : dvkp(data,'product_line'),
			'network_card' : dvkp(data,'link_protocol'),
			'network_interface' : dvkp(data,'link_protocol'),
			'operating_system' : dvkp(data,'provided'),
			'pc_card_slots' : '',
			'pointing_device' : get_item(dvkp(data,'input_type').split(','),1),
			'power' : conditional_format('Input = %s',dvkp(data,'adapter_input')) + ' ' + conditional_format('Output = %s',dvkp(data,'adapter_output')),
			'power_supply_type' : dvkp(data,'power_supply_type'),
			'pre-installed_software' : '',
			'product_name' : dvkp(data,'product_line'),
			'product_number' : get_item(dvkp(data,'part_number').split(':'),1),
			'software_-_productivity_&_finance' : '',
			'software_included' : '',
			'sound' : dvkp(data,'video_sound'),
			'subcategory' : dvkp(data,'brand') + ' ' + clean(dvkp(data,'model')),
			'subsubcategory' : dvkp(data,'brand') + ' ' + clean(dvkp(data,'model')),
			'url' : self.spec_url,
			'video_graphics' : dvkp(data,'graphics_processor'),
			'webcam' : 'Integrated Camera' if empty(dvkp(data,'webcam')) == False else '',
			'weight' : dvkp(data,'characteristics_weight'),
			'whats_in_the_box' : '',
			'wireless_connectivity' : dvkp(data,'wireless_protocol'),
			'wwan' : ''
		}
		fields_08012017 = {
			'cpu' : dvkp(data,'chipset_cpu'),
			'cpu_cache' : dvkp(data,'chipset_cache'),
			'cpu_generation' : dvkp(data,'processor_generation'),
			'cpu_brand' : dvkp(data,'processor_manufacturer'),
			'cpu_model' : dvkp(data,'processor_number'),
			'cpu_speed_min' : dvkp(data,'processor_clock'),
			'cpu_speed_max' : dvkp(data,'chipset_max_turbo'),
			'cpu_sub_brand' : dvkp(data,'processor_type'),
			'color':dvkp(data,'miscellaneous_color'),
			'display_type':dvkp(data,'display_type'),
			'display_resolution':dvkp(data,'display_resolution'),
			'graphics_brand' : dvkp(data,'graphics_processor_series'),
			'graphics_cpu' : dvkp(data,'graphics_processor'),
			'hard_drive_space' : dvkp(data,'hard_drive_capacity'),
			'hard_drive_type' : dvkp(data,'hard_drive_type'),
			'hard_drive_speed' : dvkp(data,'hard_drive_spindle_speed'),
			'keyboard_features' : dvkp(data,'input_features'),
			'model_number':model_number,
			'optical_drive' : dvkp(data,'optical_storage_drive_type'),
			'operating_system_name':get_chunk(dvkp(data,'operating_system'),1),
			'operating_system_version':regex_get_number(dvkp(data,'operating_system'),1),
			'operating_system_bit':regex_get_value('bit',dvkp(data,'operating_system'),1),
			'ram_speed' : dvkp(data,'memory_clock'),
			'ram_type' : dvkp(data,'memory_technology'),
			'screen_size' : dvkp(data,'diagonal_size'),
			'series' : get_chunk(dvkp(data,'header_product_line'),1),
			'touchscreen':dvkp(data,'display_touchscreen',"NO"),
			'webcam_exists':dvkp(data,'integrated_webcam',"NO"),
		}
		fields.update(fields_08012017)
		return fields