import json

# aws ec2 describe-security-groups --no-paginate > all_sg.json
# aws ec2 describe-instances --no-paginate > all_instances.json

describe_network_sgs = "all_sg.json"
describe_instances = "all_instances.json"

f_acl = open(describe_network_sgs)
data = json.load(f_acl)["SecurityGroups"]

print("| description | group_name | group_id | direction | protocol | ip_range | port_from | port_to | instance_name | Comment |")
print("|---|----|---|---|---|---|---|---|---|---|")

for el in data:
    description = el["Description"][:50]
    group_name = el["GroupName"]
    group_id = el["GroupId"]

    # Look up the instance
    f_instance = open(describe_instances)
    data_instance = json.load(f_instance)["Reservations"]
    instance_name = instance_state = ""
    for instance in data_instance:        
        if "Instances" in instance and "SecurityGroups" in instance["Instances"][0]:
            instance_id = instance["Instances"][0]["InstanceId"]
            # Search in security groups
            for instance_group in instance["Instances"][0]["SecurityGroups"]:
                if instance_group["GroupId"] == group_id:
                    tags = instance["Instances"][0]["Tags"]
                    for t in tags:
                        if t["Key"] == "Name" and t["Value"] not in instance_name:
                            instance_name = "{} {} ({})".format(instance_name, t["Value"], instance["Instances"][0]["State"]["Name"])
        # Search in attachments (such as network interface)
        if "Instances" in instance and "NetworkInterfaces" in instance["Instances"][0]:
            for interface in instance["Instances"][0]["NetworkInterfaces"]:
                if "Groups" in interface:
                    #print("hier")
                    for interface_group in interface["Groups"]:
                        if interface_group["GroupId"] == group_id:
                            tags = instance["Instances"][0]["Tags"]
                            for t in tags:
                                if t["Key"] == "Name" and t["Value"] not in instance_name:
                                    instance_name = "{} {} ({})".format(instance_name, t["Value"], instance["Instances"][0]["State"]["Name"])

    
    if "IpPermissions" in el:
        for perm in el["IpPermissions"]:
            direction = "ingress"
            port_from = port_to = ""
            if "FromPort" in perm:
                port_from = perm["FromPort"]
            else:
                port_from = "Any"
            if "ToPort" in perm:
                port_to = perm["ToPort"]
            else:
                port_to = "Any"
            protocol = perm["IpProtocol"]
            if protocol == "-1":
                protocol = "Any"
            elif protocol == "6":
                protocol = "tcp"
            elif protocol == "17":
                protocol = "udp"            
            ip_range = ""
            if "IpRanges" in perm:
                for range in perm["IpRanges"]:
                    description_range = ""
                    if "Description" in range:
                        description_range = " ({})".format(range["Description"])                
                    ip_range = "{} {}{}".format(ip_range, range["CidrIp"], description_range)
            else:
                ip_range = "Any"                
            if len(instance_name.strip()) < 1:
                instance_name = "Not used (?)"
            print("| {} | {} | {} | {} | {} | {} | {} | {} | {} | |".format(description, group_name, group_id, direction, protocol, ip_range, port_from, port_to, instance_name))

    if "IpPermissionsEgress" in el:
        for perm in el["IpPermissionsEgress"]:
            direction = "egress"
            port_from = ""
            port_to = ""
            if "FromPort" in perm:
                port_from = perm["FromPort"]
            else:
                port_from = "Any"                
            if "ToPort" in perm:
                port_to = perm["ToPort"]
            else:
                port_to = "Any"                
            protocol = perm["IpProtocol"]
            if protocol == "-1":
                protocol = "Any"
            elif protocol == "6":
                protocol = "tcp"
            elif protocol == "17":
                protocol = "udp"            
            ip_range = ""
            if "IpRanges" in perm:
                for range in perm["IpRanges"]:
                    description_range = ""
                    if "Description" in range:
                        description_range = " ({})".format(range["Description"])
                    ip_range = "{} {}{}".format(ip_range, range["CidrIp"], description_range)
            else:
                ip_range = "Any"

            if len(instance_name.strip()) < 1:
                instance_name = "Not used (?)"
            print("| {} | {} | {} | {} | {} | {} | {} | {} | {} | |".format(description, group_name, group_id, direction, protocol, ip_range, port_from, port_to, instance_name))

    print("|---|----|---|---|---|---|---|---|---|---|")

