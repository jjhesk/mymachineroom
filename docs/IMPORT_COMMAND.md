# Import Command Documentation

## Overview

The `import` command in MachineRoom is used to import server configurations from text files into the local SQLite database. It reads server definitions, validates them, and stores them for later management operations.

## Table of Contents

1. [Command Syntax](#command-syntax)
2. [File Format](#file-format)
3. [How the Import Process Works](#how-the-import-process-works)
4. [Usage Examples](#usage-examples)
5. [Error Handling](#error-handling)
6. [Configuration Requirements](#configuration-requirements)
7. [Integration with Other Commands](#integration-with-other-commands)
8. [Security Considerations](#security-considerations)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

> 📋 **Quick Reference**: For a condensed version, see [IMPORT_QUICK_REFERENCE.md](IMPORT_QUICK_REFERENCE.md)

## Command Syntax

```bash
connect import <filename>
```

**Alternative aliases:**
- `update_file`
- `update_conf` 
- `updateconfig`
- `updateconfiguration`
- `updateconfigurations`

### Parameters

- `<filename>`: Name of the server configuration file (without path)
  - File must be located in `Config.DATAPATH_BASE` directory
  - File extension is optional (e.g., `servers.txt` or `servers`)

## File Format

### Server Configuration Format

Server configurations are stored in plain text files with the following format:

```
server_id--host--user--password--port--ssh_key_path
```

**Field Description:**
- `server_id`: Unique identifier for the server (required)
- `host`: IP address or hostname of the server (required)
- `user`: SSH username for authentication (required)
- `password`: SSH password for authentication (optional, can be empty for SSH key auth)
- `port`: SSH port number (optional, defaults to 22)
- `ssh_key_path`: Path to SSH private key file (optional, for key-based authentication)

### Supported Delimiters

The parser supports multiple delimiter formats for flexibility:
- `--` (double dash) - **Recommended**
- `---` (triple dash)
- `----` (quad dash)
- `——` (em dash)
- `————` (double em dash)

### Example Server File

```
web-server-01--192.168.1.100--root--password123--22
db-server-01--192.168.1.101--admin--securepass--2222
api-server-01--10.0.0.50--ubuntu--mypassword
cache-server--10.0.0.60--redis--cachepass--6379
kansas-server--204.12.246.204--kliner------22--/Users/hesdx/.ssh/kansas_rsa
prod-web--192.168.1.100--ubuntu------/Users/hesdx/.ssh/prod_key
```

### Tunnel Configuration

If the first line starts with `#`, it's treated as a tunnel configuration:

```
#tunnel-profile-name--TUNNEL_TYPE--tunnel-server--username--password
```

**Supported tunnel types:**
- `L2TP/IPSEC`
- `CISCO/IPSEC`
- `IKEV2`
- `SSH`
- `WIREGUARD`
- `PPTP`

**Example tunnel configuration:**
```
#production-vpn--L2TP/IPSEC--vpn.company.com--vpnuser--vpnpass
web-01--192.168.1.100--root--password123--22
web-02--192.168.1.101--root--password123--22
```

## How the Import Process Works

### 1. Command Processing

The import command follows this flow:

```python
# Location: machineroom/worker.py, lines 124-131
elif a == "import":
    if b == "":
        err_exit("need to have one more arg")
    file = os.path.join(Config.DATAPATH_BASE, b)
    if os.path.exists(file) is False:
        err_exit("Wrong path cannot open this file" + file)
    job = ServerDoorJob(b)
    job.action_import()
```

### 2. File Validation

- Checks if filename argument is provided
- Validates file exists in `Config.DATAPATH_BASE` directory
- Creates `ServerDoorJob` instance with filename

### 3. Import Execution

```python
# Location: machineroom/worker.py, lines 21-22
def action_import(self):
    self.run_conn()
```

The `action_import()` method calls `run_conn()` which:

1. **Reads the server file** line by line
2. **Parses each line** using `reader_split_recognition()` and `reader_profile_0()`
3. **Validates server IDs** against bad ID list
4. **Detects tunnel configuration** if first line starts with `#`
5. **Stores server data** in SQLite database via `ServerRoom` class

### 4. File Parsing Logic

```python
# Location: machineroom/util.py, lines 531-605
def reader_split_recognition(line: str) -> list:
    # Handle consecutive delimiters by normalizing them first
    import re
    
    # Normalize consecutive delimiters to avoid confusion
    # ---- becomes --- + empty field + --- (no space)
    line = re.sub(r'----', '--- ---', line)
    line = re.sub(r'————', '———— ————', line)
    line = re.sub(r'——', '—— ——', line)
    
    # Now split on the appropriate delimiter
    if "————" in line:
        line = line.split("————")
    elif "——" in line:
        line = line.split("——")
    elif "---" in line:
        line = line.split("---")
    elif "--" in line:
        line = line.split("--")
    
    # Clean up any empty strings or spaces, and fix any remaining double dashes
    line = [field.strip() for field in line]
    line = [field.lstrip('-') if field.startswith('--') else field for field in line]
    
    return line

def reader_profile_0(line: list) -> dict:
    profile = {
        "id": line[0],
        "host": line[1], 
        "user": line[2],
        "pass": line[3],
        "port": 22  # default port
    }

    # Handle port field (4th field, index 4)
    try:
        port = line[4]
        # Check if this looks like a port number (numeric) or SSH key path (starts with /)
        if port and port.strip() and not port.strip().startswith('/'):
            profile.update({"port": port})
    except IndexError:
        pass  # Use default port 22

    # Handle SSH key path field
    # It could be in position 5 (if port is specified) or position 4 (if port is not specified)
    ssh_key_path = None
    try:
        # First try position 5 (when port is specified)
        ssh_key_path = line[5]
    except IndexError:
        try:
            # If position 5 doesn't exist, try position 4 (when port is not specified)
            potential_key = line[4]
            if potential_key and potential_key.strip().startswith('/'):
                ssh_key_path = potential_key
        except IndexError:
            pass
    
    if ssh_key_path and ssh_key_path.strip():  # Only set if not empty
        profile.update({"ssh_key_path": ssh_key_path.strip()})

    return profile
```

### 5. Database Storage

Servers are stored in the `server_room` table with the following schema:

```sql
CREATE TABLE server_room (
    id CHAR(100) PRIMARY KEY,           -- Server identifier
    host CHAR(100) NOT NULL,            -- Server IP/hostname
    user CHAR(100) NOT NULL,            -- SSH username
    pass CHAR(100) NOT NULL,            -- SSH password
    port NUMBER(5) NOT NULL,            -- SSH port
    description CHAR(1000),             -- Server description
    res BLOB(100000) NOT NULL,          -- JSON metadata
    next_action BLOB(100000) NOT NULL   -- JSON for scheduled actions
);
```

**Metadata Structure** (`res` field):
```json
{
    "identity_cert_installed": true,
    "local_cert_path": "/Users/username/.ssh/custom_key",
    "docker_compose_installed": true,
    "python3_installed": true,
    "daed_installed": true,
    "yacht_installed": true,
    "tunnel_profile": "vpn-profile-name",
    "home_path": "/root",
    "ports": [22, 80, 443, 8080],
    "retired": false
}
```

## Usage Examples

### Basic Import

```bash
# Import servers from a file called "my_servers.txt"
connect import my_servers.txt
```

### Complete Example

**1. Create server configuration file:**

Create `production_servers.txt` in your `DATAPATH_BASE` directory:

> 💡 **Quick Start**: You can use the example file at `docs/example_servers.txt` as a template.

```
#prod-vpn--L2TP/IPSEC--vpn.company.com--vpnuser--vpnpass
web-01--192.168.1.100--root--password123--22
web-02--192.168.1.101--root--password123--22
db-primary--192.168.1.200--postgres--dbpass--5432
db-replica--192.168.1.201--postgres--dbpass--5432
cache-redis--192.168.1.210--redis--cachepass--6379
```

**2. Import the servers:**

```bash
connect import production_servers.txt
```

**3. Verify import:**

```bash
connect ls
```

Expected output:
```
ID          HOST            TUNNEL PROFILE    EXPIRED    CERT    DOCKER    DAED    YACHT    PY
----------  --------------  ----------------  ---------  ------  --------  ------  -------  --
web-01      192.168.1.100   prod-vpn                              False    False   False   False
web-02      192.168.1.101   prod-vpn                              False    False   False   False
db-primary  192.168.1.200   prod-vpn                              False    False   False   False
db-replica  192.168.1.201   prod-vpn                              False    False   False   False
cache-redis 192.168.1.210   prod-vpn                              False    False   False   False
```

### Advanced Examples

**Multiple environments:**
```
#dev-vpn--L2TP/IPSEC--dev-vpn.company.com--devuser--devpass
dev-web-01--10.0.1.100--ubuntu--devpass--22
dev-db-01--10.0.1.200--postgres--devpass--5432

#staging-vpn--L2TP/IPSEC--staging-vpn.company.com--staginguser--stagingpass
staging-web-01--10.0.2.100--ubuntu--stagingpass--22
staging-db-01--10.0.2.200--postgres--stagingpass--5432
```

**Mixed authentication methods:**
```
# Use SSH keys (password can be empty or placeholder)
web-01--192.168.1.100--root----22
# Use password authentication
web-02--192.168.1.101--root--password123--22
# Custom SSH port
web-03--192.168.1.102--admin--adminpass--2222
# SSH key authentication with custom key
kansas-server--204.12.246.204--kliner------22--/Users/hesdx/.ssh/kansas_rsa
# SSH key authentication with default port
prod-web--192.168.1.100--ubuntu------/Users/hesdx/.ssh/prod_key
```

## Error Handling

### Common Errors

1. **Missing filename argument:**
   ```
   need to have one more arg
   ```
   **Solution:** Provide a filename: `connect import servers.txt`

2. **File not found:**
   ```
   Wrong path cannot open this file /path/to/file
   ```
   **Solution:** 
   - Check file exists in `DATAPATH_BASE` directory
   - Verify filename spelling
   - Check file permissions

3. **Invalid server ID:**
   ```
   BadIDs exception raised
   ```
   **Solution:** Use a valid server ID (avoid reserved keywords)

4. **Malformed server line:**
   ```
   ServerAuthInfoErr exception raised
   ```
   **Solution:** Ensure proper delimiter format (`--`)

5. **Database connection error:**
   ```
   sqlite3.OperationalError
   ```
   **Solution:** Check database permissions and disk space

6. **SSH key file not found:**
   ```
   Permission denied (publickey)
   ```
   **Solution:** 
   - Verify the SSH key file exists at the specified path
   - Check file permissions (should be 600 for private keys)
   - Ensure the path is correct and accessible

7. **SSH key authentication failed:**
   ```
   Authentication failed
   ```
   **Solution:**
   - Verify the private key corresponds to a public key on the server
   - Check that the public key is in the server's `~/.ssh/authorized_keys`
   - Ensure the SSH key is not password-protected or provide the passphrase

### Validation Rules

- **Server ID**: Must be unique, not empty, and not in reserved list
- **Host**: Must be valid IP address or hostname
- **User**: Must not be empty
- **Password**: Can be empty (for SSH key authentication)
- **Port**: Must be numeric, defaults to 22 if not specified
- **SSH Key Path**: Must be a valid file path if specified (validation occurs during connection)

### SSH Key Path Validation

The system performs the following validation for SSH key paths:

1. **Path Format**: SSH key paths should start with `/` (absolute path) or `~` (home directory)
2. **File Existence**: The SSH key file must exist and be readable
3. **File Type**: Should be a private key file (typically without `.pub` extension)
4. **Permissions**: The private key file should have appropriate permissions (typically 600)

**Common SSH Key Path Examples**:
```
/Users/username/.ssh/id_rsa
/Users/username/.ssh/custom_key
~/.ssh/production_key
/opt/keys/server_key
```

## Configuration Requirements

### File Location

Server files must be placed in the directory specified by `Config.DATAPATH_BASE`:

```python
# Location: machineroom/const.py
DATAPATH_BASE: str = "...._file....locator"  # Configure this path
```

### Environment Setup

1. **Python Environment**: Python 3.11+ with virtual environment
2. **Dependencies**: Fabric, Paramiko, SQLiteAsJSON, tabulate
3. **System Requirements**: macOS with VPN utilities, SSH client

### Database Requirements

- SQLite database will be created automatically at `{DATAPATH_BASE}/cache.db`
- Database schema is defined in `machineroom/schema.json`
- Ensure write permissions to the data directory

## Integration with Other Commands

After importing servers, you can use other MachineRoom commands:

### List Servers
```bash
connect ls
```

### Connect to Server
```bash
connect <server_id>
# Example: connect web-01
```

### Add SSH Certificates
```bash
connect add-cert <cert_name> <pubkey_path>
```

### Scan Server Ports
```bash
connect scanports
```

### Mark Servers as Retired
```bash
connect retire
```

### Docker Operations
```bash
connect docker-scan
```

## Security Considerations

### Data Storage
- Server passwords are stored in **plain text** in the database
- Tunnel credentials are also stored in **plain text**
- Database file should have restricted permissions (600 or 700)

### File Permissions
- Server configuration files should have appropriate permissions (600 or 700)
- Avoid storing sensitive files in shared directories
- Consider using SSH key authentication instead of passwords

### Network Security
- Use VPN tunnels for secure access to remote networks
- Implement proper firewall rules on target servers
- Regularly rotate passwords and SSH keys

### Best Security Practices
1. **Use SSH keys** instead of passwords when possible
2. **Encrypt sensitive configuration files** at rest
3. **Limit file permissions** to owner only
4. **Regularly audit** imported server configurations
5. **Use strong passwords** for server authentication
6. **Implement VPN tunnels** for remote access

## Best Practices

### File Organization
1. **Use descriptive server IDs** that are easy to identify
2. **Group related servers** in the same file (e.g., by environment)
3. **Use consistent naming conventions** (e.g., `env-service-number`)
4. **Include comments** in configuration files for clarity

### Server Configuration
1. **Use SSH keys** instead of passwords when possible
2. **Specify custom ports** explicitly for non-standard SSH ports
3. **Use tunnel configurations** for secure access to remote networks
4. **Test connections** after import using the `ls` command

### Maintenance
1. **Regularly backup** your server configuration files
2. **Keep configurations up to date** as infrastructure changes
3. **Remove retired servers** from configuration files
4. **Document server purposes** in configuration files

### Example Naming Conventions
```
# Environment-Service-Number format
prod-web-01--192.168.1.100--root--password123--22
prod-web-02--192.168.1.101--root--password123--22
prod-db-01--192.168.1.200--postgres--dbpass--5432
staging-web-01--10.0.2.100--ubuntu--stagingpass--22
dev-web-01--10.0.1.100--ubuntu--devpass--22
```

## Troubleshooting

### Import Not Working

1. **Check file location:**
   ```bash
   ls -la $DATAPATH_BASE/
   ```

2. **Verify file format:**
   ```bash
   cat $DATAPATH_BASE/your_file.txt
   ```
   
   Compare with the example format in `docs/example_servers.txt`

3. **Check file permissions:**
   ```bash
   ls -la $DATAPATH_BASE/your_file.txt
   ```

### Database Issues

1. **Check database file:**
   ```bash
   ls -la $DATAPATH_BASE/cache.db
   ```

2. **Verify database integrity:**
   ```bash
   sqlite3 $DATAPATH_BASE/cache.db "PRAGMA integrity_check;"
   ```

3. **Check database schema:**
   ```bash
   sqlite3 $DATAPATH_BASE/cache.db ".schema server_room"
   ```

### Connection Issues

1. **Test SSH connectivity:**
   ```bash
   ssh user@host -p port
   ```

2. **Check VPN tunnel status:**
   ```bash
   vpnutil status
   ```

3. **Verify network connectivity:**
   ```bash
   ping host
   ```

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| File not found | Wrong path or filename | Check `DATAPATH_BASE` and filename |
| Parse error | Wrong delimiter format | Use `--` delimiter consistently |
| Database error | Permission or disk space | Check permissions and disk space |
| Connection failed | Network or authentication | Verify network and credentials |
| Tunnel not working | VPN configuration | Check tunnel profile and credentials |
| SSH key not found | Invalid key path | Verify SSH key file exists and is accessible |
| SSH auth failed | Key mismatch or permissions | Check key permissions and server's authorized_keys |

### Debug Mode

For detailed debugging, you can check the source code locations:

- **Command processing**: `machineroom/worker.py:124-131`
- **Import execution**: `machineroom/worker.py:21-22`
- **File parsing**: `machineroom/util.py:524-560`
- **Database operations**: `machineroom/sql.py:220-280`

---

## Conclusion

The import command is a powerful tool for managing multiple servers in MachineRoom. By following this documentation, you can effectively import server configurations, manage your infrastructure, and maintain secure access to your servers.

For additional help, refer to the main [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) documentation or check the source code for implementation details.
