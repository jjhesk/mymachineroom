# Machine Room Management on my console

Locate and manage all my machines on my console.

## Introduction

Congratulations on utilizing technology to improve your machine room management! Having a machine room management app on your console, easily accessible at your fingertips, is a game-changer. It streamlines processes, increases efficiency, and allows you to stay on top of everything with ease. By taking advantage of this tool, you are not only simplifying your workload but also paving the way for future success. Keep up the great work and continue to embrace innovation in your everyday tasks. You've got this!

## Why

1. Improved efficiency: By having all machines located and managed on one console, you can easily track and monitor their performance, making it easier to identify and address issues quickly. This can help to prevent downtime and keep your operations running smoothly.

2. Centralized control: Having all machines on one console allows for centralized control and management, making it easier to implement changes, updates, or maintenance tasks across all machines simultaneously.

3. Increased visibility: With all machines located on one console, you have greater visibility into the status and performance of each machine, allowing you to make more informed decisions and better plan for maintenance and upgrades.

4. Enhanced security: Centralized management of all machines can help to improve security by providing better oversight of access controls, security settings, and compliance with policies and regulations.

5. Cost savings: Managing all machines on one console can help to reduce operational costs by streamlining processes, improving efficiency, and reducing the need for manual intervention.

6. Scalability: As your operations grow, having all machines on one console makes it easier to scale up and add new machines, without the need for additional management tools or resources.

7. Improved collaboration: Centralized management of all machines can facilitate better collaboration among team members, as everyone can access the same data, reports, and tools from one console.


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
from machineroom.worker import internal_work
"""

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


"""
if __name__ == '__main__':
    internal_work()


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
