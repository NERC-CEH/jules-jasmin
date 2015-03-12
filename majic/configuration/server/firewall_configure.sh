#!/usr/bin/env bash
#
# iptables configuration script
#

IP_ADMIN=192.171.156.100
IP_RANGES_CEH="192.171.129.0/24 192.171.156.0/25 192.171.172.0/24 192.171.178.0/24 192.171.192.0/24 193.62.153.0/24"
#IP_RANGES_TESSELLA=""

IPS_FOR_SSH="$IP_RANGES_CEH $IP_ADMIN"

if [ -n "$1" ]
then
  echo "Usage: config_firewall - configures the firewall to allow access to ssh for CEH Wallingford and https access for everyone"
  exit
fi

# Flush all current rules from iptables
#
  iptables -F

#
# Allow SSH connections on tcp port 22
# This is essential when working on remote servers via SSH to prevent locking yourself out of the system
#
 iptables -A INPUT -p tcp -s $IP_ADMIN --dport 22 -j ACCEPT  # SSH for admin so the admin always has access
 for ip_for_ssh in $IPS_FOR_SSH
 do
	iptables -A INPUT -p tcp -s $ip_for_ssh --dport 22 -j ACCEPT
 done

#
# Set default policies for INPUT, FORWARD and OUTPUT chains
#
 iptables -P INPUT DROP
 iptables -P FORWARD DROP
 iptables -P OUTPUT ACCEPT
#
# Set access for localhost
#
 iptables -A INPUT -i lo -j ACCEPT
#
# Accept packets belonging to established and related connections
#
 iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
#
#  Allow https access
#
iptables -A INPUT -p tcp -s $IP_ADMIN --dport 443 -j ACCEPT

#
# Save settings
#
 /sbin/service iptables save
#
# List rules
#
 iptables -L -v
