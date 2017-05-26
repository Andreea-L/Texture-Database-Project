import xml.etree.ElementTree as ET
from collections import defaultdict
import os
import fnmatch
from pprint import pprint
import string
import csv
import itertools
from fuzzywuzzy import fuzz

PATHS = ['C:\Users\Andreea\Documents\Substance Project\SubstanceDatabase2-updated\Substance_Database_2.1\Substance_Database_2.1_BitmapBased_Sbs\Substance_Database_2.1_BitmapBased_Sbs']#,
		# 'C:\Users\Andreea\Documents\Substance Project\SubstanceDatabase2-updated\Substance_Database_2.1\Substance_Database_2.1_Procedural_0\Substance_Database_2.1_Procedural_Sbs',
		# 'C:\Users\Andreea\Documents\Substance Project\SubstanceDatabase2-updated\Substance_Database_2.1\Substance_Database_2.1_Procedural_0\Substance_Database_2.1_Procedural_Sbs\PBR_Materials']

SIMILARITY_PERCENTAGE = 97


channel_dict = defaultdict(int)
basic_param_dict = defaultdict(int)
advanced_param_dict = defaultdict(int)

ungrouped_dict = defaultdict(int)

def format_identifier(s):
	return string.capwords(s.replace("_"," "))

def setup_path(path):

	sbs_files = []
	for dirpath, dirnames, files in os.walk(path):
		dirnames[:] = [d for d in dirnames if d not in [".autosave", "PBR_Materials"]]
		for f in fnmatch.filter(files, '*.sbs'):
			sbs_files += [os.path.join(dirpath, f)]
	return sbs_files

def extract_info(content_tag):

	global channel_dict, basic_param_dict, advanced_param_dict, ungrouped_dict


	print "Texture Name:", content_tag.find("identifier").attrib['v']

	output_channels = content_tag.find("paraminputs")
	for channel in output_channels:

		name = format_identifier(channel.find("identifier").attrib['v'])
		print "Name:", name
		ch_type = channel.find("type").find("value").attrib['v']
		print "Type:", ch_type
		# dval_tag = channel.find("defaultValue")
		# if dval_tag is not None:
		# 	for v in dval_tag:
		# 		dvalue = v.find("value").attrib['v']
		# 		print "Default value:", dvalue

		dwidget_tag = channel.find("defaultWidget")
		if dwidget_tag is not None:
			widget_name = dwidget_tag.find("name").attrib['v']
			if widget_name in ["slider", "color", "angle", "dropdownlist"]:
				options = dwidget_tag.find("options")
				for option in options:
					if option.find("name").attrib['v'] == "parameters":
						print "Values: ", option.find("value").attrib['v']
					elif option.find("name").attrib['v'] == "min":
						print "Minimum value: ", option.find("value").attrib['v']
					elif option.find("name").attrib['v'] == "max":
						print "Maximum value: ", option.find("value").attrib['v']
					elif option.find("name").attrib['v'] == "step":
						print "Step size: ", option.find("value").attrib['v']

		group = ""
		group_tag = channel.find("group")
		if group_tag is not None:
			group = group_tag.attrib['v']
			print "Group:", group
		else:
			ungrouped_dict[name] +=1

		if group == "Channels":
			channel_dict[name] += 1
		elif "Basic" in group:
			basic_param_dict[name] += 1
		elif "Advanced" in group:
			advanced_param_dict[name] += 1
		print "\n"
	print "##################\n"


def merge_similar(dictionary):	
	for pair in list(itertools.combinations(dictionary,2)):
		if fuzz.ratio(pair[0], pair[1]) > SIMILARITY_PERCENTAGE:
			dictionary[pair[0]] += dictionary[pair[1]]
			del dictionary[pair[1]]

def write_dict_to_csv(dictionary, file_name, delim):

	with open(file_name+'.csv', 'w+') as csv_file:
		writer = csv.writer(csv_file,delimiter=delim)
		for key, value in dictionary.items():
		   writer.writerow([key, value])

def main():

	i=0
	for path in PATHS:

		sbs_files = setup_path(path)

		for file in sbs_files:
			print "Parsing: ", file, "\n"

			tree = ET.parse(file)
			root = tree.getroot()
			content = root.find("content")
			content_tag = content[0]
			if content_tag.tag=="group":
				content_tag = content_tag.find("content").find("graph")

			extract_info(content_tag)



		print "#### CHANNELS ####"
		pprint(dict(channel_dict))

		print "#### BASIC PARAMETERS ####"
		pprint(dict(basic_param_dict))

		print "#### ADVANCED PARAMETERS ####"
		pprint(dict(advanced_param_dict))

		print "#### UNGROUPED PARAMETERS/CHANNELS ####"
		pprint(dict(ungrouped_dict))

		for d in [(channel_dict,"channel"), (basic_param_dict, "basic"), (advanced_param_dict, "adv"), (ungrouped_dict, "ungrouped")]:
			write_dict_to_csv(d[0], str(i)+"_raw_"+d[1]+"_count", ",")
			merge_similar(d[0])
			write_dict_to_csv(d[0], str(i)+"_merged_"+d[1]+"_count", ",")

		for d in [channel_dict, basic_param_dict, advanced_param_dict, ungrouped_dict]:
			d.clear()

		i += 1

if __name__ == "__main__":
	main()