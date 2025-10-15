# Import Command Quick Reference

## Command Syntax
```bash
connect import <filename>
```

## File Format
```
server_id--host--user--password--port--ssh_key_path
```

## Example File
```
#tunnel-profile--L2TP/IPSEC--vpn.server.com--user--pass
web-01--192.168.1.100--root--password123--22
db-01--192.168.1.200--postgres--dbpass--5432
kansas-server--204.12.246.204--kliner------22--/Users/hesdx/.ssh/kansas_rsa
```

## Supported Delimiters
- `--` (recommended)
- `---`
- `----`
- `——`
- `————`

## Common Commands
```bash
# Import servers
connect import servers.txt

# List imported servers
connect ls

# Connect to server
connect web-01

# Add SSH certificate
connect add-cert mykey /path/to/key.pub
```

## File Location
Place server files in: `$DATAPATH_BASE/`

## Troubleshooting
- **File not found**: Check file exists in `DATAPATH_BASE`
- **Parse error**: Use `--` delimiter consistently
- **Connection failed**: Verify network and credentials
- **SSH key not found**: Verify SSH key file exists and is accessible
- **SSH auth failed**: Check key permissions and server's authorized_keys

## Example Template
See `docs/example_servers.txt` for a complete template.

---
For detailed documentation, see [IMPORT_COMMAND.md](IMPORT_COMMAND.md)
