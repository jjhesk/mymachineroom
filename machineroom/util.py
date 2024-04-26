# !/usr/bin/env python
# coding: utf-8
import re
import sys
from fabric import Connection
from subprocess import Popen, PIPE
import json
import os.path
from typing import Union, Tuple, TextIO

from invoke import StreamWatcher
from machineroom.sql import ServerRoom

from .const import *
from .errs import *


def function_command_alias(input: str, actual: str, command_alias: list):
    if input in command_alias:
        return True, actual
    return False, None


def check_for_bad_ids(id_name: str):
    all_bad = CMD_SCAN_DOCKER + CMD_IMPORT + CMD_SCAN_PORT + CMD_LIST + CMD_VERSION + CMD_RETIRE + CMD_OFF_CERT + CMD_ADD_CERT + CMD_GENERATE_PROFILE +CMD_SET_BASH_START
    if id_name in all_bad:
        raise BadIDs()


def use_args() -> Tuple[str, str, str]:
    opt1 = ""
    opt2 = ""
    opt3 = ""
    cmd = "ls"

    if len(sys.argv) >= 2:
        opt1 = sys.argv[1]
        if len(sys.argv) >= 3:
            opt2 = sys.argv[2]
            if len(sys.argv) >= 4:
                opt3 = sys.argv[3]

    cmd = opt1
    f, c = function_command_alias(opt1, "ls", CMD_LIST)
    if f is True:
        cmd = c
    f, c = function_command_alias(opt1, "docker-scan", CMD_SCAN_DOCKER)
    if f is True:
        cmd = c
    f, c = function_command_alias(opt1, "import", CMD_IMPORT)
    if f is True:
        cmd = c
    f, c = function_command_alias(opt1, "v", CMD_VERSION)
    if f is True:
        cmd = c
    f, c = function_command_alias(opt1, "retire", CMD_RETIRE)
    if f is True:
        cmd = c
    f, c = function_command_alias(opt1, "off-cert", CMD_OFF_CERT)
    if f is True:
        cmd = c
    f, c = function_command_alias(opt1, "add-cert", CMD_ADD_CERT)
    if f is True:
        cmd = c
    f, c = function_command_alias(opt1, "watch-profile", CMD_GENERATE_PROFILE)
    if f is True:
        cmd = c
    f, c = function_command_alias(opt1, "set-home", CMD_SET_BASH_START)
    if f is True:
        cmd = c

    return cmd, opt2, opt3


def err_exit(msg):
    if isinstance(msg, str):
        print(msg)
    if isinstance(msg, MachineRoomErr):
        print(str(msg))
    exit(0)


def read_file_at_line(full_path: str, line: int) -> str:
    content_line = ""
    with open(full_path, 'r') as fp:
        for count, content in enumerate(fp):
            if count == line:
                content_line = content.strip().replace("\n", "")
        fp.close()
    return content_line


def read_file_total_lines(full_path: str) -> int:
    print(f"count lines from {full_path}")
    with open(full_path, 'r') as fp:
        for count, line in enumerate(fp):
            pass
        fp.close()
    print('Total Lines', count + 1)
    return count + 1


def read_content(full_path: str) -> str:
    content = ""
    with open(full_path, 'r') as fp:
        content = fp.read()
        fp.close()
    return content


def extract_address_arg(full_path: str, head_line_json: str) -> str:
    payload_x = ""
    with open(full_path, 'r') as fp:
        dumps = fp.readlines()
        fp.close()
        for line in dumps:
            line = line.strip()
            if head_line_json in line:
                starting_index = line.find(head_line_json) + len(head_line_json)
                ending_index = len(line)
                payload_x = line[starting_index:ending_index]
                break
    return payload_x.strip().replace("\n", "")


def add_line_if_line_not_exist(full_path: str, hint_line: str, content_insert: str):
    if find_text(hint_line, full_path) is False:
        with open(full_path, 'r') as rf:
            temp = rf.readlines()
            rf.close()
            temp.append(content_insert)
            contents = "".join(temp)
        _save_str(full_path, contents)


def edit_file_context(full_path: str, fine_line: str, content_insert: str):
    with open(full_path, 'r') as rf:
        temp = rf.readlines()
        u = 0
        for line in temp:
            if fine_line in line:
                print("found and write!")
                temp[u] = content_insert
                break
            u += 1
        contents = "".join(temp)

    _save_str(full_path, contents)


