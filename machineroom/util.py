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
from .const import *

CMD_LIST1 = ["ls", "show", "list", "tell"]
CMD_LIST2 = ["scan", "check", "validation", "valid"]


def use_args() -> Tuple[str, str]:
    opt1 = None
    opt2 = None
    cmd = "ls"

    if len(sys.argv) >= 2:
        opt1 = sys.argv[1]
        if len(sys.argv) >= 3:
            opt2 = sys.argv[2]

    if opt1 in CMD_LIST1:
        cmd = "ls"
    elif opt1 in CMD_LIST2:
        cmd = "sc"
    else:
        cmd = opt1

    return cmd, opt2


def err_exit(msg: str):
    print(msg)
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


class ServerAuthInfoErr(Exception):
    ...


class NodeCountIsNotInPlan(Exception):
    ...


class Servers:
    _meta_file: str
    current_id: str
    current_host: str
    current_user: str
    current_pass: str
    _srv_index: int
    _meta_file: int

    def __init__(self, file: str):
        self._meta_file = file
        self.serv_count = 20
        self._srv_index = 0

    @property
    def path_file(self) -> str:
        return os.path.join(Config.DATAPATH_BASE, self._meta_file)

    @property
    def at_server(self) -> int:
        return self._srv_index

    def detect_servers(self):
        self.serv_count = read_file_total_lines(self.path_file)
        self.read_serv_at(0)

    def read_serv_at(self, index: int) -> dict:
        n = index % self.serv_count
        line = read_file_at_line(self.path_file, n)
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

        self._srv_index = n
        tmp = {
            "id": line[0],
            "ip": line[1],
            "user": line[2],
            "pass": line[3]
        }
        self.current_id = line[0]
        self.current_host = line[1]
        self.current_user = line[2]
        self.current_pass = line[3]
        print(f"######## Now enter server ID#{n}: {line[0]} {line[1]}")
        return tmp

    def use_next_node(self) -> dict:
        self._srv_index = self._srv_index + 1
        return self.read_serv_at(self._srv_index)


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
        self._line_ += val
        self._line_ += ", "

    def output(self) -> str:
        return self._line_
