"""
1. saves images/annotations from categories
2. creates new json by filtering the main json file

coco_categories = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']

Expected Directory:
script.py
COCO[
    annotations
    val2017
    train2017
]
"""

from pycocotools.coco import COCO
import requests
import os
from os.path import join
from tqdm import tqdm
import json


class coco_category_filter:
    """
    Downloads images of one category & filters jsons
    to only keep annotations of this category
    """

    def __init__(self, json_path, _categ):
        self.coco = COCO(json_path)  # instanciate coco class
        self.categ = ''
        self.images = self.get_imgs_from_json(_categ)

    def get_imgs_from_json(self, _categ):
        """returns image names of the desired category"""
        # Get category ids
        self.catIds = self.coco.getCatIds(catNms=_categ)
        assert len(self.catIds) > 0, "[ERROR] cannot find category index for {}".format(_categ)
        print("catIds: ", self.catIds)
        # Get the corresponding image ids and images using loadImgs
        imgIds = []
        for c in self.catIds:
            imgIds += self.coco.getImgIds(catIds=c)  # get images over categories (logical OR)
        imgIds = list(set(imgIds))  # remove duplicates
        images = self.coco.loadImgs(imgIds)
        print(f"{len(images)} images of '{self.categ}' instances")
        return images

    def save_imgs(self, imgs_dir):
        """saves the images of this category"""
        print("Saving the images with required categories ...")
        os.makedirs(imgs_dir, exist_ok=True)
        # Save the images into a local folder
        for im in tqdm(self.images):
            img_data = requests.get(im['coco_url']).content
            with open(os.path.join(imgs_dir, im['file_name']), 'wb') as handler:
                handler.write(img_data)

    def filter_json_by_category(self, json_dir):
        """creates a new json with the desired category"""
        # {'supercategory': 'person', 'id': 1, 'name': 'person'}
        ### Filter images:
        print("Filtering the annotations ... ")
        imgs_ids = [x['id'] for x in self.images]  # get img_ids of imgs with the category (prefiltered)
        new_imgs = [x for x in self.coco.dataset['images'] if x['id'] in imgs_ids]  # select images by img_ids
        catIds = self.catIds
        ### Filter annotations
        new_annots = [x for x in self.coco.dataset['annotations'] if x['category_id'] in catIds]  # select annotations based on category id
        ### Reorganize the ids (note for reordering subset 1-N)
        #new_imgs, annotations = self.modify_ids(new_imgs, new_annots)
        ### Filter categories
        new_categories = [x for x in self.coco.dataset['categories'] if x['id'] in catIds]
        print("new_categories: ", new_categories)
        data = {
            "info": self.coco.dataset['info'],
            "licenses": self.coco.dataset['licenses'],
            "images": new_imgs,
            "annotations": new_annots,
            "categories": new_categories
        }
        print("saving json: ")
        with open(os.path.join(json_dir, "coco_annotation.json"), 'w') as f:
            json.dump(data, f)

    def modify_ids(self, images, annotations):
        """
        creates new ids for the images. I.e., maps existing image id to new subset image id and returns the dictionaries back
        images: list of images dictionaries

        images[n]['id']                                     # id of image
        annotations[n]['id']                                # id of annotation
        images[n]['id'] --> annotations[n]['image_id']      # map 'id' of image to 'image_id' in annotation
        """
        print("Reinitialicing images and annotation IDs ...")
        ### Images
        map_old_to_new_id = {}  # necessary for the annotations!
        for n, im in enumerate(images):
            map_old_to_new_id[images[n]['id']] = n + 1  # dicto with old im_ids and new im_ids
            images[n]['id'] = n + 1  # reorganize the ids
        ### Annotations
        for n, ann in enumerate(annotations):
            annotations[n]['id'] = n + 1
            old_image_id = annotations[n]['image_id']
            annotations[n]['image_id'] = map_old_to_new_id[old_image_id]  # replace im_ids in the annotations as well
        return images, annotations


def main(subset, year, root_dir, categories, experiment):
    json_file = join(root_dir, 'annotations/instances_' + subset + year + '.json')  # local path

    # Output files
    img_dir = join(root_dir, experiment, 'images')
    os.makedirs(img_dir, exist_ok=True)
    json_dir = join(root_dir, experiment, 'annotations')
    os.makedirs(json_dir, exist_ok=True)

    # Methods
    coco_filter = coco_category_filter(json_file, categories)  # instantiate class
    coco_filter.filter_json_by_category(json_dir)
    # coco_filter.save_imgs(img_dir)

if __name__ == '__main__':
    subset, year = 'train', '2017'  # val - train
    # root_dir = '/home/jason/1_Tommy/COCO_extract/COCO2017'
    root_dir = '/media/jason/9400F87F00F8699E/Yolact/COCO_extract/COCO2017'
    experiment = "COCO2017train"
    categories = ['person', 'bench', 'motorcycle', 'car', 'truck','bus','fire hydrant']  # can be multiple categories
    main(subset, year, root_dir, categories, experiment)