def extract_block_from_line(head_line_json: str, endline_str: str, temp_file: str = Config.TEMP_FILE,
                            isJson: bool = True) -> \
        Union[dict, str, int]:
    path = os.path.join(Config.DATAPATH_BASE, temp_file)
    payload_x = {}
    with open(path, 'r') as fp:
        # read all lines using readline()
        dumps = fp.readlines()
        for line in dumps:
            if head_line_json in line:
                starting_index = line.find(head_line_json) + len(head_line_json)
                ending_index = line.find(endline_str) - 1
                payload_x = line[starting_index:ending_index]
        fp.close()

    if isJson is True:
        payload_x = json.loads(payload_x)

    return payload_x


def extract_by_regx(regex, temp_file: str = Config.TEMP_FILE) -> list:
    path = os.path.join(Config.DATAPATH_BASE, temp_file)
    payload_x = []
    with open(path, 'r') as fp:
        dat = fp.read()
        matches = re.finditer(regex, dat, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            the_number = match.group(1)
            # print(the_number)
            payload_x.append(the_number)
        fp.close()
    return payload_x


def capture_js_block(start_cap_line: str, end_cap_line: str, offset_back_line: int = 1,
                     additional_line_js: str = "", blocks_handler=None) -> dict:
    path = os.path.join(Config.DATAPATH_BASE, Config.TEMP_FILE)
    line_bank = []
    nb = 0
    start = 0
    end = 0

    with open(path, 'r') as fp:
        # read all lines using readline()
        dumps = fp.readlines()
        for line in dumps:
            if start_cap_line in line:
                start = nb
            if end_cap_line in line:
                end = nb

            if start > 0 and end == 0:
                line_bank.append(line)

            if end > 0:
                break
            nb += 1
        fp.close()
    path_tmp = os.path.join(Config.DATAPATH_BASE, Config.TEMP_JS)
    if blocks_handler is None:
        line_bank = line_bank[:len(line_bank) - offset_back_line]
        line_bank.append(additional_line_js)
    else:
        # for additional customization
        line_bank = blocks_handler(line_bank, len(line_bank), offset_back_line, additional_line_js)

    my_str_as_bytes = str.encode("".join(line_bank))
    _save_bytes(my_str_as_bytes, path_tmp)
    return evaluate_javascript(path_tmp)


def evaluate_javascript(path: str):
    """Evaluate and stringify a javascript expression in node.js, and convert the
    resulting JSON to a Python object"""
    node = Popen(['node', path], stdin=PIPE, stdout=PIPE)
    # stdout, _ = node.communicate(f'console.log(JSON.stringify({s}))'.encode('utf8'))
    stdout, _ = node.communicate()
    filter1 = stdout.decode('utf8')
    filter1 = filter1.replace("\n", "")
    # filter1 = filter1.replace("None", "")
    # filter1 = filter1.replace("[Array]", "[]")
    # filter1 = filter1.replace("[Object]", "{}")
    # return fd
    # my_str_as_bytes = str.encode(filter1)
    # self._save_bytes(my_str_as_bytes, path)
    return json.loads(filter1)


def _save_bytes(file_name: str, content: bytes):
    """
    save the bytes info into the file
    :param content:
    :param file_name:
    :return:
    """
    file_object = None
    try:
        file_object = open(file_name, 'wb')
        file_object.truncate(0)
    except FileNotFoundError:
        file_object = open(file_name, 'ab+')
    finally:
        # file_object.buffer.write(content)
        file_object.write(content)
        file_object.close()


def _save_str(file_name: str, content: str):
    """
    save the bytes info into the file
    :param content:
    :param file_name:
    :return:
    """
    file_object = None
    try:
        file_object = open(file_name, 'w')
        file_object.write(content)
    except FileNotFoundError:
        file_object = open(file_name, 'a+')
        file_object.write(content)


def extract_from_block(head_line_json: str, endline_str: str, isJson: bool = True) -> Union[dict, str, int]:
    path = os.path.join(Config.DATAPATH_BASE, Config.TEMP_FILE)
    payload_x = {}
    with open(path, 'r') as fp:
        # read all lines using readline()
        dumps = fp.readlines()
        for line in dumps:
            if head_line_json in line:
                starting_index = line.find(head_line_json) + len(head_line_json)
                ending_index = line.find(endline_str) - 1
                payload_x = line[starting_index:ending_index]
        fp.close()

    if isJson is True:
        payload_x = json.loads(payload_x)

    return payload_x


def extraction(head_line_json: str, bug: bool = False, showinJson: bool = True):
    payload_x = ""
    path = os.path.join(Config.DATAPATH_BASE, Config.TEMP_FILE)
    with open(path, 'r') as fp:
        # read all lines using readline()
        dumps = fp.readlines()
        for line in dumps:
            if head_line_json in line:
                line = line.strip()
                prematerial = line.replace(head_line_json, "").strip()
                if showinJson is False:
                    payload_x = prematerial[:-1] if bug is False else prematerial
                else:
                    if bug is True:
                        payload_x = json.loads(prematerial)
                    else:
                        payload_x = json.loads(prematerial[:-1])

        fp.close()

    return payload_x


def find_text(search_keyword: str, temp_file: str):
    # path = os.path.join(DATAPATH_BASE, temp_file)
    with open(temp_file, 'r') as g:
        duline = g.readlines()
        for line in duline:
            if search_keyword in line:
                return True
        g.close()

    return False


def store_txt(file_put: str, content: str):
    path_tmp = os.path.join(Config.DATAPATH_BASE, file_put)
    my_str_as_bytes = str.encode(content)
    _save_bytes(my_str_as_bytes, path_tmp)


class BufferFile:
    _file: str

    def __init__(self):
        self._file = "tmp_remote_execution.sh"

    def defaultName(self):
        self._file = "tmp_remote_execution.sh"
        self._check_file()

    def setName(self, file_name: str):
        self._file = file_name
        self._check_file()
        return self

    @property
    def path(self):
        return os.path.join(Config.DATAPATH_BASE, self._file)

    @property
    def execution_cmd(self) -> str:
        return self._file
        #  return f"sh {self._file}"

    def _check_file(self):
        with open(self.path, "w") as f_io:
            f_io.write("")
            f_io.close()

    def open_file_io_buffer(self, method: str = "ab"):
        return open(self.path, method)

    def new_bash(self):
        self.clear()
        self.add_cmd("#!/bin/bash")
        # self.add_cmd("source ~/.profile")

    def clear(self):
        self._check_file()

    def write_content(self, block: str):
        with open(self.path, "w") as f_io:
            f_io.write(block)
            f_io.close()

    def write_content_b(self, block: bytes):
        with open(self.path, "wb") as f_io:
            f_io.write(block)
            f_io.close()

    def add_cmd(self, line: str, at_line: int = -1):
        line = line + "\n"
        with open(self.path, "a") as f_io:
            if at_line == -1:
                f_io.write(line)
            else:
                f_io.seek(at_line, os.SEEK_END)
                f_io.write(line)
            f_io.close()

    def this_file_filter(self, items: list):
        text_pl = ""
        with open(self.path, "r") as f_io:
            text_pl = f_io.read()
            f_io.close()
        for symbol in items:
            text_pl = text_pl.replace(symbol, "")
        self.write_content(text_pl)

    def remove_color(self):
        with open(self.path, "r") as f_io:
            text_pl = f_io.read()
            f_io.close()
            regex = re.compile(r"\[38;2(;\d{,3}){3}m")
            text_pl = regex.sub("", text_pl)
            self.write_content(text_pl)

    def save_as(self, file_name: str):
        base_database = os.path.join(Config.DATAPATH_BASE, file_name)
        content = ""
        with open(self.path, "r") as f_io:
            content = f_io.read()
            f_io.close()

        with open(base_database, "w+") as f_io:
            f_io.write(content)
            f_io.close()

        print("save as done.")


class Servers:
    _meta_file: str
    current_id: str
    current_host: str
    current_user: str
    current_pass: str
    current_srv_port:int
    _srv_index: int
    _meta_file: int
    _tunnel_type: TunnelType
    profile_name: str
    _on_detect: bool
    _local_db: ServerRoom

    def __init__(self, file: str):
        self._meta_file = file
        self.serv_count = 20
        self._tunnel_type = TunnelType.NO_TUNNEL
        self.profile_name = ""
        self._srv_index = 0
        self._on_detect = True
        self._local_db = ServerRoom()

    @property
    def path_file(self) -> str:
        return os.path.join(Config.DATAPATH_BASE, self._meta_file)

    def has_this_server(self):
        return self._local_db.has_this_server()

    def is_cert_installed(self):
        return self._local_db.is_cert_installed()

    def cert_install(self):
        return self._local_db.cert_install()

    def local(self):
        return self._local_db

    @property
    def at_server(self) -> int:
        return self._srv_index

    @property
    def tunnel_type(self) -> TunnelType:
        return self._tunnel_type

    def detect_servers(self):
        self.serv_count = read_file_total_lines(self.path_file)
        try:
            self.read_serv_at(0)
            self._on_detect = False
        except FoundVPNTunnel:
            ...

    def read_serv_at(self, index: int):
        n = index % self.serv_count
        line = read_file_at_line(self.path_file, n)
        line = reader_split_recognition(line)
        configuration = reader_profile_0(line)
        self._srv_index = n
        ID = configuration.get("id")
        IP = configuration.get("host")

        if index == 0 and "#" in configuration.get("id"):
            TUNNEL_TYPE = IP
            print(f"Detected tunnel for machine group {ID} using {TUNNEL_TYPE}")
            self._tunnel_type = TunnelType.Recongize(TUNNEL_TYPE)
            self.profile_name = line[0].replace("#", "")
            raise FoundVPNTunnel()

        self.current_id = ID
        self.current_host = IP
        self.current_user = configuration.get("user")
        self.current_pass = configuration.get("pass")
        self.current_srv_port = configuration.get("port")
        self._local_db.set_server_id(ID)
        if self._on_detect is False:
            print(f"## ☎️ Now enter network ID#{n}: {ID} {IP}")
        if self.has_tunnel():
            self._local_db.entrance_L2(self.profile_name, configuration)
        else:
            self._local_db.entrance_L1(configuration)

    def has_tunnel(self) -> bool:
        return self._tunnel_type != TunnelType.NO_TUNNEL

    def use_next_node(self, x: int = 1):
        self._srv_index = self._srv_index + x
        check_for_bad_ids(self.current_id)
        self.read_serv_at(self._srv_index)


def reader_split_recognition(line: str) -> list:
    if "----" in line:
        line = line.split("----")
    elif "---" in line:
        line = line.split("---")
    elif "--" in line:
        line = line.split("--")
    elif "————" in line:
        line = line.split("————")
    elif "——" in line:
        line = line.split("——")
    if isinstance(line, str):
        raise ServerAuthInfoErr()

    return line


def reader_profile_0(line: list) -> dict:
    profile = {
        "id": line[0],
        "host": line[1],
        "user": line[2],
        "pass": line[3],
        "port": 22
    }

    try:
        port = line[4]
        profile.update({
            "port": port
        })
    except KeyError:
        ...

    return profile


class InfrastructurePlannerFoundation:
    # total running nodes on this KVM
    nodes: int
    # the total steps is always 1+
    iterate_steps: int
    # the remote workspace
    LOCAL_WORKSPACE: str
    connector: Connection
    tmp_text_io: TextIO
    tmp_file_man: BufferFile

    def set_nodes(self, amount_nodes: int):
        self.nodes = amount_nodes
        self.iterate_steps = amount_nodes + 1
        return self


class DummyWatcher(StreamWatcher):
    def submit(self, stream):
        # print(f'Output: "{stream}"')
        return []


class FieldConstruct:
    def __init__(self):
        self._line_ = ""

    def add_line(self, line: str):
        self._line_ += line
        self._line_ += "\n"

    def normal_field(self, key: str, val: str):
        self._line_ += key
        self._line_ += ": "
        self._line_ += val
        self._line_ += "\n"

    def add_block(self, key: str, val: str):
        self._line_ += key
        self._line_ += ": "
        self._line_ += "\n"
        self._line_ += val
        self._line_ += "\n"

    def normal_field_table(self, key: str, val: str):
        self._line_ += key
        self._line_ += ": "
        self._line_ += val
        self._line_ += "\n"

    def add_icon(self, val: str):
        if val == "":
            return
        self._line_ += val
        self._line_ += ", "

    def output(self) -> str:
        return self._line_
