import requests
import socket
import pypdns
import json
import dns.resolver
from datetime import datetime

write_to_minimedusa_file_output = True
minimedusa_file_output = "minimedusa_output.txt"

do_pdns= True
do_rdns = True

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
tld_check = [".be"]
tld_highlight = {}

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

def minimedusa_query(ips, whois_server, whois_port, pypdns, do_pdns, rdns_server, do_rdns):
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
        print("Processing IP: {}".format(ip))
        result[ip] = dict(zip(header, values))

        result[ip]["domains"] = []
        result[ip]["rdns"] = None
        try:
            # Passive DNS
            if do_pdns:
                pdns = pypdns.rfc_query(ip)
                if len(pdns) > 0:
                    for record in pdns:
                        if record.rrtype == "A":
                            result[ip]["domains"].append(record.rdata)
                            for tld in tld_check:
                                if record.rdata.endswith(tld):
                                    if ip in tld_highlight:
                                        tld_highlight[ip].append(record.rdata)
                                    else:
                                        tld_highlight[ip] = [record.rdata]

            # Reverse DNS
            if do_rdns:
                result[ip]["rdns"] = get_rdns(ip, rdns_server)

        except Exception as e:
            result[ip]["domains"] = []
            result[ip]["rdns"] = None
    return result

if __name__ == '__main__':
    minimedusa = get_minimedusa(source_minimedusa)
    print("Got {} IPs from Minimedusa".format(len(minimedusa)))
    minimedusa_dict = minimedusa_query(minimedusa, whois_server, whois_port, pypdns, do_pdns, rdns_server, do_rdns)
    
    title = "MegaMedusa config: Parsed {} IPs ({})".format(len(minimedusa_dict), datetime.now().date())
    summary = "Records\n------------\n"
    summary += "IP|ASN|CC|AS Name|RDNS|Domains\n"
    for el in minimedusa_dict:
        entry = minimedusa_dict[el]
        summary += "{}|{}|{}|{}|{}|{}\n".format(el, entry["asn"], entry["cc"], entry["as_name"], entry["rdns"], entry["domains"])
    summary += "\n"
    summary += "\n"
    if do_pdns or do_rdns:
        summary += "TLD checks\n------------\n"
        summary += "(best to ignore Cloudflare, Google, etc. hits | grep -v ^172.6)\n"
        for el in tld_highlight:
            summary += "{}|{}\n".format(el, tld_highlight[el])
        summary += "\n"
    
    if write_to_minimedusa_file_output:
            summary = title + "\n\n" + summary + "\n"
            with open(minimedusa_file_output, 'w') as file:
                file.write(summary)

