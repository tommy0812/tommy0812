import os
import cv2
import numpy as np
import xml.etree.ElementTree as ET
import yaml
import argparse

def point_Area(input_path, points, color):
	img = cv2.imread(input_path)
	zeros = np.zeros((img.shape), dtype=np.uint8)
	mask = cv2.fillPoly(zeros, points, color)
	# print(mask.shape)
	return points, mask


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="config")
	parser.add_argument(
		"--config",
		nargs="?",
		type=str,
		default="label_tommy.yaml",
		# default="label.yaml",
		help="Configuration file to use",
		)
	args = parser.parse_args()
	with open(args.config) as fp:
		cfg = yaml.safe_load(fp)
	

	# ROOT_DIR_LABEL = "/media/jason/9400F87F00F8699E/Tommy_TriSDNet/c2l_train_xml/"
	# ROOT_DIR_IMG = "/media/jason/9400F87F00F8699E/Tommy_TriSDNet/c2l_train/"
	ROOT_DIR_LABEL = "/media/jason/9400F87F00F8699E/Tommy_TriSDNet/c2l_train_xml/"
	ROOT_DIR_IMG = "/media/jason/9400F87F00F8699E/Tommy_TriSDNet/c2l_train/"
	f = open("train_label.txt")
	line = f.readline()

	
	while line:
		img_name = line.replace(".xml", "")
		img_name = img_name.replace("\n", "")
		tree = ET.parse(ROOT_DIR_LABEL + img_name + ".xml")
		
		root = tree.getroot()

		im_path = ROOT_DIR_IMG + img_name + ".png"
		# im_path = ROOT_DIR_IMG + img_name + ".jpg"
		img = cv2.imread(im_path)
		mask_img = np.zeros((img.shape), dtype=np.uint8)
		# print(mask_img.shape)

		for objects in root.findall('object'):

			label_name = objects.find('attribution').text

			if label_name in cfg["label"].keys():
				color = tuple(cfg["label"][label_name]["color"])

				points = objects.find('segmentation').text
				if points == "None":
					continue

				cnt = 0
				for j in range(len(points)):
					if points[j] == "[":
						cnt += 1

				new_points = points.replace("[", "")
				new_points = new_points.replace("]", "")
				# points_array = np.fromstring(new_points, dtype=int, sep=',') # from ezlabel format

				points_array = np.fromstring(new_points, dtype=float, sep=',') # from labelme format
				points_array = points_array.astype(int) # from labelme format

				points_array = points_array.reshape(1, cnt-1, 2)
				
				_, mask = point_Area(im_path, points_array, color)

				# classes = np.unique(mask)
				# print(classes)
				mask_img += mask
			else:
				print("more classes")
				
		


																									  

		cv2.imwrite("/media/jason/9400F87F00F8699E/Tommy_TriSDNet/test0814/" + img_name +  ".png", mask_img)
		# classes = np.unique(mask_img)
		# print(classes)
		line = f.readline()

	f.close()


