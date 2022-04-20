Some notes from the [Mandiant M-Trends 2022](https://www.mandiant.com/media/15671) report.


# Statistics 

## Detection by source

- There was an increase in external notification of intrusions in 2021 compared to 2020. However, awareness of most intrusions continues to come about through internal detections
- In Americas, organizations detected intrusions internally in 60% of cases in 2021
- In EMEA, organizations were notified of an incident by an external entity in 62% of intrusions in 2021

## Dwell Time

- The global median dwell time for 2021 was 21 days compared to 24 days in 2020. This 13% improvement in global median dwell time was comprised of noteworthy changes in relation to source of detection. 
- In 2021, fewer investigations in EMEA were ransomware related—17% compared to 22% in 2020

## Industry Targeting

 - In 2021 business/professional services and financial were the top targeted industries across the globe. Retail and hospitality, healthcare and high tech round out the top five industries favored by adversaries.


 ## Initial Infection Vector

 - Exploits remained the most frequently identified initial infection vector in 2021. In intrusions where the initial infector vector was identified, 37% started with an exploit—an 8-percentage point increase over 2020.
- Supply chain compromise was the second most prevalent initial infection vector identified in 2021. When the initial infection vector was identified, supply chain compromise accounted for 17% of intrusions in 2021 compared to less than 1% in 2020. Further, 86% of supply chain compromise intrusions in 2021 were related to the SolarWinds breach and SUNBURST.1
- In 2021, Mandiant experts observed an uptick in intrusions with an initial infection vector due to a prior compromise. These intrusions include handoffs from one group to another and prior malware infections. Prior compromises accounted for 14% of intrusions where the initial infection vector was identified.
- Mandiant experts observed far fewer intrusions initiated via phishing in 2021. When the initial compromise was identified, phishing was the vector in only 11% of intrusions in 2021 compared to 23% in 2020. This speaks to organizations’ ability to better detect and block phishing emails as well as enhanced security training of employees to recognize and report phishing attempts.

## Operations

### Financial gain

- FinanciallymotivatedintruDsatiaoTnhsefctontinuetobeamainstayin2021,withInvolvedExploits adversaries seeking monetary gain in 3 out of 10 intrusions through methods such as extortion, ransom, payment card theft and illicit transfers. 

### Data theft

- Threat actors continuIenvtoolvepdrEioxprilotitzse data theft as a primary mission objective. In 2021, Mandiant identified data theft in 29% of intrusions.

### Compromised Architecture and Insider Threat

- In 2021 Mandiant experts observed a slight uptick in compromises that likely served only to compromise architecture for further attacks.

### Exploit Activity

- Adversaries frequently leveraged exploits in 2021 with 30% of all intrusions involving exploit activity.

## Malware

- Of the 733 newly tracked malware families in 2021, the top five categories were backdoors (31%), downloaders (13%), droppers (13%), ransomware (7%), launchers (5%) and credential stealers (5%).

- The malware families seen most frequently during intrusions investigated by Mandiant experts were BEACON, SUNBURST, METASPLOIT, SYSTEMBC, LOCKBIT and RYUK.

- RYUK and LOCKBIT were the most used ransomware families during intrusions investigated by Mandiant in 2021.

## Operating systems

- Previous trends in operation system effectiveness continued in 2021 as newly tracked as well as observed malware families were predominately effective on Windows. However, malware families impacting Linux became more prevalent in 2021

## ATT&CK techniques

1. T1027: Obfuscated Files or Information 51.4%
2. T1059: Command and Scripting Interpreter 44.9%
3. T1071: Application Layer Protocol 36.8%
4. T1082: System Information Discovery 31.8%
5. T1083: File and Directory Discovery 31.7%
6. T1070: Indicator Removal on Host 31.7%
7. T1055: Process Injection 28.5%
8. T1021: Remote Services 27.4%
9. T1497: Virtualization/Sandbox Evasion 26.9%
10. T1105: Ingress Tool Transfer 26.5%


# Threat actors

## FIN12

- FIN12 is a financially motivated threat group behind prolific RYUK ransomware attacks dating to at least October 2018. Mandiant’s definition of FIN12 is limited to post-compromise activity because we have high confidence FIN12 relies on partners to obtain initial access to victim environments. Instead of conducting data theft and extortion, a tactic widely adopted by other ransomware threat actors, FIN12 appears to prioritize speed.
- FIN12 has largely targeted high-revenue organizations. 
- Unlike other ransomware threat actors, the group has frequently targeted organizations in the healthcare sector.
- Historically, FIN12 has maintained a close partnership with TRICKBOT-affiliated threat actors.
- FIN12 seemingly diversified its partnerships
- In at least four FIN12 intrusions between February and April 2021, evidence revealed malicious access to the targeted organization’s Citrix environment. While investigations did not confirm how FIN12 obtained legitimate credentials to the environment, it is plausible the threat actors relied on purchases from underground forums.
- In two separate FIN12 intrusions during May 2021, a threat actor obtained a foothold in environments through malicious email campaigns distributed internally from compromised user accounts. In both incidents, the threat actor used compromised credentials to access the targeted organization’s Microsoft 365 environment.

## FIN13

- FIN13 is a financially motivated threat group that targets organizations based in Mexico
- monetized its intrusions by collecting information required to conduct fraudulent financial transfers
- FIN13 has gained access to victim organizations by exploiting vulnerabilities in public-facing web servers and popular tools and malware that are at least partially based on publicly available code
- FIN13 is further characterized by its extensive use of web shells and other passive backdoors across various stages of the attack lifecycle.
- maintained presence in victim environments for durations up to several years
- FIN13 monetizes its operations with schemes directly enabled via data theft
- often steals financial data or files related to a company’s point-of-sale (POS) systems, ATMs and general financial transaction processing systems
- fluent in Spanish

## UNC2891

- targeted financial organizations in the Asia Pacific region
- possesses a fluency and expertise in targeting Unix and Linux based systems for objectives which appear to be financially motivated
- Mandiant identified evidence that UNC2891 used an expansive attacker toolkit called SUN4ME. SUN4ME is a self-contained ELF binary with over a hundred commands that aid the operator in all stages of the attack lifecycle.
- In every case where Mandiant recovered variants of SUN4ME, it had been loaded through an in-memory dropper Mandiant tracks as STEELCORGI

## UNC1151

- cluster of activity Mandiant believes is linked to the Belarusian government
- Ghostwriter information operations campaign
- targeted a wide variety of governmental and private sector entities, with a focus in Ukraine, Lithuania, Latvia, Poland and Germany
- Anti-NATO Sentiments

# Targeting virtualization infrastructure

- turning on the ESXi Shell and enabling direct access via SSH (TCP/22) to the ESXi servers to ensure that ESXi host access remains available
- created new (local) accounts for their use on the ESXi servers
- changed the password of the existing ESXi root account
- upload their encryptor (binary)
- shell scripts to discover where virtual machines were located on the ESXi datastores, forcefully stop any running virtual machines, optionally delete snapshots and then iterate through the datastores to encrypt all the virtual machine disk and configuration files

# Common misconfigurations

- Kerberoasting highly privileged user account-based Service Principal Names
- GPO edit permissions for non-privileged users
- Privileged user account usage over non-tier 0 assets
- Use of unconstrained delegation
- Certificate template permits Domain Admin escalation
- Identities without multi-factor authentication (MFA) enforcement resulted in unauthorized access
- Legacy authentication to bypass MFA in Azure AD
- Privileged Identities Synced from On-Premises Infrastructure
- Relaxed firewall rules on cloud-hosted virtual machines
- Overly-permissive roles assigned to non-privileged users
- Illicit consent grants attacks
- Risky Azure API permissions delegated to single or multi-tenant applications

