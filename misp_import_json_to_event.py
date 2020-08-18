from pymisp import ExpandedPyMISP, MISPEvent, MISPOrganisation, MISPAttribute, MISPTag, MISPObject
from datetime import date
import time
import json
import uuid
import sys

misp_url = ""
misp_key = ""
misp_verifycert = False
insert_sleep = 0.25

if not misp_verifycert:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
api = ExpandedPyMISP(misp_url, misp_key, misp_verifycert)

if not len(sys.argv) >= 3:
    print("Requires at least two arguments: %s <JSON file> <create organisation> [<misp event title>]" % sys.argv[0])
    sys.exit()
if len(sys.argv) == 4:
    event_import_info = sys.argv[3]
else:
    event_import_info = False

json_import = sys.argv[1]
event_import_org = sys.argv[2]          
event_import_uuid = str(uuid.uuid4())   # Unique ID
event_import_date = date.today()        # Create event with current data
event_import_distribution = 2           # Connected


# Check if organisation already exist
org = MISPOrganisation()
try:
    org.id = api.get_organisation(event_import_org, pythonify=True).id
except:
    # We need to create a new one
    org_new = MISPOrganisation()
    org_new.name = event_import_org
    org_new.uuid = str(uuid.uuid4())
    org_new.type = "CSIRT"
    org_new.sector = "Government"
    org.id = api.add_organisation(org_new, pythonify=True).id


# Create the MISP event by loading the JSON file
# This will not add the attributes, but does add the event tags and galaxies
# We also add a random UUID for uniqueness
event = MISPEvent()
event.load_file(json_import)
event.uuid = event_import_uuid
if not event_import_info:
    event_import_info = event.info
event.info = event_import_info
event.date = event_import_date
event.distribution = event_import_distribution
event.orgc = api.get_organisation(org, pythonify=True)
event = api.add_event(event, pythonify=True)


# Check if the event was created
if (int(event.id) > 0):
    # Yes, read the content and add attributes and objects
    # Include a sleep so for the scheduler
    count_attributes = 0
    count_objects = 0
    with open(json_import) as json_file:
        data = json.load(json_file)

        if 'Attribute' in data.get("response")[0].get("Event"):
            attributes = data.get("response")[0].get("Event").get("Attribute")
            for attribute in attributes:
                misp_tag = []
                if 'Tag' in attribute:
                    for tag in attribute.get('Tag'):
                        misp_tag.append(tag.get('name'))
                
                mispattribute = MISPAttribute()
                mispattribute.from_dict(**{
                        'value': attribute.get("value"),
                        'category': attribute.get("category"),
                        'type': attribute.get("type"),
                        'to_ids': attribute.get("to_ids"),
                        'comment': attribute.get("comment"),
                        'Tag': misp_tag
                        })
                res = api.add_attribute(event, mispattribute)
                time.sleep(insert_sleep)
                count_attributes = count_attributes + 1

        if 'Object' in data.get("response")[0].get("Event"):
            objects = data.get("response")[0].get("Event").get("Object")
            for obj in objects:
                misp_object = MISPObject(obj.get('name'))
                if 'Attribute' in obj:
                    for attribute in obj.get('Attribute'):
                        misp_object.add_attribute(attribute.get('object_relation'), type=attribute.get('type'), category=attribute.get('category'), value=attribute.get('value'), to_ids=attribute.get('to_ids'), comment=attribute.get('comment') )
                api.add_object(event, misp_object)
                time.sleep(insert_sleep)
                count_objects = count_objects + 1
    
    # Now publish the event
    api.publish(event)

    # Print result
    print("Event %s (%s) created with %s attributes and %s objects." % (event_import_info, event.id, count_attributes, count_objects))

