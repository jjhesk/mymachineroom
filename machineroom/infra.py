from machineroom import taskbase as tb, __version__
from machineroom.tunnels.conn import *

try:
    import SQLiteAsJSON
except:
    os.system('python3.11 -m pip install SQLiteAsJSON')
    import SQLiteAsJSON

from machineroom import *

execute_path = os.path.dirname(__file__)


class Infra1(tb.DeploymentBotFoundation):
    def __init__(self, x):
        super().__init__(x)

    def run_conn(self, callback_x=None):
        k = self.start_server_from
        if self.srv.serv_count < k:
            print("cannot start from out of range server number")
            return
        if self.run_tunnel_detection():
            self.srv.use_next_node()
            k += 1

        while k < self.srv.serv_count:
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

    def run_offline(self, call_job=None):
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
