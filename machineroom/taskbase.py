import pexpect
from fabric import Connection, Config as FabricConfig, Result
from machineroom.sql import ServerRoom
from machineroom.util import *


def copy_id(c: Connection, file: str = Config.PUB_KEY):
    '''fab push 公钥 ssh-copy-id'''
    print("copy_id operation")
    c.put(file, "/tmp/id.pub")
    try:
        c.run("if [ ! -d ~/.ssh ]; then mkdir -p ~/.ssh; fi")
        c.run(
            "if [ ! -f ~/.ssh/authorized_keys ]; then cp /tmp/id.pub ~/.ssh/authorized_keys && chmod 0600 ~/.ssh/authorized_keys; fi")
        c.run("cat ~/.ssh/authorized_keys /tmp/id.pub | sort -u > /tmp/uniq.authorized_keys")
        c.run(
            "if [ `cat ~/.ssh/authorized_keys | wc -l` -lt `cat /tmp/uniq.authorized_keys | wc -l` ]; then cat /tmp/id.pub >> ~/.ssh/authorized_keys; fi")
    finally:
        c.run("rm -f /tmp/id.pub /tmp/uniq.authorized_keys")


def exists(c: Connection, path: str) -> bool:
    r = c.run(f'stat {path}', warn=True, pty=True, hide=True)
    line = str(r.stdout.strip().replace("\n", ""))
    if "No such file or directory" in line:
        return False
    else:
        return True


def ensure_path_exist(c: Connection, path: str) -> bool:
    if exists(c, path) is False:
        print(f"make path for {path}")
        c.run(f"mkdir -p {path}", warn=True, pty=True)


# https://fabric-zh.readthedocs.io/_/downloads/zh-cn/latest/pdf/
def detect_cert(c: Connection) -> bool:
    r = c.run("cat ~/.ssh/authorized_keys", warn=True)
    line = str(r.stdout.strip().replace("\n", ""))
    t = True if Config.MY_KEY_FEATURE in line else False
    if t is True:
        print(f"certification found {Config.MY_KEY_FEATURE}")
    else:
        print(f"certification not found for {Config.MY_KEY_FEATURE}")
    return t


def detect_ram(d: Connection) -> float:
    r = d.run("awk '/Mem:/ {print $2}' <(free -h)", warn=True, pty=True, hide=True)
    line = str(r.stdout.strip().replace("\n", ""))
    try:
        if "Gi" in line:
            line = float(line.replace("Gi", ""))

        if "Mi" in line:
            line = float(line.replace("Mi", "")) / 1024
    except Exception as e:
        print(e)
        return 0.0

    return float(line)


def detect_program(c: Connection, program: str) -> bool:
    r = c.run(
        f'''command -v {program} >/dev/null 2>&1 || {{ echo >&2 "I require {program} but it's not installed. NOTFOUND. Aborting."; exit 1; }}''',
        warn=True, pty=True
    )
    line = str(r.stdout.strip().replace("\n", "")).replace("Gi", "")
    if "NOTFOUND" in line:
        return False
    return True


DETECT_PROCESS = 'ps aux | grep -sie "{COMMAND_NAME}" | grep -v "grep -sie"'


def detect_process(c: Connection, command: str) -> bool:
    print("detect program ", command)
    r = c.run(DETECT_PROCESS.format(COMMAND_NAME=command), pty=False, timeout=3000, warn=True)
    before = r.stdout.strip()
    if before == "":
        return False
    else:
        count = str(before).split("\n")
        return len(count) > 0


def detect_available_ports(c: Connection) -> list:
    print("检测并罗列未被占用的端口")
    r = exec_shell_global(c, PORT_DETECTION)
    ports = r.stdout.strip().split("\n")
    return ports


def install_python(c: Connection):
    c.run(PYTHON_CE, warn=True)


def install_docker_ce(c: Connection):
    exec_shell_global(c, DOCKER_CE_INSTALL)
    return True


def install_docker_compose(c: Connection):
    exec_shell_global(c, DOCKER_COMPOSE.format(
        DOCKER_COMPOSE_VERSION=Config.DOCKER_COMPOSE_VERSION
    ))


def run_context(c: Connection, block: str) -> Result:
    result = c.run(block, pty=False, echo=True)
    return result


def run_local_file(c: Connection, file_name: str) -> Result:
    script_file = open(file_name)
    result = c.run(script_file.read())
    script_file.close()
    return result


def exec_shell_global(c: Connection, _program_: str):
    return exec_shell_program(c, Config.HOME, _program_)


