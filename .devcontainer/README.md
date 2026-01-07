# DevContainer Host Configuration

This directory contains the DevContainer configuration for the TN5250 Robot Framework project. The host configuration system allows you to manage IBM i host entries dynamically without rebuilding the container.

## Files

<<<<<<< HEAD
- **`devcontainer.json.template`**: Template configuration file with example hosts. Use this as a reference to create your local `devcontainer.json`.
=======
- **`devcontainer.template.json`**: Template configuration file with example hosts. Use this as a reference to create your local `devcontainer.json`.
>>>>>>> 38b2252 (Copy selected files from copilot/implement-dynamic-host-configuration)
- **`devcontainer.json`**: Your local configuration (gitignored - not committed to version control).
- **`hosts.conf`**: Configuration file containing host-to-IP mappings. Modify this to add/remove hosts.
- **`setup-hosts.sh`**: Startup script that reads `hosts.conf` and adds entries to `/etc/hosts`.

## Setup Instructions

1. **First-time setup**:
   ```bash
   # Copy the template to create your local configuration
   cp .devcontainer/devcontainer.json.template .devcontainer/devcontainer.json
   
   # Edit devcontainer.json to set your git user name and email
   # (Replace 'Your Name' and 'your.email@example.com')
   ```

2. **Configure hosts**:
   Edit `.devcontainer/hosts.conf` and add your host entries:
   ```
   # Format: hostname ip_address
   dev400 192.168.1.100
   prod400 192.168.1.200
   ```

3. **Build/Rebuild the container**:
   - In VS Code: Press `F1` → "Dev Containers: Rebuild Container"
   - The `setup-hosts.sh` script will run automatically via `postCreateCommand`

## Benefits

- ✅ No customer-specific data in version control
- ✅ Easy host management without container rebuilds (just modify `hosts.conf`)
- ✅ Team members can maintain their own configurations
- ✅ Different environments (dev, test, prod) are easily managed

## How It Works

1. When the container is created, the `postCreateCommand` runs `setup-hosts.sh`
2. The script reads `hosts.conf` and adds each host entry to `/etc/hosts`
3. Your TN5250 applications can connect to the configured hosts
4. To update hosts, modify `hosts.conf` and rebuild the container

## Notes

- The `devcontainer.json` file is gitignored to prevent accidental commits of customer data
<<<<<<< HEAD
- Always use `devcontainer.json.template` as the reference for configuration structure
=======
- Always use `devcontainer.template.json` as the reference for configuration structure
>>>>>>> 38b2252 (Copy selected files from copilot/implement-dynamic-host-configuration)
- The `hosts.conf` file is committed to version control but should only contain example/placeholder entries
