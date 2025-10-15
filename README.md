# MachineRoom - Centralized Server Management Console

A powerful Python-based tool for managing multiple remote servers from a single console interface. MachineRoom provides centralized control over SSH connections, Docker deployments, VPN tunneling, and server health monitoring.

## 🚀 What is MachineRoom?

MachineRoom is a comprehensive server management solution that allows you to:

- **Manage multiple servers** from a single command-line interface
- **Automate SSH key deployment** and certificate management across servers
- **Deploy and manage Docker containers** with built-in orchestration
- **Monitor server health** with port scanning and container status checks
- **Support VPN tunneling** (L2TP/IPSec, Cisco/IPSec, IKEv2, SSH, WireGuard)
- **Batch operations** for executing commands across multiple servers simultaneously
- **Centralized authentication** with secure credential management

## ✨ Key Features

### 🔧 Server Management
- Import server lists from configuration files
- Centralized SSH connection management
- Automated certificate deployment and removal
- Server health monitoring and port scanning
- Batch operations across multiple servers

### 🐳 Docker Integration
- Automated Docker and Docker Compose installation
- Container orchestration and management
- Yacht web interface deployment
- Watchtower for automatic container updates
- Custom Docker Compose configurations

### 🔐 Security & Authentication
- SSH key management and deployment
- Custom certificate support with SSH key path specification
- Mixed authentication (password + SSH key) support
- VPN tunnel integration
- Secure credential storage in SQLite database

### 📊 Monitoring & Health Checks
- Port scanning and service detection
- Container status monitoring
- Database integrity checks
- System resource monitoring

## 🏗️ Architecture

MachineRoom uses a modular architecture with the following components:

- **CLI Interface** (`worker.py`) - Command-line interface for user interactions
- **Infrastructure Layer** (`infra.py`) - Core server management operations
- **Task Base** (`taskbase.py`) - Deployment and automation foundation
- **Database Layer** (`sql.py`) - SQLite-based server repository
- **Tunnel Management** (`tunnels/`) - VPN and SSH tunnel support
- **Configuration** (`const.py`) - Centralized configuration management

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- SSH client
- Network access to target servers

### Install from PyPI

```bash
pip3 install machineroom
```

Or for system-wide installation:

```bash
sudo pip3 install machineroom --upgrade
```

### Install from Source

```bash
git clone https://github.com/jjhesk/mymachineroom.git
cd mymachineroom
pip3 install -e .
```

## ⚙️ Configuration

### Basic Setup

Create a configuration file or set environment variables:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from machineroom.const import Config

# Configure your data directory (where server lists and cache are stored)
Config.DATAPATH_BASE = "/path/to/your/data/directory"

# Configure your SSH public key path
Config.PUB_KEY = "/Users/yourusername/.ssh/id_rsa.pub"

# Optional: Configure additional settings
Config.LOCAL_KEY_HOLDER = "/Users/yourusername/.ssh"
Config.MY_KEY_FEATURE = "your-email@domain.com"
Config.RAM_GB_REQUIREMENT = 4
Config.DOCKER_COMPOSE_VERSION = "2.24.6"

from machineroom.worker import internal_work

if __name__ == '__main__':
    internal_work()
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `DATAPATH_BASE` | Base directory for server lists and cache | `"...._file....locator"` |
| `PUB_KEY` | Path to your SSH public key | `"/Users/xxxx/.ssh/id_rsa.pub"` |
| `LOCAL_KEY_HOLDER` | Directory containing SSH keys | `"/Users/xxxx/.ssh"` |
| `MY_KEY_FEATURE` | Your email/identifier for SSH keys | `"xxx@xxxx"` |
| `RAM_GB_REQUIREMENT` | Minimum RAM requirement for servers | `4` |
| `DOCKER_COMPOSE_VERSION` | Docker Compose version to install | `"2.24.6"` |
| `REMOTE_WS` | Remote workspace path | `"...remote_locator"` |
| `HOME` | Default home directory on remote servers | `"/root"` |

### Create a Custom Executable

Create a custom script for easy execution:

```bash
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from machineroom.const import Config

# Configure your paths
Config.DATAPATH_BASE = "/Users/yourusername/.machineroom"
Config.PUB_KEY = "/Users/yourusername/.ssh/id_rsa.pub"

from machineroom.worker import internal_work

if __name__ == '__main__':
    internal_work()
```

Make it executable:

```bash
chmod +x your_script.py
```

## 🚀 Usage

### Basic Commands

MachineRoom provides a command-line interface for managing your servers. Here are the main commands:

#### List Servers
```bash
python3 your_script.py ls
```
Shows a table of all configured servers with their status, certificates, and installed services.

#### Connect to a Server
```bash
python3 your_script.py <server_id>
```
Establishes an SSH connection to the specified server.

#### Import Server List
```bash
python3 your_script.py import <server_list_file>
```
Imports servers from a configuration file into the local database.

> 📖 **Detailed Documentation**: See [Import Command Documentation](docs/IMPORT_COMMAND.md) for comprehensive guide on file format, examples, and troubleshooting.

#### Scan Server Ports
```bash
python3 your_script.py watch-profile <server_list_file>
```
Scans and records open ports on all servers in the specified list.

#### Manage Certificates
```bash
# Add custom certificate
python3 your_script.py add-cert <server_list_file>

# Remove certificate
python3 your_script.py off-cert <server_list_file>
```

#### Retire Servers
```bash
python3 your_script.py retire <server_list_file>
```
Marks servers as retired in the database.

#### Check Version
```bash
python3 your_script.py v
```
Shows the current MachineRoom version.

### Server List Format

Create a text file with one server per line in the following format:

```
server_id--hostname--username--password--port--ssh_key_path
```

