import json
import os

list_of_senz = []

path_txt = "\cenz.txt"
path_json = "\cenz.json"

with open(os.path.dirname(os.path.abspath(__file__)) + path_txt, encoding="utf-8") as r:
	for i in r:
		n = i.lower().split("\n")[0]
		if n != "":
			list_of_senz.append(n)

with open(os.path.dirname(os.path.abspath(__file__)) + path_json, "w", encoding = "utf-8") as e:
	json.dump(list_of_senz, e)
