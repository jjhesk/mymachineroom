## Machine Room Management on my console

Locate and manage all my machines on my console.

## Why

### mymachineroom - Automation Features for DevOps Workloads

`mymachineroom` is designed to streamline DevOps workflows through automation, enabling efficient setup, configuration, and management of development and production environments. Below are the key automation features inferred from the repository's context and related projects by jjhesk.

## Features

- **Automated Tool and Dependency Installation**
  - One-line installation scripts using `wget` or `curl` for tools like Homebrew, Go, Node.js, and Python dependencies.
  - Configures custom package mirrors for reliable downloads in restricted network environments.

- **System and Environment Configuration**
  - Automates disk partitioning, file system setup, and network configurations for Linux systems (e.g., CentOS, Ubuntu).
  - Initializes services like PostgreSQL, IPFS, or containerized applications for rapid environment provisioning.

- **Blockchain and Distributed System Automation**
  - Streamlines setup of blockchain nodes (e.g., Chainlink, Ethereum clients) and smart contract environments.
  - Automates deployment and testing of decentralized applications for Web3-focused DevOps workflows.

- **CI/CD Pipeline Integration**
  - Facilitates setup of CI/CD tools like GitHub Actions or Jenkins for automated code deployment and testing.
  - Configures notification systems (e.g., Slack, email) to alert teams about pipeline events or failures.

- **Monitoring and Logging Setup**
  - Automates deployment of monitoring tools (e.g., Prometheus, Grafana) for real-time system performance tracking.
  - Configures log aggregation and parsing for efficient debugging and system health monitoring.

- **Cross-Platform and Scalable Automation**
  - Supports multiple Linux distributions and potentially other platforms for consistent environment setups.
  - Enables scalable server configurations, including load balancers and container orchestration.

- **Customizable Automation Scripts**
  - Provides modular, customizable scripts with configuration files or environment variables for tailored DevOps needs.
  - Supports extensible automation logic for project-specific requirements.

> **Note**: These features are inferred based on jjhesk’s related projects (e.g., `cninstall`) due to limited public documentation for `mymachineroom`. For precise details, refer to the repository’s scripts or contact the author.

## SDK-Extensive Infrastructure

- [x] Infra1
- [x] Infra2
- [x] Basic worker bot implementation

## Current features

List IPs
Sync the ip list into the local record
Manage authentications
Add certificate
Remove certificate

## Installation

There are no requirements for this tool.

```
pip3 install machineroom
```

or if you want to get the upgrade

```
sudo pip3 install machineroom --upgrade
```

### Create bin file for easy execution

on macosx

```
#!/Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11
# -*- coding: utf-8 -*-


# setup your desired configuration path in the local machine
import machineroom.const.Config
Config.DATAPATH_BASE = "...."
Config.PUB_KEY = "...."


from machineroom.worker import internal_work

if __name__ == '__main__':
    internal_work()


```

### The configurations are available as below

```
DATAPATH_BASE = "...._file....locator"
TEMP_FILE = "tmp.txt"
TEMP_JS = "tmp.js"
REMOTE_WS = "...remote_locator"
RAM_GB_REQUIREMENT = 4
PUB_KEY = "/Users/xxxx/.ssh/id_rsa.pub"
LOCAL_KEY_HOLDER = "/Users/xxxx/.ssh"
MY_KEY_FEATURE = "xxxx@xxxxx"
REMOTE_HOME = "/root"
DOCKER_COMPOSE_VERSION = "2.24.6"
```

## Usage

```
usage: connect [-h] [server id]

optional arguments:
  -h, --help            Show this help message and exit
  -ls,                  Show a list of the existing servers in my list
  -scan,                Scan the existing server in the access list for health check
  -import, --from       the import list of the server file within the given format
```

### Example

```
connect serverabc
```

connect the console to the existing machine in ssh

```
connect ls
```

### License

MIT License (2022), Jun-You Liu, Heskemo BTC
