import os

from machineroom import taskbase as tb, __version__
from machineroom.tunnels.conn import *

try:
    import SQLiteAsJSON
except:
    os.system('python3.11 -m pip install SQLiteAsJSON')
    import SQLiteAsJSON

from machineroom import *

execute_path = os.path.dirname(__file__)


class ServerDoorJob(tb.DeploymentBotFoundation):
    def __init__(self, x):
        super().__init__(x)
        self.db = ServerRoom()

    def __run_connect(self, callback_x=None):
        k = self.start_server_from
        if self.srv.serv_count < k:
            print("cannot start from out of range server number")
            return
        if self.run_tunnel_detection():
            self.srv.use_next_node()
            k += 1

        while k < self.srv.serv_count:
            self.db.set_server_id(self.srv.current_id)
            self.stage_0()
            c = self._est_connection()
            try:
                self.stage_1(c)
                if callable(callback_x):
                    callback_x(c)
            except (tb.pexpect.TIMEOUT, tb.pexpect.EOF):
                print("maybe a time out")
            except ConnectionResetError as e:
                self.connection_err(e, True)
            except Exception as e:
                self.connection_err(e, False)
            self.srv.use_next_node()
            k += 1
        self.run_tunnel_detection_off()

    def __run_offline(self, call_job=None):
        k = self.start_server_from
        if self.srv.serv_count < k:
            print("cannot start from out of range server number")
            return
        while k < self.srv.serv_count:
            self.db.set_server_id(self.srv.current_id)
            self.stage_0()
            try:
                if callable(call_job):
                    call_job(self.srv.current_id)
            except Exception as e:
                self.connection_err(e, False)
            self.srv.use_next_node()
            k += 1

    def action_import(self):
        self.__run_connect()

    def action_retire(self):
        self.__run_offline(self._retire_on_each_server)

    def action_off_cert(self):
        self.__run_offline(self._action_off_cert)

    def _retire_on_each_server(self):
        self.db.update_res_kv("retired", True)

    def _action_off_cert(self):
        self.db.delete_res_kv("identity_cert_installed")

    def action_add_custom_cert(self, name, pubkey_path):
        def add_certification(x):
            if tb.detect_cert_signature(x, name) is False:
                tb.copy_id(x, pubkey_path)
                self.db.update_res_kv(f"custom_cert_{name}", True)

        self.__run_connect(add_certification)


def internal_work():
    """
    This is the cmd console use functions
    alpha stage now.
    """
    (a, b, c) = use_args()
    local = ServerRoom()
    if a == "ls":
        print("Here is my machine room...")
        gh = local.show_all_serv()
        for (id, host, res) in gh:
            y = FieldConstruct()
            y.add_icon(f"{id}  -> {host}     ")
            if local.get_tunnel_profile() != "":
                y.add_icon(f"TUNNEL PROFILE: {local.get_tunnel_profile()}")
            y.add_icon("EXPIRED" if local.is_what_installed_full("retire", id) else "")
            y.add_icon("CERT" if local.is_what_installed_full("identity_cert_installed", id) else "")
            y.add_icon("DOCKER" if local.is_what_installed_full("docker_compose_installed", id) else "")
            y.add_icon("DEAD" if local.is_what_installed_full("daed_installed", id) else "")
            y.add_icon("YACHT" if local.is_what_installed_full("yacht_installed", id) else "")
            y.add_icon("PY" if local.is_what_installed_full("python3_installed", id) else "")
            print(y.output())
    elif a == "sc":
        print("This to scan out the running docker containers in the status of that server")


    elif a == "import":
        file = os.path.join(Config.DATAPATH_BASE, b)
        if os.path.exists(file) is False:
            print("Wrong path cannot open this file")
        job = ServerDoorJob(b)
        job.action_import()
    elif a == "v":
        print(f"version. {__version__}")
    elif a == "retire":
        file = os.path.join(Config.DATAPATH_BASE, b)
        if os.path.exists(file) is False:
            print("Wrong path cannot open this file")
        job = ServerDoorJob(b)
        job.action_retire()
    elif a == "off-cert":
        file = os.path.join(Config.DATAPATH_BASE, b)
        if os.path.exists(file) is False:
            print("Wrong path cannot open this file")
        job = ServerDoorJob(b)
        job.action_off_cert()
    elif a == "add-cert":
        file = os.path.join(Config.DATAPATH_BASE, b)
        if os.path.exists(file) is False:
            print("Wrong path cannot open this file")
        job = ServerDoorJob(b)
        job.action_add_custom_cert("BLK_LOCAL", "/Users/hesdx/.ssh/blsp1.pub")
    elif a != None:
        local.set_server_id(a)
        if local.has_this_server() is False:
            err_exit(f"there is no such server for ---> {a}")
        cert = "/Users/hesdx/.ssh/id_rsa" if local.is_cert_installed() else ""
        (h, u, p) = local.get_info()
        port_sentence = "" if p == 22 else f"-p {p} "
        home_path = local.get_home_path()
        home_path = f'"cd {home_path}; bash"' if home_path != "" else ''
        if local.get_tunnel_profile() != "":
            print("TUNNEL PROFILE: {local.get_tunnel_profile()}")
            use_macos_vpn_on(local.get_tunnel_profile())
        os.system(f'ssh {port_sentence}-i {cert} -t {u}@{h} {home_path}')
    else:
        err_exit("cannot serv no args")

# if __name__ == '__main__':
#    internal_work()
