#!/usr/bin/env bash
#
# iptables configuration script for a Workbench Tool
#

IP_LOCAL_NETWORK="192.168.3.0/24"

IPS_FOR_SSH="${IP_LOCAL_NETWORK}"

# Flush all current rules from iptables
#
  iptables -F

#
# Allow SSH connections on tcp port 22
# This is essential when working on remote servers via SSH to prevent locking yourself out of the system
#

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
# Save settings
#
 /sbin/service iptables save
#
# List rules
#
 iptables -L -v
