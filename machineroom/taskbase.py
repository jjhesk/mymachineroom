import os.path

import pexpect
from fabric import Connection, Config as FabricConfig, Result
from machineroom.sql import ServerRoom
from machineroom.tunnels import conn
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
        return False
    return True


def upload_cache_file(c: Connection, cache_file_name: str, if_not_exist: bool = False):
    remote_path = os.path.join(Config.REMOTE_WS, "cache", cache_file_name)
    local_path = os.path.join(Config.WS_LOCAL, "cache", cache_file_name)
    if if_not_exist is True:
        if exists(c, remote_path) is False:
            c.put(local_path, remote_path)
    else:
        c.put(local_path, remote_path)


def upload_cache_file_modify(c: Connection, cache_file_name: str, modifier, if_not_exist: bool = False):
    remote_path = os.path.join(Config.REMOTE_WS, "cache", cache_file_name)
    local_path = os.path.join(Config.WS_LOCAL, "cache", cache_file_name)
    local_mod_path = os.path.join(Config.WS_LOCAL, "cache", "mod_" + cache_file_name)

    if callable(modifier):
        io = open(local_path, "r")
        content = io.read()
        io.close()
        new_content = modifier(content)

        io = open(local_mod_path, "w")
        io.write(new_content)
        io.close()

    if os.path.isfile(local_mod_path):
        if if_not_exist is True:
            if exists(c, remote_path) is False:
                c.put(local_mod_path, remote_path)
        else:
            c.put(local_mod_path, remote_path)
        os.remove(local_mod_path)


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


def detect_cert_signature(c: Connection, machine_name: str) -> bool:
    r = c.run("cat ~/.ssh/authorized_keys", warn=True)
    line = str(r.stdout.strip().replace("\n", ""))
    t = True if machine_name in line else False
    if t is True:
        print(f"certification found {machine_name}")
    else:
        print(f"certification not found for {machine_name}")
    return t


def detect_assigned_IP_addresses(c: Connection) -> list[str]:
    r = c.run("""ip addr show eth0 | grep "inet\b" | awk '{print $2}' | cut -d/ -f1""", warn=True, pty=True, hide=True)
    the_list_ips = str(r.stdout.strip()).split("\n")
    return the_list_ips


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


def run_context(c: Connection, block: str) -> Result:
    result = c.run(block, pty=False, echo=True)
    return result


def run_local_file(c: Connection, file_name: str) -> Result:
    script_file = open(file_name)
    result = c.run(script_file.read())
    script_file.close()
    return result


def exec_shell_global(c: Connection, _program_: str):
    return exec_shell_program(c, Config.SYSTEM_TEMP, _program_)


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


# Back up related commands
def safe_cache_backup(c: Connection, local_file_name: str):
    """
    safely backup the working cache file in the remote server
    download the gz db to local
    """
    original_rm = os.path.join(Config.REMOTE_WS, "cache", "cache.db")
    remote_path = os.path.join(Config.REMOTE_WS, "cache", local_file_name)
    t = BACKUP_CACHE_FAST.replace("_CFP_", original_rm).replace("_FR_", local_file_name)
    exec_shell_program(c, "/tmp", t)
    local_path = os.path.join(Config.WS_LOCAL, "cache", "server_backups", local_file_name)
    c.get(remote_path, local_path)
    print("Download successful")
    return local_path


def open_backup_cache_local(local_path) -> str:
    """
    the final local path of the cache file backup
    """
    local_fz = os.path.join(Config.WS_LOCAL, "cache", "server_backups", "cache.db")
    (p, f) = os.path.split(local_path)
    # local_compressed = os.path.join(WS_LOCAL, "cache", local_file_name)
    # local_fz = os.path.join(WS_LOCAL, "cache", local_file_name.replace(".tar.gz", ""))
    # db_name_x = f.replace(".tar.gz", "")
    # local_pd = os.path.join(WS_LOCAL, "cache")
    local_cmd = f'cd {p} && tar -xvf {f}'
    print(local_cmd)
    os.system(local_cmd)
    # os.renames("cache.db", db_name_x)
    os.chdir(Config.WS_LOCAL)
    # return os.path.join(p, db_name_x)
    return local_fz