def exec_shell_program(c: Connection, remote_path: str, _program_: str) -> Result:
    buffer_file = BufferFile()
    buffer_file.new_bash()
    buffer_file.add_cmd(_program_)
    c.put(buffer_file.path, remote_path)
    return exec_shell(c, remote_path, buffer_file.execution_cmd)


def exec_shell_program_file(c: Connection, remote_path: str, program_file: BufferFile) -> Result:
    c.put(program_file.path, remote_path)
    return exec_shell(c, remote_path, program_file.execution_cmd)


def exec_shell(c: Connection, working_path: str, bash_file: str, empty_content_after_execution: bool = False) -> Result:
    cmd0 = f'cd {working_path} && {Config.BASH} {bash_file}'
    cmd1 = f'cd {working_path} && echo "" > {bash_file}'
    result = c.run(cmd0, pty=True, timeout=3000, warn=True)
    if result.ok and empty_content_after_execution:
        result = c.run(cmd1, pty=True, timeout=3600, warn=True)
    return result


def exec_docker_compose(c: Connection, working_path: str, yml_file: str, upgrade: bool = False) -> Result:
    cmd0 = f"cd {working_path} &&"
    if yml_file == "docker-compose.yml":
        if upgrade:
            cmd0 = cmd0 + f"{Config.DOCKER_COMPOSE} pull &&"
        cmd1 = cmd0 + f'{Config.DOCKER_COMPOSE} up -d'
        if upgrade:
            cmd1 = cmd1 + ' --force-recreate'
    else:
        if upgrade:
            cmd0 = cmd0 + f"{Config.DOCKER_COMPOSE} pull &&"
        cmd1 = cmd0 + f'{Config.DOCKER_COMPOSE} -f {yml_file} up -d'
        if upgrade:
            cmd1 = cmd1 + ' --force-recreate'

    return c.run(cmd1, pty=True, timeout=3600, warn=True, echo=True)


def exec_container_program(c: Connection, container_id: str, bash_line: str) -> Result:
    # cmd1 = f'cd {working_path} && docker exec {container_id} ckb miner'
    cmd2 = f'{Config.DOCKER} exec {container_id} {bash_line} &'
    return c.run(cmd2, pty=True, timeout=900, warn=True)


def deploy_container_with_docker_compose(
        c: Connection, docker_compose_file_content: str, force_recreate: bool = False
) -> Result:
    """
    please check if the docker-compose exists otherwise it will have a problem
    """
    tmp_file = BufferFile()
    tmp_file.setName("tmp_docker-compose.yml")
    tmp_file.add_cmd(docker_compose_file_content)
    remote_path = os.path.join(Config.REMOTE_WS, "docker-compose.yml")
    local_path = os.path.join(Config.DATAPATH_BASE, tmp_file.execution_cmd)
    c.put(local_path, remote_path)
    return exec_docker_compose(c, Config.REMOTE_WS, "docker-compose.yml", force_recreate)


def check_no_permission(c: Connection):
    check = "docker-compose"
    r = c.run(check, pty=True, timeout=100, warn=True, hide=True)
    if r.ok is False:
        line = str(r.stdout.strip().replace("\n", ""))
        if "Permission denied" in line:
            print("not permission from docker-compose")
            c.run("chmod +x /usr/bin/docker-compose", pty=True, timeout=100, warn=True)
    else:
        print("--- permission ok ---")


def system_init_test(c: Connection):
    # /root
    c.run("echo $HOME")
    # /usr/bin/bash
    c.run("echo $BASH")


def check_docker_ps(c: Connection, keywords: list, is_full_match: bool = False):
    r = c.run("docker ps", timeout=10)
    if r.ok:
        line = str(r.stdout.strip().replace("\n", ""))
        if is_full_match is False:
            for k in keywords:
                if k in line:
                    return True
        else:
            f = 0
            for k in keywords:
                if k in line:
                    f += 1
            return f == len(keywords)
    return False


def check_namespace_index_docker_ps(c: Connection, keywords: list) -> list[int]:
    r = c.run("docker ps", timeout=10)
    orders = []
    if r.ok:
        line = str(r.stdout.strip().replace("\n", ""))
        for k in keywords:
            if k in line:
                orders.append(keywords.index(k))
    return orders


def check_docker_ps_specific(c: Connection, keyword: str) -> bool:
    return check_docker_ps(c, [keyword])


def install_container_management_utility(c: Connection, out_bound_listing_port: int = 8000):
    if check_docker_ps_specific(c, "yacht") is True:
        print(f"management yacht is installed. it should be online {c.host}:{out_bound_listing_port}")
        return
    exec_shell_global(c, YACHT_INSTALL.format(LISTEN_PORT=out_bound_listing_port))
    print("[                       yacht is ready                      ]")
    print(f"{c.host}:{out_bound_listing_port} is ready for the web login")


