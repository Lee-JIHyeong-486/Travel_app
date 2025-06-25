# This code is for generating public/category_tree.json and id_map.json using cat.csv

import csv
import json
from collections import defaultdict

def add_path(tree, path):
    n = tree["Category"]
    for p in path:
        if not p in n:
            n.append(p)
        if not p in tree:
            tree[p] = []
        n = tree[p]

def id_mapping(id_map, path, id):
    id_map[path[-1]] = id

tree = {"Category":[]}
id_map = {}

with open("public/cat.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        category_path = row[1].strip().split(" > ")
        add_path(tree, category_path)
        id_mapping(id_map, category_path,row[0])

with open('public/category_tree.json',"w",encoding="utf-8") as f:
    json.dump(tree,f,indent=2,ensure_ascii=False)

with open('public/id_map.json',"w",encoding="utf-8") as f:
    json.dump(id_map, f, indent=2, ensure_ascii=False)