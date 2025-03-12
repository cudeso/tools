import requests
import socket
import pypdns
import json
import dns.resolver
from datetime import datetime

write_to_minimedusa_file_output = True
minimedusa_file_output = "minimedusa_output.txt"

### Which IP list to use from Minimedusa?
#       official, without private:https://minimedusa.lol/ip/current-cleaned.txt
#       official:https://minimedusa.lol/ip/current.txt
#       unofficial,without private:https://minimedusa.lol/ip/current-scraped-cleaned.txt
#       unofficial:https://minimedusa.lol/ip/current-scraped.txt
source_minimedusa = "https://minimedusa.lol/ip/current-scraped-cleaned.txt"

### TeamCymru whois server
whois_server = "whois.cymru.com"
whois_port = 43

### CIRCL Passive DNS API
pypdns = pypdns.PyPDNS(basic_auth=('USERNAME','PASSWORD'))

### DNS server for (optional) RDNS
rdns_server = "8.8.8.8"

def get_minimedusa(url):
    if url:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.text.split("\n")
            else:
                return False
        except Exception as e:
            return False
    else:
        return False

def get_rdns(ip, rdns_server):
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [rdns_server]
        answer = resolver.resolve_address(ip)
        return str(answer[0])
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
        return None

def minimedusa_query(ips, whois_server, whois_port, pypdns, rdns_server, rdns=False):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((whois_server, whois_port))
        query = "begin\nverbose\n" + "\n".join(ips) + "\nend\n"
        s.sendall(query.encode('utf-8'))
        response = b""
        while True:
            data = s.recv(4096)
            if not data:
                break
            response += data

    lines = response.decode('utf-8').strip().split('\n')
    header = ["asn", "ip", "bgpprefix", "cc", "registry", "allocated", "as_name"]

    result = {}
    for line in lines[2:]:
        values = line.split('|')
        values = [v.strip() for v in values]
        ip = values[1]  # IP is in column 1
        print("Processing IP: {}, remaining {}".format(ip, len(result) - len(lines[2:])))
        result[ip] = dict(zip(header, values))

        result[ip]["domains"] = []
        result[ip]["rdns"] = None
        try:
            # CIRCL Passive DNS
            pdns = pypdns.rfc_query(ip)
            if len(pdns) > 0:
                for record in pdns:
                    if record.rrtype == "A":
                        result[ip]["domains"].append(record.rdata)

            # Reverse DNS
            if rdns:
                result[ip]["rdns"] = get_rdns(ip, rdns_server)
        except Exception as e:
            result[ip]["domains"] = []
            result[ip]["rdns"] = None
    return result

if __name__ == '__main__':
    minimedusa = get_minimedusa(source_minimedusa)
    print("Got {} IPs from Minimedusa".format(len(minimedusa)))
    minimedusa_dict = minimedusa_query(minimedusa, whois_server, whois_port, pypdns, rdns_server, rdns=True)
    
    title = "MegaMedusa config: Parsed {} IPs ({})".format(len(minimedusa_dict), datetime.now().date())
    summary = "Records\n------------\n"
    summary += "IP|ASN|CC|AS Name|RDNS|Domains\n"
    for el in minimedusa_dict:
        entry = minimedusa_dict[el]
        summary += "{}|{}|{}|{}|{}|{}\n".format(el, entry["asn"], entry["cc"], entry["as_name"], entry["rdns"], entry["domains"])
    summary += "\n"

    if write_to_minimedusa_file_output:
            summary = title + "\n\n" + summary + "\n"
            with open(minimedusa_file_output, 'w') as file:
                file.write(summary)