**Field Description:**
- `server_id`: Unique identifier for the server (required)
- `hostname`: IP address or hostname of the server (required)
- `user`: SSH username for authentication (required)
- `password`: SSH password for authentication (optional, can be empty for SSH key auth)
- `port`: SSH port number (optional, defaults to 22)
- `ssh_key_path`: Path to SSH private key file (optional, for key-based authentication)

**Examples:**
```
# Traditional password authentication
web1--192.168.1.10--root--mypassword--22
db1--192.168.1.11--admin--secretpass--2222

# SSH key authentication with custom port
kansas-server--204.12.246.204--kliner------22--/Users/hesdx/.ssh/kansas_rsa

# SSH key authentication with default port
prod-web--192.168.1.100--ubuntu------/Users/hesdx/.ssh/prod_key
```

### Examples

#### 1. Initial Setup
```bash
# Create your server list
echo "web1--192.168.1.10--root--mypassword--22" > servers.txt

# Import servers
python3 your_script.py import servers.txt

# List all servers
python3 your_script.py ls
```

#### 2. Connect to a Server
```bash
# Connect to web1 server
python3 your_script.py web1
```

#### 3. Deploy Certificates
```bash
# Add SSH certificates to all servers
python3 your_script.py add-cert servers.txt
# Follow prompts to enter certificate details
```

#### 4. Monitor Server Health
```bash
# Scan ports on all servers
python3 your_script.py watch-profile servers.txt

# Check server status
python3 your_script.py ls
```

### Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `ls` | List all servers with status | `python3 script.py ls` |
| `<server_id>` | Connect to specific server | `python3 script.py web1` |
| `import <file>` | Import server list | `python3 script.py import servers.txt` |
| `watch-profile <file>` | Scan ports on servers | `python3 script.py watch-profile servers.txt` |
| `add-cert <file>` | Add SSH certificates | `python3 script.py add-cert servers.txt` |
| `off-cert <file>` | Remove certificates | `python3 script.py off-cert servers.txt` |
| `retire <file>` | Mark servers as retired | `python3 script.py retire servers.txt` |
| `set-home <id> <path>` | Set home directory for server | `python3 script.py set-home web1 /home/user` |
| `v` | Show version | `python3 script.py v` |

## 🔧 Advanced Features

### Docker Management

MachineRoom includes comprehensive Docker support:

- **Automated Installation**: Installs Docker and Docker Compose on target servers
- **Container Orchestration**: Deploy and manage containers across multiple servers
- **Yacht Integration**: Deploy Yacht web interface for container management
- **Watchtower**: Automatic container updates
- **Custom Configurations**: Support for custom Docker Compose files

### VPN Tunnel Support

Supports multiple VPN tunnel types:

- L2TP/IPSec
- Cisco/IPSec  
- IKEv2
- SSTP
- SSH Tunneling
- WireGuard
- PPTP

### Health Monitoring

Built-in monitoring capabilities:

- Port scanning and service detection
- Container status monitoring
- Database integrity checks
- System resource monitoring
- Automated health reports

## 🛠️ Troubleshooting

### Common Issues

#### Connection Refused
```
Error: Connection refused to server
```
**Solution**: 
- Verify server is running and accessible
- Check firewall settings
- Ensure SSH service is running on the target port

#### Authentication Failed
```
Error: Authentication failed
```
**Solution**:
- Verify username and password in server list
- Check if SSH key authentication is properly configured
- Ensure the user has proper permissions

#### Certificate Issues
```
Error: Certificate not found
```
**Solution**:
- Verify `PUB_KEY` path in configuration
- Ensure the public key file exists and is readable
- Check that the corresponding private key is available

#### Import File Not Found
```
Error: Wrong path cannot open this file
```
**Solution**:
- Verify the file path exists in `DATAPATH_BASE` directory
- Check file permissions
- Ensure the server list file format is correct

### Debug Mode

Enable verbose logging by modifying your script:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Your existing configuration...
```

### Database Issues

If you encounter database corruption:

```bash
# Check database integrity
sqlite3 cache.db "PRAGMA integrity_check;"

# Backup and recreate if needed
cp cache.db cache.db.backup
rm cache.db
# Re-import your server lists
```

### Network Issues

For VPN tunnel problems:

1. Verify tunnel configuration
2. Check network connectivity
3. Ensure proper credentials are configured
4. Test tunnel connection manually

## 📚 Additional Resources

### File Structure

```
machineroom/
├── __init__.py          # Package initialization
├── const.py             # Configuration and constants
├── worker.py            # Main CLI interface
├── infra.py             # Infrastructure management
├── taskbase.py          # Deployment automation
├── sql.py               # Database operations
├── util.py              # Utility functions
├── errs.py              # Error handling
└── tunnels/             # VPN tunnel support
    ├── conn.py          # Connection management
    └── fork.py          # Process management
```

### Dependencies

- `SQLiteAsJSON` - Database operations
- `fabric` - SSH connection management
- `pexpect` - Process automation
- `tabulate` - Table formatting
- `paramiko` - SSH protocol implementation

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Documentation

- **[Import Command Documentation](docs/IMPORT_COMMAND.md)** - Comprehensive guide for importing server configurations
- **[Import Quick Reference](docs/IMPORT_QUICK_REFERENCE.md)** - Quick reference card for import command
- **[System Design](docs/design/SYSTEM_DESIGN.md)** - Detailed system architecture and design patterns

### Support

For issues and questions:
- Check the troubleshooting section above
- Review the documentation in the `docs/` directory
- Open an issue on GitHub

## 📄 License

MIT License (2022), Jun-You Liu, Heskemo BTC

---

**MachineRoom** - Simplifying server management, one command at a time.

