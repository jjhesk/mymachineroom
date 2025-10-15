import os
import random

from machineroom import taskbase as tb, __version__, ServerRoom, use_args, FieldConstruct, err_exit
from machineroom.infra import Infra1
from machineroom.tunnels.conn import *
from fabric import Connection
from tabulate import tabulate

try:
    import SQLiteAsJSON
except:
    os.system('python3.11 -m pip install SQLiteAsJSON')
    import SQLiteAsJSON

execute_path = os.path.dirname(__file__)


class ServerDoorJob(Infra1):

    def action_import(self):
        self.run_conn()

    def action_retire(self):
        self.run_offline(self._retire_on_each_server)

    def action_off_cert(self):
        self.run_offline(self._action_off_cert)

    def _retire_on_each_server(self):
        self.srv.local().update_res_kv("retired", True)

    def _action_off_cert(self):
        self.srv.local().delete_res_kv("identity_cert_installed")

    def action_scan_ports(self):
        self.run_conn(self._from_c_ports)

    def _from_c_ports(self, c: Connection):
        m = tb.list_all_open_ports(c)
        self.srv.local().update_res_kv("ports", m)
        any_one = random.choice(m)

    def action_add_custom_cert(self, name, pubkey_path):
        """Add a custom certificate to servers and store the path."""
        def certification(c: Connection):
            if tb.detect_cert_signature(c, name) is False:
                tb.copy_id(c, pubkey_path)
                # Store custom cert metadata
                self.srv.local().update_res_kv(f"custom_cert_{name}", True)
                # Store the private key path (convert .pub to private key)
                private_key_path = self._resolve_private_key_path(pubkey_path)
                self.srv.local().set_local_cert_path(private_key_path)
        
        self.run_conn(certification)

    def _resolve_private_key_path(self, pubkey_path: str) -> str:
        """
        Convert public key path to private key path.
        
        Args:
            pubkey_path: Path to public key (.pub file)
        
        Returns:
            str: Path to corresponding private key
        """
        return pubkey_path.replace(".pub", "")

    def action_remove_custom_cert(self, name):
        def certification(c: Connection):
            if tb.detect_cert_signature(c, name) is False:
                self.srv.local().delete_res_kv(f"custom_cert_{name}")

        self.run_conn(certification)


