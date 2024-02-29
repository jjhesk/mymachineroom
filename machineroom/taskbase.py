from fabric import Connection, Result
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


# https://fabric-zh.readthedocs.io/_/downloads/zh-cn/latest/pdf/
def detect_cert(c: Connection) -> bool:
    print("detect certification")
    r = c.run("cat ~/.ssh/authorized_keys", warn=True)
    line = str(r.stdout.strip().replace("\n", ""))
    return True if Config.MY_KEY_FEATURE in line else False


def detect_ram(d: Connection) -> float:
    r = d.run("awk '/Mem:/ {print $2}' <(free -h)", warn=True, pty=True, hide=True)
    line = str(r.stdout.strip().replace("\n", "")).replace("Gi", "")
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


def install_python(c: Connection):
    program = '''
sudo apt-get install -y \
apt-transport-https \
ca-certificates \
curl \
software-properties-common \
python3'''
    c.run(program, warn=True)


def install_docker_ce(c: Connection):
    program = """
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
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
sudo systemctl enable docker
    """
    exec_shell_global(c, program)
    return True


def install_docker_compose(c: Connection):
    program = f"""
DOCKER_VER={Config.DOCKER_COMPOSE_VERSION}
sudo curl -L "https://github.com/docker/compose/releases/download/v$DOCKER_VER/docker-compose-$(uname -s)-$(uname -m)" -o /usr/bin/docker-compose
chmod +x /usr/bin/docker-compose"""
    exec_shell_global(c, program)


def run_context(c: Connection, block: str) -> Result:
    result = c.run(block, pty=False, echo=True)
    return result


def run_local_file(c: Connection, file_name: str) -> Result:
    script_file = open(file_name)
    result = c.run(script_file.read())

    script_file.close()
    return result


def exec_shell_global(c: Connection, program: str):
    return exec_shell_program(c, Config.HOME, program)


def exec_shell_program(c: Connection, remote_path: str, program: str) -> Result:
    buffer_file = BufferFile()
    buffer_file.new_bash()
    buffer_file.add_cmd(program)
    c.put(buffer_file.path, remote_path)
    return exec_shell(c, remote_path, buffer_file.execution_cmd)


def exec_shell_program_file(c: Connection, remote_path: str, program_file: BufferFile) -> Result:
    c.put(program_file.path, remote_path)
    return exec_shell(c, remote_path, program_file.execution_cmd)


def exec_shell(c: Connection, working_path: str, bash_file: str) -> Result:
    cmd = f'cd {working_path} && /usr/bin/bash {bash_file}'
    cmd2 = f'cd {working_path} && echo "" > {bash_file}'
    return c.run(cmd, pty=True, warn=True)


def exec_docker_compose(c: Connection, working_path: str, yml_file: str) -> Result:
    cmd1 = f'cd {working_path} && /usr/bin/docker-compose -f {yml_file} up -d'
    return c.run(cmd1, pty=True, timeout=100)


def exec_container_program(c: Connection, container_id: str, bash_line: str) -> Result:
    # cmd1 = f'cd {working_path} && docker exec {container_id} ckb miner'
    cmd2 = f'docker exec {container_id} {bash_line} &'
    return c.run(cmd2, pty=True, timeout=100, warn=True)


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
    program = f"""
docker volume create yacht
docker run -d -p {out_bound_listing_port}:8000 --restart unless-stopped -v /var/run/docker.sock:/var/run/docker.sock -v yacht:/config --name yacht selfhostedpro/yacht
"""
    exec_shell_global(c, program)
    print("[                       yacht is ready                      ]")
    print(f"{c.host}:{out_bound_listing_port} is ready for the web login")
