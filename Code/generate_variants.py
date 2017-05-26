import xml.etree.ElementTree as ET
from collections import defaultdict
import os
import glob
import fnmatch
from pprint import pprint
import string
import subprocess
import itertools
import numpy as np

PATHS = ['C:\Users\Andreea\Documents\Substance Project\SubstanceDatabase2-updated\Substance_Database_2.1\Substance_Database_2.1_BitmapBased_Sbs\Substance_Database_2.1_BitmapBased_Sbs']
OUTPUT_DIR = "C:\Users\Andreea\Documents\Substance Project\Bitmap Variations"
BATCHTOOL_DIR = "C:\Program Files\Allegorithmic\Substance BatchTools 6"
RESOURCE_DIR = "C:\Program Files\Allegorithmic\Substance Designer 6\\resources\packages"
PARAMS_OF_INTEREST = ["Contrast", "Hue Shift", "Saturation", "Luminosity"]

TREE = None
CONTENT_TAG = None
VAR_COUNT = 1

f = open("variant_list.csv", "w+")

def format_identifier(s):
	return string.capwords(s.replace("_"," "))

def setup_path(path):

	sbs_files = []
	for dirpath, dirnames, files in os.walk(path):
		dirnames[:] = [d for d in dirnames if d not in [".autosave", "PBR_Materials"]]
		for f in fnmatch.filter(files, '*.sbs'):
			sbs_files += [os.path.join(dirpath, f)]
	return sbs_files


def cook_and_render(variant, filename):
	global VAR_COUNT
	fulldir = OUTPUT_DIR+"\\Results1\\"+filename
	
	sbs_output_name = OUTPUT_DIR+"\\Resources\\"+filename +"_v_"+str(VAR_COUNT)+".sbs"
	#print sbs_output_name

	if not os.path.exists(fulldir):#+"\\renders\\"+filename+"_v_"+str(VAR_COUNT)):
		os.makedirs(fulldir)#+"\\renders\\"+filename+"_v_"+str(VAR_COUNT))

	TREE.write(sbs_output_name, encoding="UTF-8")	
	

	subprocess.call([BATCHTOOL_DIR+"/sbscooker.exe", "--inputs", sbs_output_name, "--includes", RESOURCE_DIR, "--output-path", fulldir])
	os.remove(sbs_output_name)

	sbsar_output_name = fulldir+"\\"+filename+"_v_"+str(VAR_COUNT)+".sbsar"
	# print command
	#print sbsar_output_name
	if os.path.isfile(sbsar_output_name):
		subprocess.call([BATCHTOOL_DIR+"\sbsrender.exe", "render", "--inputs", sbsar_output_name, "--output-format-compression", "dxt1", "--output-format", "webp", "--output-path", fulldir+"\\", "--output-name",r"{inputName}_{outputNodeName}", "--input-graph-output", "basecolor"])
		os.remove(sbsar_output_name)
		# for fn in glob.glob(fulldir+"\\renders\\"+filename+"_v_"+str(VAR_COUNT)+"\*.webp") :
		# 	print fn
		# 	if "basecolor" not in os.path.basename(fn):
		# 		os.remove(fn)
		VAR_COUNT += 1
	else:
		return -1

varc = 1
varc1 = 1

def sbs_generation(variant, index, param_list, filename):
	golbal varc, varc1, f

	if index == len(param_list):
		print "Writing variant", varc,":", variant
		# if (float(variant[0]) > 0.7 and float(variant[1]) < -0.7) or (float(variant[0]) < 0.3 and float(variant[1]) > 0.7):
			
		# # print varc, " : ", variant, "\n"
		# # replace_values(param_list, variant)
		# # ret = cook_and_render(variant, filename)
		# # if ret == -1:
		# # 	return None
		# 	f.write("REJECTED,")
		f.write(str(varc)+","+",".join(variant)+"\n")
		varc += 1
		return variant
	if variant is not None:
		for v in param_list[index][1]:
			
			variant.append(v)
			variant = sbs_generation(variant, index+1, param_list, filename)
			if variant is None:
				break
			else:
				variant = variant[:-1]
			
	return variant


def replace_values(param_list, variant):

	p_list = [p[0] for p in param_list]
	output_channels = CONTENT_TAG.find("paraminputs")
	for channel in output_channels:

		name = format_identifier(channel.find("identifier").attrib['v'])
		if name in p_list:
			value_to_write = variant[p_list.index(name)]

			dval_tag = channel.find("defaultValue")
			if dval_tag is not None:
				for v in dval_tag:
					dvalue = v.find("value").set('v', value_to_write)
				dwidget_tag = channel.find("defaultWidget")
				if dwidget_tag is not None:
					widget_name = dwidget_tag.find("name").attrib['v']
					if widget_name in ["slider", "color", "angle", "dropdownlist"]:
						options = dwidget_tag.find("options")

						for option in options:

							if option.find("name").attrib['v'] == "parameters":
								prev_value = option.find("value").attrib['v']
								option.find("value").set('v', value_to_write+prev_value[:1])
							elif option.find("name").attrib['v'] == "default":
								option.find("value").set('v', value_to_write)


def extract_info():

	param_list = []

	print "Texture Name:", CONTENT_TAG.find("identifier").attrib['v']

	output_channels = CONTENT_TAG.find("paraminputs")
	for channel in output_channels:
		entry = []

		name = format_identifier(channel.find("identifier").attrib['v'])
		group_tag = channel.find("group")
		group = group_tag.attrib['v'] if group_tag is not None else ""

		if "Basic" in group:
			if name in PARAMS_OF_INTEREST:
				entry.append(name)
				

				dwidget_tag = channel.find("defaultWidget")
				if dwidget_tag is not None:
					widget_name = dwidget_tag.find("name").attrib['v']
					if widget_name in ["slider", "color", "angle"]:
						options = dwidget_tag.find("options")
						low, high = 0, 0

						for option in options:
							if option.find("name").attrib['v'] == "min":
								low = float(option.find("value").attrib['v'])
							elif option.find("name").attrib['v'] == "max":
								high = float(option.find("value").attrib['v'])

						if name == "Luminosity":
							bins = np.linspace(low+0.2, high-0.2, num=7)
						elif name == "Contrast":
							bins = np.linspace(low+0.2, high-0.2, num=11)
						else:
							bins = np.linspace(low, high, num=11)
						entry.append(['{:.2f}'.format(x) for x in bins])

				param_list.append(entry)


	pprint(param_list)
	print "##################\n"
	return param_list

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

	global TREE, CONTENT_TAG, VAR_COUNT, f

	for path in PATHS:

		sbs_files = setup_path(path)

		for file in sbs_files[0:]:

			filename = file.split("\\")[-1].split(".")[0]

			print "Parsing: ", file, "\n"

			TREE = ET.parse(file)
			root = TREE.getroot()
			content = root.find("content")
			CONTENT_TAG = content[0]
			if CONTENT_TAG.tag=="group":
				CONTENT_TAG = CONTENT_TAG.find("content").find("graph")

			f.write("Luminosity,"+"Contrast,"+"Hue Shift,"+"Saturation\n")
			sbs_generation([], 0, extract_info(), filename)
			VAR_COUNT = 1
			f.close()
if __name__ == "__main__":
	main()