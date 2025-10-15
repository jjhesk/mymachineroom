# MachineRoom Quick Start Guide

Get up and running with MachineRoom in minutes! This guide will walk you through the essential steps to start managing your servers.

## Table of Contents

1. [Installation](#installation)
2. [Basic Setup](#basic-setup)
3. [Create Your First Server List](#create-your-first-server-list)
4. [Essential Commands](#essential-commands)
5. [Common Use Cases](#common-use-cases)
6. [Next Steps](#next-steps)

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip3 install machineroom
```

### Option 2: Install from Source

```bash
git clone https://github.com/jjhesk/mymachineroom.git
cd mymachineroom
pip3 install -e .
```

## Basic Setup

### 1. Create Your Configuration Script

Create a file called `server_manager.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from machineroom.const import Config

# Configure your data directory (where server lists and cache are stored)
Config.DATAPATH_BASE = "/Users/yourusername/.machineroom"

# Configure your SSH public key path
Config.PUB_KEY = "/Users/yourusername/.ssh/id_rsa.pub"

# Configure your email/identifier (used in SSH key comments)
Config.MY_KEY_FEATURE = "your-email@domain.com"

# Optional: Set minimum requirements
Config.RAM_GB_REQUIREMENT = 4
Config.DOCKER_COMPOSE_VERSION = "2.24.6"

from machineroom.worker import internal_work

if __name__ == '__main__':
    internal_work()
```

### 2. Make It Executable

```bash
chmod +x server_manager.py
```

### 3. Create Data Directory

```bash
mkdir -p /Users/yourusername/.machineroom
```

## Create Your First Server List

### 1. Create Server Configuration File

Create a file called `my_servers.txt` in your data directory:

```bash
# Create the file
touch /Users/yourusername/.machineroom/my_servers.txt
```

### 2. Add Your Servers

Edit the file and add your servers in this format:

```
# Format: server_id--host--user--password--port--ssh_key_path
web-01--192.168.1.100--root--mypassword--22
db-01--192.168.1.101--admin--secretpass--2222
api-01--10.0.0.50--ubuntu--mypassword
```

**Field Description:**
- `server_id`: Unique identifier for the server
- `host`: IP address or hostname
- `user`: SSH username
- `password`: SSH password (can be empty for SSH key auth)
- `port`: SSH port (optional, defaults to 22)
- `ssh_key_path`: Path to SSH private key (optional)

### 3. Example with Different Authentication Methods

```
# Password authentication
web-01--192.168.1.100--root--mypassword--22

# SSH key authentication (empty password)
kansas-server--203.0.113.100--admin------22--/Users/yourusername/.ssh/custom_key

# Custom SSH port
backup-server--192.168.1.250--backup--backuppass--2222
```

## Essential Commands

### 1. Import Your Server List

```bash
python3 server_manager.py import my_servers.txt
```

This command:
- Reads your server configuration file
- Validates the format
- Stores server information in the local database
- Establishes initial connections to verify servers

### 2. List All Servers

```bash
python3 server_manager.py ls
```

This shows a table with:
- Server ID and hostname
- Installation status (CERT, DOCKER, etc.)
- Tunnel profile (if configured)
- Retirement status

Example output:
```
ID          HOST            TUNNEL PROFILE    EXPIRED    CERT    DOCKER    DAED    YACHT    PY
----------  --------------  ----------------  ---------  ------  --------  ------  -------  --
web-01      192.168.1.100                              False   False    False   False   False
db-01       192.168.1.101                              False   False    False   False   False
api-01      10.0.0.50                                  False   False    False   False   False
```

### 3. Connect to a Server

```bash
python3 server_manager.py web-01
```

This will:
- Establish SSH connection to the server
- Use the configured authentication method
- Open an interactive shell

### 4. Deploy SSH Certificates

```bash
python3 server_manager.py add-cert my_servers.txt
```

This will:
- Prompt for your public key path
- Prompt for a certificate name
- Deploy the SSH key to all servers
- Enable passwordless SSH access

### 5. Scan Server Ports

```bash
python3 server_manager.py watch-profile my_servers.txt
```

This will:
- Connect to each server
- Scan for open ports
- Store port information in the database

## Common Use Cases

### Use Case 1: Initial Server Setup

```bash
# 1. Import servers
python3 server_manager.py import my_servers.txt

# 2. Deploy SSH certificates
python3 server_manager.py add-cert my_servers.txt

# 3. Check server status
python3 server_manager.py ls

# 4. Connect to a server
python3 server_manager.py web-01
```

### Use Case 2: Server Health Monitoring

```bash
# 1. Scan ports on all servers
python3 server_manager.py watch-profile my_servers.txt

# 2. Check status
python3 server_manager.py ls

# 3. Connect to a specific server for investigation
python3 server_manager.py web-01
```

### Use Case 3: Certificate Management

```bash
# 1. Add certificates to all servers
python3 server_manager.py add-cert my_servers.txt

# 2. Remove certificates (if needed)
python3 server_manager.py off-cert my_servers.txt

# 3. Verify certificate status
python3 server_manager.py ls
```

### Use Case 4: Server Retirement

```bash
# 1. Mark servers as retired
python3 server_manager.py retire my_servers.txt

# 2. Check retirement status
python3 server_manager.py ls
```

## Advanced Configuration

### VPN Tunnel Support

If your servers are behind a VPN, add a tunnel configuration as the first line:

```
#tunnel-profile-name--L2TP/IPSEC--vpn.company.com--vpnuser--vpnpass
web-01--192.168.1.100--root--mypassword--22
db-01--192.168.1.101--admin--secretpass--2222
```

Supported tunnel types:
- `L2TP/IPSEC`
- `CISCO/IPSEC`
- `IKEV2`
- `SSH`
- `WIREGUARD`
- `PPTP`

### Custom SSH Keys

For servers requiring different SSH keys:

```
# Use custom SSH key
kansas-server--203.0.113.100--admin------22--/Users/yourusername/.ssh/custom_key
prod-web--192.168.1.100--ubuntu------/Users/yourusername/.ssh/prod_key
```

### Multiple Environments

Create separate files for different environments:

```bash
# Development servers
python3 server_manager.py import dev_servers.txt

# Production servers  
python3 server_manager.py import prod_servers.txt

# Staging servers
python3 server_manager.py import staging_servers.txt
```

## Troubleshooting

### Common Issues

1. **"Wrong path cannot open this file"**
   - Make sure your server file is in the `DATAPATH_BASE` directory
   - Check the filename spelling

2. **SSH connection failures**
   - Verify server credentials
   - Check network connectivity
   - Ensure SSH service is running on target servers

3. **Permission denied errors**
   - Check SSH key permissions: `chmod 600 ~/.ssh/id_rsa`
   - Verify SSH key is added to the server's authorized_keys

4. **Database errors**
   - Delete the cache database: `rm /Users/yourusername/.machineroom/cache.db`
   - Re-import your servers

### Debug Mode

Enable verbose output by modifying your script:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

Now that you have the basics working, explore these advanced features:

1. **Custom Deployment Scripts** - See [EXAMPLES.md](EXAMPLES.md) for deployment automation
2. **Docker Integration** - Deploy containers across multiple servers
3. **Health Monitoring** - Set up automated health checks
4. **Configuration Management** - Deploy configurations to multiple servers
5. **Batch Operations** - Execute commands across server groups

### Recommended Reading

- [Developer Guide](MACHINEROOM_DEVELOPER_GUIDE.md) - Comprehensive development guide
- [Examples](EXAMPLES.md) - Practical examples and use cases
- [Import Command Documentation](IMPORT_COMMAND.md) - Detailed import process guide
- [System Design](design/SYSTEM_DESIGN.md) - Architecture overview

### Getting Help

- Check the [troubleshooting section](#troubleshooting) for common issues
- Review the [examples](EXAMPLES.md) for implementation patterns
- Examine the [developer guide](MACHINEROOM_DEVELOPER_GUIDE.md) for advanced usage

## Summary

You've successfully:
- ✅ Installed MachineRoom
- ✅ Created your configuration script
- ✅ Set up your first server list
- ✅ Learned essential commands
- ✅ Understood common use cases

You're now ready to manage your servers efficiently with MachineRoom! 🚀
