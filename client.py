import lib,csv, pprint, re, os, sys, traceback,time
from lib import *
from bs4 import BeautifulSoup

#########################
#    Objects
#########################
# mysql = lib.mysql_laptop_helper.MySqlLaptopHelper()
icecat = lib.icecat.Icecat()
hp = lib.hp.Hp()
cnet = lib.cnet.Cnet()
newegg = lib.newegg.Newegg()
images_icecat = lib.images_icecat.ImagesIcecat()
images_google = lib.images_google.ImagesGoogle()

#########################
#    Variables
#########################
csv_source = "C:/makeshift/files/laptops/csv/07062017_source.csv"
csv_destination = "C:/makeshift/files/laptops/csv/3.0.csv"
start = int(lh.get_item(sys.argv,1,2))
end = int(lh.get_item(sys.argv,2,2000))
scraper_cycle = [hp,cnet,icecat,newegg]
image_cycle = [images_icecat,images_google]

#########################
#    Client
#########################
csv_dest_handle = open(csv_destination, "w")
csv_writer = csv.writer(csv_dest_handle, delimiter=',')
with open(csv_source, 'r') as csvfile:
	csv = csv.reader(csvfile, delimiter=',')
	for row_number,row in enumerate(csv):
		row_inserted_flag = False
		#skip certain rows
		if row_number < start or row_number > end:
			continue
		#########################
		#    Values From Source
		#########################
		part_number = row[0].strip()
		model_number = row[1].strip()
		sub_family = row[2].strip()
		lh.new_row_print("%s: PART NUMBER -> %s: MODEL NUMBER -> %s:" % (row_number,part_number,model_number))
		#########################
		#    Data Scraper in three steps
		#########################
		for data_scraper in scraper_cycle:
			data_scraper_type = data_scraper.__class__.__name__
			try:
				#step 1
				print("\n----------------\nGetting Data with %s\n----------------" % data_scraper_type)
				data = data_scraper.get_data(model_number)
				#step 2
				print("\n----------------\nOrganizing Data with %s\n----------------" % data_scraper_type)
				organized_data = data_scraper.organize_data(data)
				#step 3
				print("\n----------------\nCreating CSV Row with %s\n----------------" % data_scraper_type)
				csv_row = data_scraper.convert_data(organized_data, part_number=part_number)
				#########################
				#    Write CSV Row
				#########################
				row_inserted_flag = True
				csv_row = [part_number,model_number,data_scraper_type] + csv_row
				print(csv_row)
				csv_writer.writerow(csv_row)
				csv_dest_handle.flush()
				time.sleep(1)
				#########################
				#
				#    IMAGES
				#
				#########################
				# if data_scraper_type == 'Icecat':
				# 	print("\n----------------\nGetting Images using Icecat\n----------------")
				# 	data = images_icecat.get_data(query=part_number + ' ' + model_number,model_number=model_number)
				# 	image_links = images_icecat.organize_data(data)
				# 	images_icecat.save_images(image_links=list(image_links),part_number=part_number)
				# else:
				# 	print("\n----------------\nGetting Images using Google\n----------------")
				# 	data = images_google.get_data(query=part_number + ' ' + model_number,model_number=model_number)
				# 	image_links = images_google.organize_data(data)
				# 	images_google.save_images(image_links=list(image_links),part_number=part_number)
				#########################
				#    Success and move on
				#########################
				break
			#########################
			#    Expected flow for a lot of laptops, because HP won't match
			#########################
			#########################
			#    Exception Here
			#########################
			except Exception:
				# #HP check
				# if data_scraper_type == 'Hp':
				# 	print("NOT HP")
				# 	continue
				traceback.print_exc()
				time.sleep(1)
				continue
		#########################
		#    If reached here, none of the scrapers returned anything. Fill in blank row
		#########################
		if row_inserted_flag == False:
			print("\n----------------\nNo Matches. Creating Blank Row\n----------------")
			blank_row = [model_number,part_number,"blank"] + [''] * 41
			print(blank_row)
			csv_writer.writerow(blank_row)
			csv_dest_handle.flush()
