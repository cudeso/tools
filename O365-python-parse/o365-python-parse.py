import csv
import json
import sys
import termtables as tt

''' 
    Koen Van Impe
    Parse Unified Audit Log
    
'''

o365_operations = {
    "Set-Mailbox": { "label": "Modify settings" },
    "Set-MailboxPlan": { "label": "Modify plan (IMAP? POP?)" },
    "Set-OwaMailboxPolicy": { "label": "Modify Outlook Web" },
    "Add-MailboxPermission": { "label": "Add mailbox permissions" },
}
o365_data = []
o365_header = ["Time", "ClientIP", "Operation", "ResultStatus", "User", "Object"]
o365_unique_operations = {}
o365_client_ip =  {}
o365_originatingserver = {}
with open('auditrecords.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    failed_line_count = 0
    start_log = ""
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
            try:
                creationtime = operation = userid = originatingserver = clientip = resultstatus = ""
                auditdata = json.loads(row[0].strip().replace("NT AUTHORITY\SYSTEM","NT AUTHORITY\\SYSTEM"))            
                creationtime = auditdata["CreationTime"]
                if start_log == "":
                    start_log = creationtime
                operation = auditdata["Operation"]
                userid = auditdata["UserId"]
                if "OriginatingServer" in auditdata:
                    originatingserver = auditdata["OriginatingServer"]
                    if originatingserver in o365_originatingserver:
                        o365_originatingserver[originatingserver] += 1
                    else:
                        o365_originatingserver[originatingserver] = 1
                if "ResultStatus" in auditdata:
                    resultstatus = auditdata["ResultStatus"]
                if "ObjectId" in auditdata:
                    objectid = auditdata["ObjectId"]
                    if len(objectid) > 25:
                        objectid = objectid[len(objectid)-25:]
                if "ClientIP" in auditdata:
                    clientip = auditdata["ClientIP"]
                    if clientip in o365_client_ip:
                        o365_client_ip[clientip] += 1
                    else:
                        o365_client_ip[clientip] = 1
                if operation in o365_unique_operations:
                    o365_unique_operations[operation] += 1
                else:
                    o365_unique_operations[operation] = 1
                if operation in o365_operations:
                    o365_data.append([creationtime, clientip, operation, resultstatus, userid, objectid])
                else:
                    # Future expansion: add explanation of operation-key
                    o365_data.append([creationtime, clientip, operation, resultstatus, userid, objectid])
            except:
                #print(auditdata)
                failed_line_count += 1
                continue
            
            line_count += 1

    # Print details
    tt.print(o365_data, header=o365_header)

    # Print Client IPs
    tt_data = []
    tt_header = ["Client IP", "Count"]
    o365_client_ip = sorted(o365_client_ip.items(), key=lambda x: x[1], reverse=True)
    for el in o365_client_ip:
        tt_data.append([el[0], el[1]])
    tt.print(tt_data, header=tt_header)

    # Print Operations
    tt_data = []
    tt_header = ["Operation", "Count"]
    o365_unique_operations = sorted(o365_unique_operations.items(), key=lambda x: x[1], reverse=True)
    for el in o365_unique_operations:
        tt_data.append([el[0], el[1]])
    tt.print(tt_data, header=tt_header)

    print(f'Processed {line_count} lines. {failed_line_count} lines failed processing. \nLog data from {start_log} until {creationtime}')
    
