class PROJECT1:
    REMOTE_WS: str = "...remote_locator"
    RAM_GB_REQUIREMENT: int = 4
    DISK_GB_REQUIREMENT: int = 100
    CONTAINER_NAME_IDS: list = []


class PROJECT2:
    YACHT_API_KEY: str = "---paste here---"


class COMMAND_PATH:
    BASH = "/usr/bin/bash"
    DOCKER_COMPOSE_VERSION: str = "2.24.6"
    DOCKER_COMPOSE = "/usr/local/bin/docker-compose"
    DOCKER = "/usr/bin/docker"


class Config(COMMAND_PATH, PROJECT1, PROJECT2):
    DATAPATH_BASE: str = "...._file....locator"
    TEMP_FILE: str = "tmp.txt"
    TEMP_JS: str = "tmp.js"
    PUB_KEY: str = "/Users/xxxx/.ssh/id_rsa.pub"
    LOCAL_KEY_HOLDER: str = "/Users/xxxx/.ssh"
    MY_KEY_FEATURE: str = "xxx@xxxx"
    HOME: str = "/root"
    STAGE1 = ["cert", "docker", "docker-compose", "env"]


HEALTH_CHK_DB = """
docker run --rm -it --mount type=bind,source={PWD},destination=/data sstc/sqlite3 find . -maxdepth 1 -iname "*.db" -print0 -exec sqlite3 '{}' 'PRAGMA integrity_check;' ';'
"""

HEALTH_CHK_DB2 = """
sudo apt update && sudo apt install sqlite3 -y
sqlite3 --version
sqlite3 {DB_FILE_PATH} "PRAGMA integrity_check;"
"""

STOP_CONTAINER_BY_NAME = """
container_id=$(docker ps -q -a -f status=running --filter name={CONTAINER_NAME})
docker stop $container_id
docker rm -v {CONTAINER_NAME}
"""

DOCKER_REMOVE_EXIT = """
docker ps --filter status=exited -q | xargs docker rm
"""

DOCKER_CLEAR_CACHE = """
docker builder prune --all -y
"""

YACHT_INSTALL = """
docker volume create yacht
docker run -d -p {LISTEN_PORT}:8000 --restart unless-stopped -v /var/run/docker.sock:/var/run/docker.sock -v yacht:/config --name yacht selfhostedpro/yacht
"""
DOCKER_COMPOSE="""
DOCKER_VER={DOCKER_COMPOSE_VERSION}
sudo curl -L "https://github.com/docker/compose/releases/download/v$DOCKER_VER/docker-compose-$(uname -s)-$(uname -m)" -o /usr/bin/docker-compose
chmod +x /usr/bin/docker-compose
"""
DOCKER_CE_INSTALL="""curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88
sudo add-apt-repository \
"deb [arch=amd64] https://download.docker.com/linux/ubuntu \
$(lsb_release -cs) \
stable"
sudo apt-get update
sudo apt-get install -y docker-ce
sudo apt-get update
sudo groupadd docker
sudo usermod -aG docker $USER
sudo systemctl enable docker"""
PYTHON_CE="""sudo apt-get install -y \
apt-transport-https \
ca-certificates \
curl \
software-properties-common \
python3"""

PORT_DETECTION="""
# 检测并罗列未被占用的端口
function list_recommended_ports {
    local start_port=8000 # 可以根据需要调整起始搜索端口
    local needed_ports=7
    local count=0
    local ports=()

    while [ "$count" -lt "$needed_ports" ]; do
        if ! ss -tuln | grep -q ":$start_port " ; then
            ports+=($start_port)
            ((count++))
        fi
        ((start_port++))
    done

    echo "推荐的端口如下："
    for port in "${ports[@]}"; do
        echo -e "\033[0;32m$port\033[0m"
    done
}
list_recommended_ports;"""