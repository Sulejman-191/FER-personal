#! /bin/sh

IPT=/sbin/iptables

$IPT -P INPUT DROP
$IPT -P OUTPUT DROP
$IPT -P FORWARD DROP

$IPT -F INPUT
$IPT -F OUTPUT
$IPT -F FORWARD

$IPT -A INPUT   -m state --state ESTABLISHED,RELATED -j ACCEPT 
$IPT -A OUTPUT  -m state --state ESTABLISHED,RELATED -j ACCEPT 
$IPT -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT

# 
# loopback"
# 
$IPT -A INPUT  -i lo   -m state --state NEW  -j ACCEPT
$IPT -A OUTPUT -o lo   -m state --state NEW  -j ACCEPT

#
# RIP na FW eth0
#
$IPT -A INPUT -i eth0  -p udp -m udp -s 192.0.2.100  -d 224.0.0.9  --sport 520 --dport 520   -m state --state NEW  -j ACCEPT
$IPT -A OUTPUT         -p udp -m udp -s 192.0.2.1    -d 224.0.0.9  --sport 520 --dport 520   -m state --state NEW  -j ACCEPT


# ================ Dodajte ili modificirajte pravila na oznacenim mjestima # 
# "anti spoofing" (eth0)
#
$IPT -A INPUT   -i eth0 -s 127.0.0.0/8  -j DROP
$IPT -A FORWARD -i eth0 -s 127.0.0.0/8  -j DROP
#
# <--- Dodajte ili modificirajte pravila 
$IPT -A INPUT   -i eth0 -s 198.51.100.0/24  -j DROP
$IPT -A FORWARD -i eth0 -s 198.51.100.0/24  -j DROP

# 
# SSH pristup iz Interneta je dozvoljen samo na racunalo "ssh"
#
# <--- Dodajte pravila
$IPT -A FORWARD -i eth0 -p tcp -d 198.51.100.10 --dport 22 -m state --state NEW -j ACCEPT

#
# na racunalu "web" se nalazi javni http i https posluzitelj
#
# <--- Dodajte pravila
$IPT -A FORWARD -i eth0 -p tcp -d 198.51.100.11 --dport 80 -m state --state NEW -j ACCEPT
$IPT -A FORWARD -i eth0 -p tcp -d 198.51.100.11 --dport 443 -m state --state NEW -j ACCEPT

#
# s posluzitelja web je dozvoljen pristup DNS poslužiteljima u Internetu 
#
# <--- Dodajte pravila
$IPT -A FORWARD -i eth0 -p tcp -s 198.51.100.11 --dport 53 -m state --state NEW -j ACCEPT
$IPT -A FORWARD -i eth0 -p udp -s 198.51.100.11 --dport 53 -m state --state NEW -j ACCEPT

#
# SSH pristup vatrozidu FW je dozvoljen samo s racunala int1 (LAN)
#
# <--- Dodajte pravila

$IPT -A INPUT -i eth2 -p tcp -s 10.0.0.21 --dport 22 -m state --state NEW -j ACCEPT

#
# svim racunalima iz LAN mreze je dozvoljen pristup DMZ i Internetu 
#
# <--- Dodajte pravila 
$IPT -A FORWARD -i eth2 -s 198.51.100.2 -m state --state NEW -j ACCEPT
# nije potrebno pravilo za DMZ jer komunikacija uopće ne bi trebala ići preko FW

# 
# za potrebe testiranja dozvoljen je ICMP (ping i sve ostalo)
#
$IPT -A INPUT   -p icmp -j ACCEPT
$IPT -A FORWARD -p icmp -j ACCEPT
$IPT -A OUTPUT  -p icmp -j ACCEPT

# NAPOMENA: nije potrebno dodavati ESTABLISHED,RELATED stanja jer su već na početku file-a dodana
# pravila koja prihvačaju sve pakete koji su ESTABLISHED,RELATED