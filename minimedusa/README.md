# Intro

Get the data from https://minimedusa.lol/

Configuration
* Output file, where to write the results.
  * write_to_minimedusa_file_output = True
  * minimedusa_file_output = "minimedusa_output.txt"
* Do Passive DNS lookup with CIRCL
  * do_pdns= True
  * Add your CIRCL Passive DNS credentials : `pypdns = pypdns.PyPDNS(basic_auth=('USERNAME','PASSWORD'))`
* Do reverse DNS
  * do_rdns = True
  * Set the DNS server to use `rdns_server`

If you enable passive dns or dns you can also highlight domains for a specific TLD. Specify the TLD in `tld_check`.

# Output

```
MegaMedusa config: Parsed 38307 IPs (2025-03-13)

Records
------------
IP|ASN|CC|AS Name|RDNS|Domains
72.10.160.170|36666|CA|GTCOMM, CA|None|[]
154.236.177.101|36992|EG|ETISALAT-MISR, EG|HOST-101-177.236.154.nile-online.net.|[]
203.190.44.225|45317|ID|JATARA-AS-ID Jaringan Lintas Utara, PT, ID|None|[]
72.10.160.174|36666|CA|GTCOMM, CA|None|[]
115.127.5.146|24342|BD|BRAC-BDMAIL-AS-BD BRACNet Limited, BD|host-146.bracnet.net.|[]
72.10.164.178|36666|CA|GTCOMM, CA|None|[]
186.148.195.165|269984|VE|CORPORACION MATRIX TV, C.A., VE|None|[]
103.39.49.156|63501|ID|MEGAHUB-AS-ID PT Mega Mentari Mandiri, ID|ip-103-39-49-156.mentari.net.id.|[]
23.122.184.9|7018|US|ATT-INTERNET4, US|23-122-184-9.lightspeed.miamfl.sbcglobal.net.|['photos.lilcmac.xyz', 'panel.lilcmac.xyz', 'fenrus.lilcmac.xyz', 'portainer.lilcmac.xyz', 'plex.lilcmac.xyz']
156.200.116.67|8452|EG|TE-AS TE-AS, EG|host-156.200.116.67.tedata.net.|[]
...

TLD checks
------------
(best to ignore Cloudflare, Google, etc. hits | grep -v ^172.6)
54.38.217.92|['brigittechardome.be', 'www.brigittechardome.be', 'etslousberg.be', 'scuderia-events.be']
63.141.128.22|['tecline.be', 'additto-lubricants.be']
160.153.0.1|['digiflare.be']
...
```