# Docker related commands in library

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


def stop_rm_container(c: Connection, container_name: str):
    cmd_line_go1 = DOCKER_STOP_CONTAIN_NAME.format(
        COMMAND_DOCKER=Config.DOCKER,
        CONTAINER_NAME=container_name
    )
    cmd_line_go2 = DOCKER_RM_NAME_BASED.format(
        COMMAND_DOCKER=Config.DOCKER,
        CONTAINER_NAME=container_name
    )
    buf_fi = BufferFile()
    buf_fi.new_bash()
    buf_fi.add_cmd(cmd_line_go1)
    buf_fi.add_cmd(cmd_line_go2)
    exec_shell_program_file(c, "/tmp", buf_fi)


def docker_is_container_conflict(rs: Result):
    line = str(rs.stdout)
    if "Error response from daemon: Conflict. The container name" in line:
        # Regular expression pattern to extract the hash inside double quotes
        pattern = r'"([a-fA-F0-9]+)"'
        # Find all occurrences of the pattern in the error message
        hashes = re.findall(pattern, line)
        return True, hashes[0]
    else:
        return False, ""


def docker_solve_conflict(c: Connection, hash: str):
    c.run(DOCKER_STOP_ID.format(CID=hash, COMMAND_DOCKER=Config.DOCKER), pty=True, timeout=100, warn=True, echo=True)
    c.run(DOCKER_STOP_RM.format(CID=hash, COMMAND_DOCKER=Config.DOCKER), pty=True, timeout=100, warn=True, echo=True)


def docker_get_container_ids_by_keyword(c: Connection, keyword: str) -> list:
    command = '__DOCKER__ ps -aqf "name=^______"'.replace('______', keyword).replace('__DOCKER__', Config.DOCKER)
    r = c.run(command, pty=True, timeout=1900, hide=True, warn=True, echo=False)
    reblock = r.stdout.replace("\r", "")
    ids = reblock.split('\n')
    container__ids = []
    for container__id in ids:
        if container__id != '':
            container__ids.append(container__id)
    container__ids = list(set(container__ids))
    return container__ids


def docker_read_console_result():
    io = open(os.path.join(Config.DATAPATH_BASE, 'command_prompt_tmp'), 'r')
    content = io.read()
    io.close()
    return json.loads(content)


def docker_save_console_result(r):
    content = r.stdout
    io = open(os.path.join(Config.DATAPATH_BASE, 'command_prompt_tmp'), 'w')
    io.write(content)
    io.close()


def docker_inspect_file(c: Connection, container_id: str):
    command = f'docker inspect {container_id}'
    r = c.run(command, pty=True, timeout=1900, hide=True, warn=True, echo=False)
    docker_save_console_result(r)
    return docker_read_console_result()


def docker_restart_containers(c: Connection, contain_ids, result_line=None):
    if isinstance(contain_ids, list):
        for id in contain_ids:
            rv = c.run(
                f"{Config.DOCKER} restart {id}",
                pty=True, timeout=1900, warn=True, echo=True
            )
            if callable(result_line):
                line = str(rv.stdout.strip().replace("\n", "")).lower()
                result_line(line, id)

    if isinstance(contain_ids, str):
        rv = c.run(
            f"{Config.DOCKER} restart {contain_ids}",
            pty=True, timeout=1900, warn=True, echo=True
        )
        if callable(result_line):
            line = str(rv.stdout.strip().replace("\n", "")).lower()
            result_line(line, contain_ids)


