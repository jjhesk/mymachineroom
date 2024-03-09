import os

from machineroom.taskbase import *

try:
    import SQLiteAsJSON
except:
    os.system('python3.11 -m pip install SQLiteAsJSON')
    import SQLiteAsJSON

from machineroom import *

execute_path = os.path.dirname(__file__)


class Import(DeploymentBotFoundation):
    def __init__(self, x):
        super().__init__(x)
        self.db = ServerRoom()
        k = 0
        while k < self.srv.serv_count:
            self.db.set_server_id(self.srv.current_id)
            c = self._est_connection()
            try:
                self.stage_1(c)
            except (pexpect.TIMEOUT, pexpect.EOF):
                print("maybe a time out")
            except ConnectionResetError as e:
                self.connection_err(e, True)
            except Exception as e:
                self.connection_err(e, False)
            self.srv.use_next_node()
            k += 1


def internal_work():
    """
    This is the cmd console use functions
    alpha stage now.
    """
    (a, b) = use_args()
    local = ServerRoom()
    if a == "ls":
        print("Here is my machine room...")
        gh = local.show_all_serv()
        for (id, host, res) in gh:
            cert_ok = "YES" if local.is_what_installed_full("identity_cert_installed", id) else "NO"
            print(f'{id}  -> {host}     certificated [{cert_ok}]')

    elif a == "sc":
        print("This function is will be soon available to you.")
    elif a == "import":
        file = os.path.join(Config.DATAPATH_BASE, b)
        if os.path.exists(file) is False:
            print("Wrong path cannot open this file")
        Import(b)
    elif a != None:
        local.set_server_id(a)
        if local.has_this_server() is False:
            err_exit(f"there is no such server for ---> {a}")
        cert = "/Users/hesdx/.ssh/id_rsa" if local.is_cert_installed() else ""
        (h, u, p) = local.get_info()
        port_sentence = "" if p == 22 else f"-p {p} "
        home_path = local.get_home_path()
        home_path = f'"cd {home_path}; bash"' if home_path != "" else ''
        os.system(f'ssh {port_sentence}-i {cert} -t {u}@{h} {home_path}')
    else:
        err_exit("cannot serv no args")

# if __name__ == '__main__':
#    internal_work()