# docker run -d -p 9055:8000 --restart unless-stopped -v /var/run/docker.sock:/var/run/docker.sock -v yacht:/config --name yacht selfhostedpro/yacht


class DeploymentBotFoundation:
    # the text file servers that recorded the authentications and some basic information
    srv: Servers
    # the local db connection of servers
    db: ServerRoom

    def __init__(self, server_room: str):
        # the server room file, usually "xxxx_server_room.txt", located under cache folder.
        self.srv = Servers(server_room)
        self.srv.detect_servers()

    def _config(self) -> FabricConfig:
        return FabricConfig({
            'run': {
                'watchers': [
                    DummyWatcher(),
                ],
            },
        })

    def _est_connection(self) -> Connection:
        if self.db.has_this_server() is False:
            return Connection(host=self.srv.current_host, port=22, user=self.srv.current_user, connect_kwargs={
                "password": self.srv.current_pass,
                # "key_filename": ['/Users/..../.ssh/id_rsa']
            }, config=self._config())
        elif self.db.is_cert_installed() is False:
            return Connection(host=self.srv.current_host, port=22, user=self.srv.current_user, connect_kwargs={
                "password": self.srv.current_pass,
                # "key_filename": ['/Users/..../.ssh/id_rsa']
            }, config=self._config())
        else:
            print("cert is installed.")
            return Connection(host=self.srv.current_host, port=22, user=self.srv.current_user, connect_kwargs={
                # "password": self.srv.current_pass,
                "key_filename": [Config.PUB_KEY]
            }, config=self._config())

    def connection_err(self, item: Exception, on_err_exit: bool):
        print("======================== exit.")
        print(self.srv.current_id, self.srv.current_host)
        if "Connection reset by peer" in str(item) or "Errno 54" in str(item):
            print("Maybe Offline")
        else:
            print(item)
        print("======================== exit.")
        if on_err_exit:
            exit(1)

    def handle_exceptions(self, e: Exception, fail_exit: bool = False) -> bool:
        if isinstance(e, pexpect.TIMEOUT):
            print("maybe a time out")
            return False
        elif isinstance(e, pexpect.EOF):
            print("maybe end of file")
            return False
        elif isinstance(e, ConnectionResetError):
            self.connection_err(e, fail_exit)
            return False
        else:
            self.connection_err(e, fail_exit)
            return True

    def stage_1(self, c: Connection):
        self.db.tipping_point(
            self.srv.current_user, self.srv.current_id,
            self.srv.current_host, self.srv.current_pass
        )
        for key in Config.STAGE1:
            self._stage_loop(c, key)

    def load_system_paths(self, c: Connection):
        r = c.run("which bash", warn=True, pty=True)
        if str(r.stdout.strip()) != "":
            Config.BASH = str(r.stdout.strip())
        r = c.run("which docker", warn=True, pty=True)
        if str(r.stdout.strip()) != "":
            Config.DOCKER = str(r.stdout.strip())
        r = c.run("which docker-compose", warn=True, pty=True)
        if str(r.stdout.strip()) != "":
            Config.DOCKER_COMPOSE = str(r.stdout.strip())

    def _stage_loop(self, c: Connection, task: str):
        if task == "cert":
            if self.db.is_cert_installed() is False:
                if detect_cert(c) is False:
                    copy_id(c, Config.PUB_KEY)
                    self.db.cert_install()
                else:
                    self.db.cert_install()

        if task == "env":
            c.config.load_shell_env()
            self.load_system_paths(c)

        if task == "docker":
            if self.db.is_docker_ce_installed() is False:
                if detect_program(c, "docker") is False:
                    install_docker_ce(c)
                    self.db.docker_ce_install()
                else:
                    print("DOCKER is installed")

        if task == "docker-compose":
            if self.db.is_docker_compose_installed() is False:
                if detect_program(c, "docker-compose") is False:
                    install_docker_compose(c)
                    self.db.docker_compose_install()
                else:
                    print("DOCKER COMPOSE is installed")
                    check_no_permission(c)

        if task == "yacht9099":
            if self.db.is_docker_yacht_installed() is False:
                install_container_management_utility(c, 9099)
                self.db.docker_yacht_install()

        if task == "python":
            if self.db.is_python_installed() is False:
                if detect_program(c, "python3") is False:
                    print("python3 needs to install")
                    install_python(c)

        if task == "yacht8221":
            if self.db.is_docker_yacht_installed() is False:
                install_container_management_utility(c, 8221)
                self.db.docker_yacht_install()

        if task == "yacht9055":
            if self.db.is_docker_yacht_installed() is False:
                install_container_management_utility(c, 9055)
                self.db.docker_yacht_install()