def docker_launch(c: Connection, vol: Union[str, list[str]], container_name: str, image: str, ver: str, command: str,
                  network: str = "", bind_file: Union[str, list[str]] = "") -> Result:
    _vol = ""
    if isinstance(vol, str):
        _vol = f" -v {vol}"
    if isinstance(vol, list):
        _vol = " -v " + " -v ".join(vol)

    if network != "":
        _net = "--net " + network
    else:
        _net = ""

    if ver == "" or ver is None:
        _ver = ""
    else:
        _ver = f":{ver}"
    _bindf = ""
    if isinstance(bind_file, str):
        if bind_file != "":
            u = bind_file.split(":")
            if len(u) == 2:
                _bindf = DOCKER_MOUNT_FILE.format(SOURCE=u[0], TARGET=u[1])
            if len(u) == 3 and u[2] == "ro":
                _bindf = DOCKER_MOUNT_FILE_RO.format(SOURCE=u[0], TARGET=u[1])

    if isinstance(bind_file, list):
        _sl = []
        for vv in bind_file:
            u = vv.split(":")
            mount_statement = ""
            if len(u) == 2:
                mount_statement = DOCKER_MOUNT_FILE.format(SOURCE=u[0], TARGET=u[1])
            if len(u) == 3 and u[2] == "ro":
                mount_statement = DOCKER_MOUNT_FILE_RO.format(SOURCE=u[0], TARGET=u[1])
            _sl.append(mount_statement)
        _bindf = " ".join(_sl)

    return c.run(DOCKER_LAUNCH_LINE.format(
        COMMAND_DOCKER=Config.DOCKER,
        VOLUME=_vol,
        NETWORK=_net,
        NODE_NAME=container_name,
        IMAGE=image,
        VERSION=_ver,
        COMMAND=command,
        BIND_FILE=_bindf,
        LOG_POLICY=Config.DOCKER_LOG_POLICY
    ), pty=True, timeout=4900, warn=True, echo=True)


def stop_container_by_name(c: Connection, container_name: str):
    cmd_line_go = DOCKER_STOP_CONTAIN_NAME.format(
        COMMAND_DOCKER=Config.DOCKER,
        CONTAINER_NAME=container_name
    )
    return c.run(cmd_line_go, pty=True, timeout=1900, warn=True, echo=True)


def docker_stop_by_prefix(c: Connection, word: str):
    service = """docker stop $(docker ps | grep "KEY_WORD" | cut -d " " -f1)""".replace('KEY_WORD', word)
    c.run(service, pty=True, timeout=1900, warn=True, echo=True)


def rm_container_by_name(c: Connection, container_name: str):
    cmd_line_go = DOCKER_RM_NAME_BASED.format(
        COMMAND_DOCKER=Config.DOCKER,
        CONTAINER_NAME=container_name
    )
    return c.run(cmd_line_go, pty=True, timeout=1900, warn=True, echo=True)


def rm_vol_by_name(c: Connection, container_name: str):
    cmd_line_go = DOCKER_RM_VOLUME.format(
        COMMAND_DOCKER=Config.DOCKER,
        CONTAINER_NAME=container_name
    )
    return c.run(cmd_line_go, pty=True, timeout=1900, warn=True, echo=True)


def log_review(c: Connection, container_word: str, log_recent_lines: int):
    """
    show the docker logs
    """
    pick_logs = DOCKER_LOG_REVIEW.replace("COMMAND_DOCKER", Config.DOCKER)
    pick_logs = pick_logs.replace("__CONTAINER_KEYWORD", container_word)
    pick_logs = pick_logs.replace("__RECENT_LINES", str(log_recent_lines))
    return c.run(pick_logs, pty=True, timeout=1900, warn=True, echo=True)


def exec_container_program(c: Connection, container_id: str, bash_line: str) -> Result:
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
    print(
        f"{c.host}:{out_bound_listing_port} is ready for the web login. Try to use chrome to open with [admin@yacht.local : pass]")


def run_yacht_restart(c: Connection, port: str):
    return c.run(RUN_YACHT.format(LISTEN_PORT=port), pty=True, timeout=300, warn=True)


