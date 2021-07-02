#!/usr/bin/env python3

import yaml
import glob

datasources = glob.glob("attack-datasources/contribution/*.yml")
outfile = open("attack-datasources.txt", "a")

for yml in datasources:
  with open(yml, 'r') as stream:
    try:        
        datasource = yaml.safe_load(stream)
        #print("{0} ; {1}".format(datasource["name"], datasource["definition"]))
        outfile.write("Data source: {0}\n".format(datasource["name"]))
        outfile.write("{0} ; {1}\n".format(datasource["name"], datasource["definition"]))
        for component in datasource["data_components"]:
           #print("{0} ; {1}".format(component["name"], component["description"]))
           outfile.write("{0} ; {1}\n".format(component["name"], component["description"]))
    except yaml.YAMLError as exc:
        print(exc)

outfile.close()
