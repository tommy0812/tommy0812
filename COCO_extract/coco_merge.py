import json

PATH = "/media/jason/9400F87F00F8699E/Yolact/COCO_extract/COCO2017/annotations/"

with open(PATH+"COCO2017val_PVB.json", "r") as jsonFile:
    data = json.load(jsonFile)

    annots = data['annotations']
    for annot in annots:
        if annot['category_id'] == 2:
            annot['category_id'] = 103
        elif annot['category_id'] == 3:
            annot['category_id'] = 102
        elif annot['category_id'] == 4:
            annot['category_id'] = 103
        elif annot['category_id'] == 6:
            annot['category_id'] = 102
        elif annot['category_id'] == 8:
            annot['category_id'] = 102

print("saving json 0 : ")
with open(PATH+"COCO2017val_PVB_3_classes.json", 'w') as f:
    json.dump(data, f)

PRE_DEFINE_CATEGORIES = [{"supercategory": "none", "id": 0, "name": "__background__"},
                       { "supercategory": "none", "id": 1, "name": "person"},
                       { "supercategory": "none", "id": 2, "name": "vehicle"},
                       { "supercategory": "none", "id": 3, "name": "bike"},]

with open(PATH+"COCO2017val_PVB_3_classes.json", 'r') as f:
    data_ = json.load(f)
    annots = data_['annotations']
    for annot in annots:
        if annot['category_id'] == 102:
            annot['category_id'] = 2     
        if annot['category_id'] == 103:
            annot['category_id'] = 3

    data_['categories'] = PRE_DEFINE_CATEGORIES

print("saving json 1 : ")
with open(PATH+"COCO2017val_PVB_3_classes.json", 'w') as f:
    json.dump(data_, f)
        
