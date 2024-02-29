import os
try:
    import SQLiteAsJSON
except:
    os.system('python3.11 -m pip install SQLiteAsJSON')
    import SQLiteAsJSON

from machineroom import *

execute_path = os.path.dirname(__file__)


def internal_work():
    (a, b) = use_args()
    # print(execute_path)
    server = Servers("my_server_room.txt")
    local = ServerRoom()
    if a == "ls":
        print("Here is my machine room...")
        gh = local.show_all_serv()
        for (id, host, res) in gh:
            cert_ok = "YES" if local.is_what_installed_full("identity_cert_installed", id) else "NO"
            print(f'{id}  -> {host}     certificated [{cert_ok}]')

    elif a == "sc":
        ...
    elif a == "import":
        server = Servers(b)
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
