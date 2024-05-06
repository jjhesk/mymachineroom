import pexpect

from machineroom import taskbase as tb, __version__
from machineroom.tunnels.conn import *

try:
    import SQLiteAsJSON
except:
    os.system('python3.11 -m pip install SQLiteAsJSON')
    import SQLiteAsJSON

from machineroom import *

execute_path = os.path.dirname(__file__)


class Infra2(tb.DeploymentBotFoundation):
    target_server_index: int
    running_arr: list[int]

    def __init__(self, x):
        super().__init__(x)
        self.target_server_index = -1
        self.running_arr = []
        if self.run_tunnel_detection():
            self.srv.use_next_node()

    def serialize_checking(self):
        if self.target_server_index > -1:
            if self.srv.serv_count > self.target_server_index:
                self.running_arr = [self.target_server_index]
        else:
            self.running_arr = [n for n in range(self.srv.serv_count)]
            if self.start_server_from >= self.srv.serv_count:
                raise Exception("logic error, start should be smaller than serv_count")
            if self.start_server_from < 0:
                raise Exception("logic error, start should be bigger than zero")
            if self.stop_server_at >= self.srv.serv_count:
                raise Exception("logic error, stop should be smaller than serv_count")
            if self.stop_server_at < self.start_server_from:
                raise Exception("logic error, start should be smaller than stop")
            self.running_arr = self.running_arr[self.start_server_from:self.stop_server_at]
        if len(self.running_arr) == 0:
            raise Exception("logic error, no server to start")

    def run_conn_looper(self, callback_x=None):
        self.serialize_checking()
        for ser_i in self.running_arr:
            self.srv.read_serv_at(ser_i)
            self.stage_0()
            c = self._est_connection()
            try:
                self.stage_1(c)
                if callable(callback_x):
                    callback_x(c)
            except Exception as e:
                if self.handle_exceptions(e, False):
                    pass
                raise e
        self.run_tunnel_detection_off()


class Infra1(tb.DeploymentBotFoundation):
    server_name: str

    def __init__(self, x):
        super().__init__(x)
        self.server_name = x

    def match_prefix_or_subfix(self, what: str) -> bool:
        return what in self.server_name

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
            except Exception as e:
                if self.handle_exceptions(e, False):
                    pass
                raise e

            self.srv.use_next_node()
            k += 1
        self.run_tunnel_detection_off()

    def run_offline(self, call_job=None):
        k = self.start_server_from
        if self.srv.serv_count < k:
            print("cannot start from out of range server number")
            return
        while k < self.srv.serv_count:
            self.stage_0()
            try:
                if callable(call_job):
                    call_job(self.srv.current_id)
            except Exception as e:
                self.connection_err(e, False)
            self.srv.use_next_node()
            k += 1