def internal_work():
    """
    This is the cmd console use functions
    alpha stage now.


            y = FieldConstruct()
            y.add_icon(f"{id}  -> {host}     ")
            tun = local.get_tunnel_profile()
            if tun != "":
                y.add_icon(f"TUNNEL PROFILE: {tun}")
            y.add_icon("EXPIRED" if local.is_what_installed_full("retire", id) else "")
            y.add_icon("CERT" if local.is_what_installed_full("identity_cert_installed", id) else "")
            y.add_icon("DOCKER" if local.is_what_installed_full("docker_compose_installed", id) else "")
            y.add_icon("DAED" if local.is_what_installed_full("daed_installed", id) else "")
            y.add_icon("YACHT" if local.is_what_installed_full("yacht_installed", id) else "")
            y.add_icon("PY" if local.is_what_installed_full("python3_installed", id) else "")

    """
    (a, b, c) = use_args()
    local = ServerRoom()
    if a == "ls":
        gh = local.show_all_serv()
        table_content = []
        for (id, host, res) in gh:
            local.set_server_id(id)
            content = []
            content.append(id)
            content.append(host)
            tun = local.get_tunnel_profile()
            if tun != "":
                content.append(f"TUNNEL PROFILE: {tun}")

            content.append("EXPIRED" if local.is_what_installed_full("retire", id) else "")
            content.append("CERT" if local.is_what_installed_full("identity_cert_installed", id) else "")
            content.append("DOCKER" if local.is_what_installed_full("docker_compose_installed", id) else "")
            content.append("DAED" if local.is_what_installed_full("daed_installed", id) else "")
            content.append("YACHT" if local.is_what_installed_full("yacht_installed", id) else "")
            content.append("PY" if local.is_what_installed_full("python3_installed", id) else "")

            table_content.append(content)

        print(tabulate(table_content))
    elif a == "docker-scan":
        print("This to scan out the running docker containers in the status of that server")
    elif a == "scanports":
        print("This to scan out the running docker containers in the status of that server")
    elif a == "import":
        if b == "":
            err_exit("need to have one more arg")
        file = os.path.join(Config.DATAPATH_BASE, b)
        if os.path.exists(file) is False:
            err_exit("Wrong path cannot open this file" + file)
        job = ServerDoorJob(b)
        job.action_import()
    elif a == "v":
        print(f"version. {__version__}")

    elif a == "watch-profile":
        if b == "":
            err_exit("need to have one more arg")
        file = os.path.join(Config.DATAPATH_BASE, b)
        if os.path.exists(file) is False:
            err_exit("Wrong path cannot open this file" + file)
        job = ServerDoorJob(b)
        job.action_scan_ports()

    elif a == "set-home":
        if b == "":
            err_exit("need to have one more arg for the server ID")
        if c == "":
            err_exit("need to have one more arg for the the remote start path, for example /home")
        local.set_server_id(b)
        if local.has_this_server() is False:
            err_exit(f"there is no such server for ---> {b}")
            local.update_res_kv("home_path", c)

    elif a == "retire":
        if b == "":
            err_exit("need to have one more arg")
        file = os.path.join(Config.DATAPATH_BASE, b)
        if os.path.exists(file) is False:
            err_exit("Wrong path cannot open this file" + file)
        job = ServerDoorJob(b)
        job.action_retire()
    elif a == "off-cert":
        if b == "":
            err_exit("need to have one more arg")
        file = os.path.join(Config.DATAPATH_BASE, b)
        if os.path.exists(file) is False:
            err_exit("Wrong path cannot open this file" + file)
        job = ServerDoorJob(b)
        job.action_off_cert()
    elif a == "add-cert":
        print("You are about to adding custom certificate to all servers on behalf this machine room.")
        if b == "":
            err_exit("need to have one more arg")
        file = os.path.join(Config.DATAPATH_BASE, b)
        if os.path.exists(file) is False:
            err_exit("Wrong path cannot open this file" + file)
        job = ServerDoorJob(b)
        key_path = input(
            "Enter the path of the pub file. For example /Users/{user_name_here}/.ssh/{user_custom_public_key}.pub")
        cert_name = input(
            "Enter the name of the pub file. open the .pub file and usually its located at the very last word of the key file.")

        job.action_add_custom_cert(cert_name, key_path)
    elif a == "remove-custom-cert":
        if b == "":
            err_exit("need to have one more arg")
        file = os.path.join(Config.DATAPATH_BASE, b)
        if os.path.exists(file) is False:
            err_exit("Wrong path cannot open this file" + file)
        job = ServerDoorJob(b)
        cert_name = input(
            "Enter the name of the pub file. open the .pub file and usually its located at the very last word of the key file.")
        job.action_remove_custom_cert(cert_name)
    elif a != None:
        local.set_server_id(a)
        if local.has_this_server() is False:
            err_exit(f"there is no such server for ---> {a}")
        cert_info = local.get_cert_info()
        cert = cert_info['path'] if cert_info['installed'] else ""
        (h, u, p) = local.get_info()
        port_sentence = "" if p == 22 else f"-p {p} "
        home_path = local.get_res_kv("home_path")
        home_path = f'"cd {home_path}; bash"' if home_path != "" else ""
        if local.get_tunnel_profile() != "":
            print("TUNNEL PROFILE: {local.get_tunnel_profile()}")
            use_macos_vpn_on(local.get_tunnel_profile())
        
        # Use custom SSH key if available, otherwise use default behavior
        ssh_key_option = f"-i {cert}" if cert else ""
        os.system(f'ssh {port_sentence}{ssh_key_option} -t {u}@{h} {home_path}')
    else:
        err_exit("cannot serv no args")

# if __name__ == '__main__':
#    internal_work()
