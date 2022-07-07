import json

# aws ec2 describe-network-acls --no-paginate > acl_list_life.json
describe_network_acls = "acl_list_life.json"

f_acl = open(describe_network_acls)
data = json.load(f_acl)["NetworkAcls"]

print("| acl_name | vpc_id | subnet_ids | rule_no | rule_action | direction | protocol | cidr_block | port_from | port_to |")
print("|----|----|----|----|----|----|----|----|----|----|")

for el in data:

    subnet = ""
    if "Associations" in el and len(el["Associations"]) > 0:
        for net in el["Associations"]:
            subnet = "{} {}".format(subnet, net["SubnetId"])

    tags = ""
    if "Tags" in el and len(el["Tags"]) > 0:
        for tag in el["Tags"]:
            tags = "{} {}".format(tags, tag["Value"])

    vpc_id = el["VpcId"]

    entries = el["Entries"]
    for entry in entries:
        port_from = port_to = "Any"
        if "PortRange" in entry:
            port_from = entry["PortRange"]["From"]
            port_to = entry["PortRange"]["To"]

        direction = "igress"
        cidr_block = entry["CidrBlock"]
        if entry["Egress"] is True:
            direction = "egress"

        protocol = entry["Protocol"]
        if protocol == "-1":
            protocol = "Any"
        elif protocol == "6":
            protocol = "tcp"
        elif protocol == "17":
            protocol = "udp"

        rule_number = entry["RuleNumber"]
        rule_action = entry["RuleAction"]

        print("| {} | {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(tags, vpc_id, subnet, rule_number, rule_action, direction, protocol, cidr_block, port_from, port_to))
    print("|----|----|----|----|----|----|----|----|----|----|")
