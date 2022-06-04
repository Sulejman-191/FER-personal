#!/bin/sh 
IPT=/sbin/iptables

$IPT -P INPUT   DROP
$IPT -P OUTPUT  DROP
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

# ================ NAT (ne treba mijenjati)
# za pristup DMZ iz LAN-a se ne radi promjena adresa
#
$IPT -t nat -A POSTROUTING -s 198.51.100.0/24 -d 10.0.0.0/24     -j ACCEPT
$IPT -t nat -A PREROUTING  -s 198.51.100.0/24 -d 10.0.0.0/24     -j ACCEPT
$IPT -t nat -A POSTROUTING -s 10.0.0.0/24     -d 198.51.100.0/24 -j ACCEPT
$IPT -t nat -A PREROUTING  -s 10.0.0.0/24     -d 198.51.100.0/24 -j ACCEPT
# 
# NAT za sve ostale odlazne datagrame
#
$IPT -t nat -A POSTROUTING -o eth0 -s 10.0.0.0/24 -j SNAT --to-source 198.51.100.2


# ================ Dodajte ili modificirajte pravila na oznacenim mjestima
# 
# "anti spoofing" (eth0)
#
$IPT -A INPUT   -i eth0 -s 127.0.0.0/8  -j DROP
$IPT -A FORWARD -i eth0 -s 127.0.0.0/8  -j DROP
#
# <--- Dodajte ili modificirajte pravila 
# $IPT -A INPUT   -i eth0 -s 192.0.0.0/8  -j DROP
# $IPT -A FORWARD -i eth0 -s 192.0.0.0/8  -j DROP

# 
# SSH pristup vatrozidu FW_int je dozvoljen samo s racunala int1 (LAN)
#
# <--- Dodajte pravila 
$IPT -A INPUT -i eth1 -p tcp -s 10.0.0.21 --dport 22 -m state --state NEW -j ACCEPT

#
# SSH pristup posluzitelju web je dozvoljen samo s racunala int1 (LAN)
#
# <--- Dodajte pravila
$IPT -A FORWARD -i eth1 -p tcp -s 10.0.0.21 -d 198.51.100.11 --dport 22 -m state --state NEW -j ACCEPT
$IPT -A FORWARD -i eth1 -p tcp -d 198.51.100.11 --dport 22 -m state --state NEW -j DROP

# 
# SSH pristup posluzitelju ssh_int iz vanjske mreze je dozvoljen samo s posuzitelja ssh (DMZ)
#
# <--- Dodajte pravila 
$IPT -A FORWARD -i eth0 -p tcp -d 10.0.0.10 -s 198.51.100.10 --dport 22 -m state --state NEW -j ACCEPT
$IPT -A FORWARD -i eth0 -p tcp -d 10.0.0.10 -s 198.51.100.10 --dport 2222 -m state --state NEW -j ACCEPT

# 
# iz LAN-a je dozvoljen pristup DMZ i Internetu 
#
# <--- Dodajte pravila 
$IPT -A FORWARD -i eth1 -m state --state NEW -j ACCEPT

# 
# za potrebe testiranja dozvoljen je ICMP (ping i sve ostalo)
#
$IPT -A FORWARD -p icmp  -j ACCEPT
$IPT -A OUTPUT  -p icmp -j ACCEPT
$IPT -A INPUT   -p icmp -j ACCEPT

# NAPOMENA: nije potrebno dodavati ESTABLISHED,RELATED stanja jer su već na početku file-a dodana
# pravila koja prihvačaju sve pakete koji su ESTABLISHED,RELATED