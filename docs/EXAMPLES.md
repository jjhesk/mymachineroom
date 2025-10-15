# MachineRoom Examples

This document provides practical examples of how to use MachineRoom for various server management tasks.

## Table of Contents

1. [Basic Server Management](#basic-server-management)
2. [Docker Deployment Examples](#docker-deployment-examples)
3. [Configuration Management](#configuration-management)
4. [Monitoring and Health Checks](#monitoring-and-health-checks)
5. [Security and Certificate Management](#security-and-certificate-management)
6. [Batch Operations](#batch-operations)
7. [Custom Deployment Scripts](#custom-deployment-scripts)

## Basic Server Management

### Example 1: Simple Server List and Connection

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from machineroom.const import Config
from machineroom.worker import internal_work

# Configure MachineRoom
Config.DATAPATH_BASE = "/Users/yourusername/.machineroom"
Config.PUB_KEY = "/Users/yourusername/.ssh/id_rsa.pub"
Config.MY_KEY_FEATURE = "your-email@domain.com"

if __name__ == '__main__':
    internal_work()
```

**Usage:**
```bash
# List all servers
python3 server_manager.py ls

# Connect to a specific server
python3 server_manager.py web-01

# Import server list
python3 server_manager.py import production_servers.txt
```

### Example 2: Server Configuration File

Create `production_servers.txt` in your `DATAPATH_BASE` directory:

```
#prod-vpn--L2TP/IPSEC--vpn.company.com--vpnuser--vpnpass
web-01--192.168.1.100--root--password123--22
web-02--192.168.1.101--root--password123--22
db-primary--192.168.1.200--postgres--dbpass--5432
cache-redis--192.168.1.210--redis--cachepass--6379
api-server--10.0.0.50--ubuntu--mypassword--22
monitoring--10.0.0.60--admin--monitorpass--2222

# Example with SSH key authentication
kansas-server--203.0.113.100--admin------22--/Users/yourusername/.ssh/custom_key
prod-web--192.168.1.100--ubuntu------/Users/yourusername/.ssh/prod_key
```

## Docker Deployment Examples

### Example 3: Web Application Deployment

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from machineroom.taskbase import DeploymentBotFoundation, docker_launch, exec_docker_compose
from machineroom.const import Config
from fabric import Connection
import json

class WebAppDeployer(DeploymentBotFoundation):
    def __init__(self, server_room_file: str):
        super().__init__(server_room_file)
        self.app_name = "my-web-app"
        self.app_version = "2.1.0"
    
    def stage_0(self):
        print(f"🚀 Deploying {self.app_name} v{self.app_version} to {self.srv.current_id}")
    
    def stage_1(self, c: Connection):
        """Deploy web application"""
        # Check if already deployed
        if self.srv.local().get_res_kv(f"{self.app_name}_deployed"):
            print(f"⚠️  {self.app_name} already deployed on {self.srv.current_id}")
            return
        
        # Create application directory
        app_dir = f"/opt/{self.app_name}"
        c.run(f"mkdir -p {app_dir}", warn=True)
        
        # Create Docker Compose file
        docker_compose_content = f"""
version: '3.8'
services:
  {self.app_name}:
    image: nginx:alpine
    container_name: {self.app_name}
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - {app_dir}/html:/usr/share/nginx/html:ro
      - {app_dir}/conf:/etc/nginx/conf.d:ro
    restart: unless-stopped
    networks:
      - {self.app_name}-net

networks:
  {self.app_name}-net:
    driver: bridge
"""
        
        # Deploy with Docker Compose
        result = exec_docker_compose(c, app_dir, "docker-compose.yml", False)
        
        if result.ok:
            # Mark as deployed
            self.srv.local().update_res_kv(f"{self.app_name}_deployed", True)
            self.srv.local().update_res_kv(f"{self.app_name}_version", self.app_version)
            print(f"✅ {self.app_name} deployed successfully on {self.srv.current_id}")
        else:
            print(f"❌ Failed to deploy {self.app_name} on {self.srv.current_id}")

# Usage
if __name__ == '__main__':
    Config.DATAPATH_BASE = "/Users/yourusername/.machineroom"
    
    deployer = WebAppDeployer("production_servers.txt")
    deployer.run_conn()
```

### Example 4: Database Deployment

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from machineroom.taskbase import DeploymentBotFoundation, docker_launch
from machineroom.const import Config
from fabric import Connection

class DatabaseDeployer(DeploymentBotFoundation):
    def __init__(self, server_room_file: str, db_type: str = "postgres"):
        super().__init__(server_room_file)
        self.db_type = db_type
        self.db_configs = {
            "postgres": {
                "image": "postgres:15-alpine",
                "env_vars": ["POSTGRES_DB=myapp", "POSTGRES_USER=admin", "POSTGRES_PASSWORD=secret"],
                "ports": ["5432:5432"],
                "volumes": ["/opt/postgres/data:/var/lib/postgresql/data"]
            },
            "mysql": {
                "image": "mysql:8.0",
                "env_vars": ["MYSQL_ROOT_PASSWORD=rootpass", "MYSQL_DATABASE=myapp"],
                "ports": ["3306:3306"],
                "volumes": ["/opt/mysql/data:/var/lib/mysql"]
            },
            "redis": {
                "image": "redis:7-alpine",
                "ports": ["6379:6379"],
                "volumes": ["/opt/redis/data:/data"]
            }
        }
    
    def stage_1(self, c: Connection):
        """Deploy database"""
        if self.db_type not in self.db_configs:
            print(f"❌ Unsupported database type: {self.db_type}")
            return
        
        config = self.db_configs[self.db_type]
        container_name = f"{self.db_type}-db"
        
        # Check if already deployed
        if self.srv.local().get_res_kv(f"{self.db_type}_deployed"):
            print(f"⚠️  {self.db_type} already deployed on {self.srv.current_id}")
            return
        
        # Create data directory
        c.run(f"mkdir -p /opt/{self.db_type}/data", warn=True)
        
        # Deploy database container
        result = docker_launch(
            c=c,
            vol=config["volumes"],
            container_name=container_name,
            image=config["image"],
            ver="",
            command="",
            network=""
        )
        
        if result.ok:
            self.srv.local().update_res_kv(f"{self.db_type}_deployed", True)
            print(f"✅ {self.db_type} deployed successfully on {self.srv.current_id}")
        else:
            print(f"❌ Failed to deploy {self.db_type} on {self.srv.current_id}")

# Usage
if __name__ == '__main__':
    Config.DATAPATH_BASE = "/Users/yourusername/.machineroom"
    
    # Deploy PostgreSQL
    postgres_deployer = DatabaseDeployer("production_servers.txt", "postgres")
    postgres_deployer.run_conn()
    
    # Deploy Redis
    redis_deployer = DatabaseDeployer("production_servers.txt", "redis")
    redis_deployer.run_conn()
```

## Configuration Management

### Example 5: Nginx Configuration Deployment

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from machineroom.taskbase import DeploymentBotFoundation, exec_shell_program
from machineroom.const import Config
from fabric import Connection
import json

class NginxConfigDeployer(DeploymentBotFoundation):
    def __init__(self, server_room_file: str, config_template: str):
        super().__init__(server_room_file)
        self.config_template = config_template
    
    def stage_1(self, c: Connection):
        """Deploy Nginx configuration"""
        server_id = self.srv.current_id
        
        # Generate server-specific configuration
        config_content = self._generate_nginx_config(server_id)
        
        # Create deployment script
        script = f"""
        #!/bin/bash
        set -e
        
        echo "Configuring Nginx for {server_id}"
        
        # Backup existing configuration
        if [ -f /etc/nginx/sites-available/default ]; then
            cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup.$(date +%Y%m%d_%H%M%S)
        fi
        
        # Create new configuration
        cat > /etc/nginx/sites-available/default << 'EOF'
        {config_content}
        EOF
        
        # Test configuration
        nginx -t
        
        # Reload Nginx
        systemctl reload nginx
        
        echo "Nginx configuration applied successfully"
        """
        
        # Execute deployment script
        result = exec_shell_program(c, "/tmp", script)
        
        if result.ok:
            self.srv.local().update_res_kv("nginx_configured", True)
            print(f"✅ Nginx configured on {server_id}")
        else:
            print(f"❌ Failed to configure Nginx on {server_id}: {result.stderr}")
    
    def _generate_nginx_config(self, server_id: str) -> str:
        """Generate Nginx configuration"""
        # Get server-specific data
        self.srv.local().set_server_id(server_id)
        server_data = self.srv.local().get_member_res("server_room", server_id)
        
        # Replace placeholders in template
        config = self.config_template
        config = config.replace("{{SERVER_ID}}", server_id)
        config = config.replace("{{SERVER_HOST}}", self.srv.current_host)
        
        # Add custom settings based on server type
        if "web" in server_id.lower():
            config = config.replace("{{UPSTREAM_SERVERS}}", "127.0.0.1:8080")
        elif "api" in server_id.lower():
            config = config.replace("{{UPSTREAM_SERVERS}}", "127.0.0.1:3000")
        
        return config

# Usage
if __name__ == '__main__':
    Config.DATAPATH_BASE = "/Users/yourusername/.machineroom"
    
    nginx_template = """
server {{
    listen 80;
    server_name {{SERVER_HOST}};
    
    location / {{
        proxy_pass http://{{UPSTREAM_SERVERS}};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    location /health {{
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }}
}}
"""
    
    deployer = NginxConfigDeployer("production_servers.txt", nginx_template)
    deployer.run_conn()
```

## Monitoring and Health Checks

### Example 6: System Health Monitor

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from machineroom.taskbase import DeploymentBotFoundation
from machineroom.const import Config
from fabric import Connection
import json
import re

class HealthMonitor(DeploymentBotFoundation):
    def __init__(self, server_room_file: str):
        super().__init__(server_room_file)
        self.health_results = {}
        self.thresholds = {
            'cpu_usage': 80,
            'memory_usage': 85,
            'disk_usage': 90
        }
    
    def stage_1(self, c: Connection):
        """Perform health checks"""
        server_id = self.srv.current_id
        health_data = {}
        
        # Check CPU usage
        result = c.run("top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1", warn=True)
        if result.ok:
            cpu_usage = float(result.stdout.strip())
            health_data['cpu_usage'] = cpu_usage
            health_data['cpu_status'] = 'warning' if cpu_usage > self.thresholds['cpu_usage'] else 'ok'
        
        # Check memory usage
        result = c.run("free | grep Mem | awk '{printf \"%.1f\", $3/$2 * 100.0}'", warn=True)
        if result.ok:
            memory_usage = float(result.stdout.strip())
            health_data['memory_usage'] = memory_usage
            health_data['memory_status'] = 'warning' if memory_usage > self.thresholds['memory_usage'] else 'ok'
        
        # Check disk usage
        result = c.run("df -h / | awk 'NR==2{print $5}' | cut -d'%' -f1", warn=True)
        if result.ok:
            disk_usage = int(result.stdout.strip())
            health_data['disk_usage'] = disk_usage
            health_data['disk_status'] = 'warning' if disk_usage > self.thresholds['disk_usage'] else 'ok'
        
        # Check running services
        services = ['nginx', 'docker', 'ssh']
        health_data['services'] = {}
        for service in services:
            result = c.run(f"systemctl is-active {service}", warn=True)
            health_data['services'][service] = result.ok
        
        # Check network connectivity
        result = c.run("ping -c 1 8.8.8.8", warn=True)
        health_data['network_ok'] = result.ok
        
        # Store results
        self.health_results[server_id] = health_data
        self.srv.local().update_res_kv("health_data", json.dumps(health_data))
        
        # Print status
        status_icons = {'ok': '✅', 'warning': '⚠️', 'error': '❌'}
        print(f"🖥️  {server_id}:")
        print(f"   CPU: {health_data.get('cpu_usage', 'N/A')}% {status_icons.get(health_data.get('cpu_status', 'error'), '❌')}")
        print(f"   Memory: {health_data.get('memory_usage', 'N/A')}% {status_icons.get(health_data.get('memory_status', 'error'), '❌')}")
        print(f"   Disk: {health_data.get('disk_usage', 'N/A')}% {status_icons.get(health_data.get('disk_status', 'error'), '❌')}")
        print(f"   Network: {'✅' if health_data.get('network_ok') else '❌'}")
    
    def generate_report(self):
        """Generate health report"""
        print("\n📊 Health Check Report")
        print("=" * 60)
        
        total_servers = len(self.health_results)
        healthy_servers = 0
        warning_servers = 0
        error_servers = 0
        
        for server_id, data in self.health_results.items():
            has_warning = any(
                data.get(f'{metric}_status') == 'warning' 
                for metric in ['cpu', 'memory', 'disk']
            )
            has_error = not data.get('network_ok', False)
            
            if has_error:
                error_servers += 1
            elif has_warning:
                warning_servers += 1
            else:
                healthy_servers += 1
        
        print(f"Total servers: {total_servers}")
        print(f"Healthy: {healthy_servers} ✅")
        print(f"Warnings: {warning_servers} ⚠️")
        print(f"Errors: {error_servers} ❌")
        
        # Detailed report
        print("\nDetailed Status:")
        for server_id, data in self.health_results.items():
            status = "❌"
            if data.get('network_ok', False):
                if all(data.get(f'{metric}_status') == 'ok' for metric in ['cpu', 'memory', 'disk']):
                    status = "✅"
                else:
                    status = "⚠️"
            
            print(f"{status} {server_id}")

# Usage
if __name__ == '__main__':
    Config.DATAPATH_BASE = "/Users/yourusername/.machineroom"
    
    monitor = HealthMonitor("production_servers.txt")
    monitor.run_conn()
    monitor.generate_report()
```

## Security and Certificate Management

### Example 7: SSH Key Deployment

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from machineroom.taskbase import DeploymentBotFoundation, copy_id, detect_cert
from machineroom.const import Config
from fabric import Connection
import os

class SSHKeyDeployer(DeploymentBotFoundation):
    def __init__(self, server_room_file: str, key_path: str = None):
        super().__init__(server_room_file)
        self.key_path = key_path or Config.PUB_KEY
    
    def stage_1(self, c: Connection):
        """Deploy SSH key"""
        server_id = self.srv.current_id
        
        # Check if key is already deployed
        if detect_cert(c):
            print(f"✅ SSH key already deployed on {server_id}")
            self.srv.local().cert_install()
            return
        
        # Deploy SSH key
        try:
            copy_id(c, self.key_path)
            self.srv.local().cert_install()
            print(f"✅ SSH key deployed successfully on {server_id}")
        except Exception as e:
            print(f"❌ Failed to deploy SSH key on {server_id}: {e}")
    
    def verify_deployment(self):
        """Verify SSH key deployment across all servers"""
        print("\n🔐 SSH Key Deployment Verification")
        print("=" * 50)
        
        for server_id in self.srv.serv_count:
            self.srv.read_serv_at(server_id)
            if self.srv.local().is_cert_installed():
                print(f"✅ {server_id}: SSH key deployed")
            else:
                print(f"❌ {server_id}: SSH key not deployed")

# Usage
if __name__ == '__main__':
    Config.DATAPATH_BASE = "/Users/yourusername/.machineroom"
    
    # Deploy default SSH key
    deployer = SSHKeyDeployer("production_servers.txt")
    deployer.run_conn()
    deployer.verify_deployment()
    
    # Deploy custom SSH key
    custom_deployer = SSHKeyDeployer("production_servers.txt", "/path/to/custom_key.pub")
    custom_deployer.run_conn()
```

### Example 8: SSL Certificate Management

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from machineroom.taskbase import DeploymentBotFoundation, exec_shell_program
from machineroom.const import Config
from fabric import Connection
import os

class SSLCertDeployer(DeploymentBotFoundation):
    def __init__(self, server_room_file: str, cert_dir: str):
        super().__init__(server_room_file)
        self.cert_dir = cert_dir
    
    def stage_1(self, c: Connection):
        """Deploy SSL certificates"""
        server_id = self.srv.current_id
        
        # Check if certificates are already deployed
        if self.srv.local().get_res_kv("ssl_cert_deployed"):
            print(f"⚠️  SSL certificates already deployed on {server_id}")
            return
        
        # Create certificate deployment script
        script = f"""
        #!/bin/bash
        set -e
        
        echo "Deploying SSL certificates for {server_id}"
        
        # Create SSL directory
        mkdir -p /etc/ssl/certs/{server_id}
        
        # Copy certificate files
        cp {self.cert_dir}/cert.pem /etc/ssl/certs/{server_id}/
        cp {self.cert_dir}/key.pem /etc/ssl/private/{server_id}/
        cp {self.cert_dir}/chain.pem /etc/ssl/certs/{server_id}/
        
        # Set proper permissions
        chmod 644 /etc/ssl/certs/{server_id}/cert.pem
        chmod 600 /etc/ssl/private/{server_id}/key.pem
        chmod 644 /etc/ssl/certs/{server_id}/chain.pem
        
        # Update Nginx configuration
        cat > /etc/nginx/sites-available/{server_id}-ssl << 'EOF'
        server {{
            listen 443 ssl;
            server_name {self.srv.current_host};
            
            ssl_certificate /etc/ssl/certs/{server_id}/cert.pem;
            ssl_certificate_key /etc/ssl/private/{server_id}/key.pem;
            ssl_trusted_certificate /etc/ssl/certs/{server_id}/chain.pem;
            
            ssl_protocols TLSv1.2 TLSv1.3;
            ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
            ssl_prefer_server_ciphers off;
            
            location / {{
                return 200 "SSL Certificate Active\\n";
                add_header Content-Type text/plain;
            }}
        }}
        EOF
        
        # Enable site
        ln -sf /etc/nginx/sites-available/{server_id}-ssl /etc/nginx/sites-enabled/
        
        # Test and reload Nginx
        nginx -t && systemctl reload nginx
        
        echo "SSL certificates deployed successfully"
        """
        
        # Execute deployment script
        result = exec_shell_program(c, "/tmp", script)
        
        if result.ok:
            self.srv.local().update_res_kv("ssl_cert_deployed", True)
            print(f"✅ SSL certificates deployed on {server_id}")
        else:
            print(f"❌ Failed to deploy SSL certificates on {server_id}")

# Usage
if __name__ == '__main__':
    Config.DATAPATH_BASE = "/Users/yourusername/.machineroom"
    
    deployer = SSLCertDeployer("production_servers.txt", "/path/to/ssl/certificates")
    deployer.run_conn()
```

## Batch Operations

### Example 9: Mass Software Installation

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from machineroom.taskbase import DeploymentBotFoundation, exec_shell_program
from machineroom.const import Config
from fabric import Connection

class SoftwareInstaller(DeploymentBotFoundation):
    def __init__(self, server_room_file: str, software_list: list):
        super().__init__(server_room_file)
        self.software_list = software_list
    
    def stage_1(self, c: Connection):
        """Install software packages"""
        server_id = self.srv.current_id
        
        # Check if software is already installed
        installed_software = self.srv.local().get_res_kv("installed_software") or []
        
        for software in self.software_list:
            if software['name'] in installed_software:
                print(f"⚠️  {software['name']} already installed on {server_id}")
                continue
            
            # Create installation script
            script = self._create_install_script(software)
            
            # Execute installation
            result = exec_shell_program(c, "/tmp", script)
            
            if result.ok:
                installed_software.append(software['name'])
                print(f"✅ {software['name']} installed on {server_id}")
            else:
                print(f"❌ Failed to install {software['name']} on {server_id}")
        
        # Update installed software list
        self.srv.local().update_res_kv("installed_software", installed_software)
    
    def _create_install_script(self, software: dict) -> str:
        """Create installation script for software"""
        if software['type'] == 'apt':
            return f"""
            #!/bin/bash
            set -e
            apt update
            apt install -y {software['name']}
            """
        elif software['type'] == 'pip':
            return f"""
            #!/bin/bash
            set -e
            pip3 install {software['name']}
            """
        elif software['type'] == 'docker':
            return f"""
            #!/bin/bash
            set -e
            docker pull {software['name']}
            """
        elif software['type'] == 'custom':
            return software['install_script']
        else:
            return f"""
            #!/bin/bash
            echo "Unknown software type: {software['type']}"
            exit 1
            """

# Usage
if __name__ == '__main__':
    Config.DATAPATH_BASE = "/Users/yourusername/.machineroom"
    
    software_list = [
        {'name': 'htop', 'type': 'apt'},
        {'name': 'docker.io', 'type': 'apt'},
        {'name': 'requests', 'type': 'pip'},
        {'name': 'nginx:alpine', 'type': 'docker'},
        {
            'name': 'custom-app',
            'type': 'custom',
            'install_script': '''
            #!/bin/bash
            wget https://example.com/app.tar.gz
            tar -xzf app.tar.gz
            ./install.sh
            '''
        }
    ]
    
    installer = SoftwareInstaller("production_servers.txt", software_list)
    installer.run_conn()
```

## Custom Deployment Scripts

### Example 10: Complete Application Stack Deployment

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from machineroom.taskbase import DeploymentBotFoundation, exec_docker_compose, docker_launch
from machineroom.const import Config
from fabric import Connection
import json

class FullStackDeployer(DeploymentBotFoundation):
    def __init__(self, server_room_file: str, app_config: dict):
        super().__init__(server_room_file)
        self.app_config = app_config
    
    def stage_1(self, c: Connection):
        """Deploy complete application stack"""
        server_id = self.srv.current_id
        
        # Deploy in stages
        self._deploy_database(c)
        self._deploy_cache(c)
        self._deploy_application(c)
        self._deploy_nginx(c)
        self._setup_monitoring(c)
        
        # Mark as fully deployed
        self.srv.local().update_res_kv("full_stack_deployed", True)
        print(f"✅ Full stack deployed on {server_id}")
    
    def _deploy_database(self, c: Connection):
        """Deploy database"""
        if self.srv.local().get_res_kv("database_deployed"):
            return
        
        docker_launch(
            c=c,
            vol=["/opt/postgres/data:/var/lib/postgresql/data"],
            container_name="postgres-db",
            image="postgres:15-alpine",
            ver="",
            command="",
            network="app-network"
        )
        
        self.srv.local().update_res_kv("database_deployed", True)
    
    def _deploy_cache(self, c: Connection):
        """Deploy Redis cache"""
        if self.srv.local().get_res_kv("cache_deployed"):
            return
        
        docker_launch(
            c=c,
            vol=["/opt/redis/data:/data"],
            container_name="redis-cache",
            image="redis:7-alpine",
            ver="",
            command="",
            network="app-network"
        )
        
        self.srv.local().update_res_kv("cache_deployed", True)
    
    def _deploy_application(self, c: Connection):
        """Deploy main application"""
        if self.srv.local().get_res_kv("app_deployed"):
            return
        
        # Create application directory
        app_dir = "/opt/myapp"
        c.run(f"mkdir -p {app_dir}", warn=True)
        
        # Create Docker Compose file
        compose_content = """
version: '3.8'
services:
  app:
    image: myapp:latest
    container_name: myapp
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres-db:5432/myapp
      - REDIS_URL=redis://redis-cache:6379
    depends_on:
      - postgres-db
      - redis-cache
    networks:
      - app-network

networks:
  app-network:
    external: true
"""
        
        # Deploy with Docker Compose
        result = exec_docker_compose(c, app_dir, "docker-compose.yml", False)
        
        if result.ok:
            self.srv.local().update_res_kv("app_deployed", True)
    
    def _deploy_nginx(self, c: Connection):
        """Deploy Nginx reverse proxy"""
        if self.srv.local().get_res_kv("nginx_deployed"):
            return
        
        nginx_config = """
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://myapp:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /health {
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }
}
"""
        
        # Create Nginx configuration
        c.run("mkdir -p /etc/nginx/sites-available", warn=True)
        c.run(f"echo '{nginx_config}' > /etc/nginx/sites-available/myapp", warn=True)
        c.run("ln -sf /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/", warn=True)
        c.run("nginx -t && systemctl reload nginx", warn=True)
        
        self.srv.local().update_res_kv("nginx_deployed", True)
    
    def _setup_monitoring(self, c: Connection):
        """Setup monitoring"""
        if self.srv.local().get_res_kv("monitoring_deployed"):
            return
        
        # Deploy monitoring stack
        monitoring_compose = """
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    networks:
      - monitoring

networks:
  monitoring:
    driver: bridge
"""
        
        # Deploy monitoring
        result = exec_docker_compose(c, "/opt/monitoring", "docker-compose.yml", False)
        
        if result.ok:
            self.srv.local().update_res_kv("monitoring_deployed", True)

# Usage
if __name__ == '__main__':
    Config.DATAPATH_BASE = "/Users/yourusername/.machineroom"
    
    app_config = {
        'name': 'myapp',
        'version': '1.0.0',
        'database': 'postgres',
        'cache': 'redis',
        'monitoring': True
    }
    
    deployer = FullStackDeployer("production_servers.txt", app_config)
    deployer.run_conn()
```

These examples demonstrate the flexibility and power of the MachineRoom framework for various server management tasks. Each example can be customized and extended based on your specific requirements.