def install_dae_proxy(c: Connection):
    return c.run(INSTALL_DAED, pty=True, timeout=900, warn=True)


def install_watch_tower(c: Connection):
    return c.run(INSTALL_WATCH_TOWER, pty=True, timeout=2900, warn=True)


def install_python(c: Connection):
    return c.run(PYTHON_CE, warn=True)


def install_docker_ce(c: Connection):
    exec_shell_global(c, DOCKER_V25_INSTALL)
    return True


def install_docker_25(c: Connection):
    exec_shell_global(c, DOCKER_V25_INSTALL)
    return True


def install_docker_compose(c: Connection):
    exec_shell_global(c, DOCKER_COMPOSE.format(
        DOCKER_COMPOSE_VERSION=Config.DOCKER_COMPOSE_VERSION
    ))


def docker_launch_solution(c: Connection, node_name: str, pass_file: str):
    print("use container name", node_name)
    _command_line = f"python main_exe.py {pass_file}"
    sentence = docker_launch(
        c=c,
        container_name=node_name,
        vol="/home/galxeionetapplication/cache:/home/galxe/cache",
        image="adriansteward/galxewrok",
        ver="",
        command=_command_line
    )
    (issue, hash) = docker_is_container_conflict(sentence)
    if issue:
        docker_solve_conflict(c, hash)
        docker_launch_solution(c, node_name, pass_file)


def docker_get_network_name_by_container_id(c: Connection, container_id: str) -> str:
    content = DOCKER_GET_NETWORK_NAME.replace("COMMAND_DOCKER", Config.DOCKER).replace("CONTAINER_ID", container_id)
    r = c.run(content, timeout=90, warn=True, hide=True)
    if r.ok:
        return str(r.stdout.strip().replace("\n", ""))
    return ""


def docker_get_container_id_by_keyword(c: Connection, keyword: str) -> str:
    content = DOCKER_GET_CONTAINER_ID.replace("COMMAND_DOCKER", Config.DOCKER).replace("__IMAGE_NAME_OR_KEYWORD__",
                                                                                       keyword)
    r = c.run(content, timeout=90, warn=True, hide=True)
    if r.ok:
        return str(r.stdout.strip().replace("\n", ""))
    return ""


def install_clash_network(
        c: Connection,
        network_config_file: str,
        helper_version: str,
        external_token_access: str,
        selector: str,
        tst_endpoint: str
):
    # network config is yaml file format
    docker_file = DOCKER_COMPOSE_XCLASH \
        .replace("X_CLASH_CONFIG_YAML_NM", network_config_file) \
        .replace("X_CLASH_GALXE_HELPER_VER", "1.2.1291" if helper_version == "" else helper_version)

    processed_selector = selector.encode('utf-16', 'surrogatepass').decode(
        'utf-16').encode("raw_unicode_escape").decode("utf-8")

    resrc = CLASH_HELPER_RESOURCE \
        .replace("___SECRET___", external_token_access) \
        .replace("___SELECTOR___", processed_selector).replace(
        "__TEST_ENDPOINT__", tst_endpoint)

    network_cfg = os.path.join("/home", "clashperfectoctopus", "clash_conf", network_config_file)
    network_cfg_local = os.path.join(Config.DATAPATH_BASE, "clash_config", network_config_file)
    content = CLASH_SETUP_1 \
        .replace("_CONTENT_DOCKER_COMPOSE", docker_file) \
        .replace("_RESOURCE_JSON", resrc)

    exec_shell_program(c, "/tmp", content)
    if os.path.isfile(network_cfg_local) is False:
        print("aborted the network config file is not found from", network_cfg_local)
        return

    if exists(c, network_cfg) is False:
        c.put(network_cfg_local, network_cfg)

    content2 = CLASH_SETUP_2 \
        .replace("_PATH_CLASH", network_cfg)
    exec_shell_program(c, "/tmp", content2)


