#!/bin/bash
# Setup script to dynamically add host entries to /etc/hosts
# Reads configuration from .devcontainer/hosts.conf

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOSTS_CONF="${SCRIPT_DIR}/hosts.conf"

echo "Setting up host entries from ${HOSTS_CONF}..."

if [ ! -f "${HOSTS_CONF}" ]; then
    echo "Warning: ${HOSTS_CONF} not found. Skipping host configuration."
    exit 0
fi

# Read the hosts.conf file and add entries to /etc/hosts
while IFS= read -r line || [ -n "$line" ]; do
    # Skip empty lines and comments
    if [[ -z "$line" ]] || [[ "$line" =~ ^[[:space:]]*# ]]; then
        continue
    fi
    
    # Parse hostname and IP address (ignore any trailing fields/comments)
    if [[ "$line" =~ ^[[:space:]]*([^[:space:]]+)[[:space:]]+([^[:space:]]+) ]]; then
        hostname="${BASH_REMATCH[1]}"
        ip_address="${BASH_REMATCH[2]}"
        
        # Check if entry already exists in /etc/hosts (exact hostname match)
        if grep -qE "^${ip_address}[[:space:]]+${hostname}([[:space:]]|$)" /etc/hosts; then
            echo "Host entry already exists: ${hostname} -> ${ip_address}"
        else
            echo "Adding host entry: ${hostname} -> ${ip_address}"
            echo "${ip_address} ${hostname}" >> /etc/hosts
        fi
    fi
done < "${HOSTS_CONF}"

echo "Host setup complete!"
