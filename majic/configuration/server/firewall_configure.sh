#!/usr/bin/env bash
#
# iptables configuration script
#

IP_ADMIN=192.171.156.100
IP_RANGES_CEH="192.171.129.0/24 192.171.156.0/25 192.171.172.0/24 192.171.178.0/24 192.171.192.0/24 193.62.153.0/24"
IP_RANGES_TESSELLA="212.140.132.200 80.252.78.170"
IP_LOCAL_NETWORK="192.168.3.0/24"
IP_TEAMCITY_SERVER="192.168.3.3"
IP_BUILD_AGENT="192.168.3.2"


IPS_FOR_SSH="$IP_RANGES_CEH $IP_RANGES_TESSELLA $IP_LOCAL_NETWORK"

if [ "$1" == "majic" ]
then
 https=1
 build_agent=1
 teamcity_server=0
elif [ "$1" == "teamcity" ]
then
 https=0
 build_agent=0
 teamcity_server=1
else
    echo "Usage: config_firewall <majic | teamcity>- configures the firewall to allow access to the machine"
  echo "                       majic for the majic web server, teamcity for the teamcity server"
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

# Teamcity access
if [ $build_agent == 1 ]
then
  iptables -A INPUT -p tcp -s $IP_TEAMCITY_SERVER --dport 9090 -j ACCEPT
fi
if [ $teamcity_server == 1 ]
then
  iptables -A INPUT -p tcp -s $IP_BUILD_AGENT --dport 9090 -j ACCEPT
fi

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
if [ $https == 1 ]
then
  iptables -A INPUT -p tcp --dport 443 -j ACCEPT
  iptables -A INPUT -p tcp --dport 80 -j ACCEPT
  # if the ip address is for this server send to internal ip since firewall
  #  doesn't seem to do this
  iptables -t nat -I OUTPUT --dest 192.171.139.30 -p tcp --dport 443 -j DNAT --to-dest 192.168.3.2
fi

#
# Save settings
#
 /sbin/service iptables save
#
# List rules
#
 iptables -L -v