class DeploymentBotFoundation:
    # the text file servers that recorded the authentications and some basic information
    srv: Servers
    # the local db connection of servers
    db: ServerRoom
    start_server_from: int
    stop_server_at: int
    start_server_in_list: list[int]

    def __init__(self, server_room: str):
        # the server room file, usually "xxxx_server_room.txt", located under cache folder.
        self.srv = Servers(server_room)
        self.start_server_from = 0
        self.stop_server_at = self.srv.serv_count - 1
        self.start_server_in_list = []
        self.srv.detect_servers()

    def _config(self) -> FabricConfig:
        return FabricConfig({
            'run': {
                'watchers': [
                    DummyWatcher(),
                ],
            },
        })

    def run_tunnel_detection(self):
        if self.srv.tunnel_type == TunnelType.NO_TUNNEL:
            return False
        conn.use_macos_vpn_on(self.srv.profile_name)
        return True

    def run_tunnel_detection_off(self):
        if self.srv.tunnel_type == TunnelType.NO_TUNNEL:
            return
        conn.use_macos_vpn_off(self.srv.profile_name)

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

    def stage_0(self):
        if self.srv.tunnel_type == TunnelType.NO_TUNNEL:
            self.db.tipping_point(
                self.srv.current_user, self.srv.current_id,
                self.srv.current_host, self.srv.current_pass
            )
        else:
            self.db.tipping_point_tunnel(
                self.srv.profile_name, self.srv.current_user, self.srv.current_id,
                self.srv.current_host, self.srv.current_pass)

    def stage_1(self, c: Connection):
        for key in Config.STAGE1:
            self._stage_loop(c, key)

    def load_system_paths(self, c: Connection):
        r = c.run("which bash", warn=True, pty=True)
        if str(r.stdout.strip()) != "":
            Config.BASH = str(r.stdout.strip())
        r = c.run("which docker", warn=True, pty=True)
        if str(r.stdout.strip()) != "":
            Config.DOCKER = str(r.stdout.strip())
            self.db.docker_ce_install()
        r = c.run("which docker-compose", warn=True, pty=True)
        if str(r.stdout.strip()) != "":
            Config.DOCKER_COMPOSE = str(r.stdout.strip())
            self.db.docker_compose_install()
        r = c.run("which daed", warn=True, pty=True)
        if str(r.stdout.strip()) != "":
            self.db.dae_install()

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
            else:
                install_docker_ce(c)

        if task == "python":
            if self.db.is_python_installed() is False:
                if detect_program(c, "python3") is False:
                    print("python3 needs to install")
                    install_python(c)
                    self.db.python3_install()

        if task == "daed":
            if self.db.is_dae_installed() is False:
                if detect_program(c, "daed") is False:
                    print("daed will be installed")
                    install_dae_proxy(c)
                    self.db.dae_install()

        if task == "watchtower":
            if self.db.is_watchtower_installed() is False:
                if check_docker_ps_specific(c, "containrrr/watchtower") is False:
                    print("watchtower will be installed - the automatic updates of the docker container")
                    install_watch_tower(c)
                    self.db.watchtower_install()

        if task == "clash":
            if self.db.is_xclash_installed() is False:
                if check_docker_ps_specific(c, "dreamacro/clash") is False:
                    print("dreamacro.clash will be installed")
                    if self.install_xclash(1) is True:
                        self.db.docker_clash_install()
            else:
                if self.install_xclash_update() is True:
                    if self.install_xclash(2) is True:
                        print("xclash is updated.")

        if task.startswith("yacht"):
            port = task.replace("yacht", "")
            if port == "":
                port = "9055"
            if self.db.is_docker_yacht_installed() is False:
                install_container_management_utility(c, int(port))
                self.db.docker_yacht_install()

    def install_xclash(self, install_times: int) -> bool:
        # if check_docker_ps_specific(c, "dreamacro/clash") is False:...

        return False

    def install_xclash_update(self) -> bool:
        return False
