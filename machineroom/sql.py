# !/usr/bin/env python
# coding: utf-8
import datetime
import sqlite3
from typing import Tuple

from SQLiteAsJSON import ManageDB
from SQLiteAsJSON.SQLiteAsJSON import db_logger
import os.path
import json
from requests import Response

from machineroom.const import Config


class SqlDataNotFound(Exception):
    pass


def obj_to_tuple(obj) -> dict:
    """ Parse JSON object and format it for insert_data method

    Parameters:
        obj (dict): The JSON object that should be formatted

    Returns:
        dict: JSON object with keys and values formatted for insert_data method """

    keys = ''
    values = ''
    for key, value in obj.items():
        keys = f'{keys},{key}' if keys != '' else key
        values = f'{values}, :{key}' if values != '' else f':{key}'

    return {"keys": keys, "values": values}


def obj_to_string(update_config) -> str:
    update_string = ''
    index = 0
    for key, value in update_config.items():
        update_string = update_string + f"{key}='{value}'," if index < len(
            update_config) - 1 else update_string + f"{key}='{value}'"
        index = index + 1

    return update_string


class CompanyUserBase(ManageDB):
    """
    modified blockchain db controller
    """

    def found_table(self, tableName: str) -> bool:
        sqlStatement = f"SELECT name FROM sqlite_sequence WHERE type='table' AND name='{tableName}'"
        cursor = self.conn.cursor()
        cursor.execute(sqlStatement)
        db_result = cursor.fetchone()
        if db_result is None:
            return False
        else:
            return True

    def has_id_in_tbl(self, tbl: str, row_id: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {tbl} WHERE id = ?", (row_id,))
        db_result = cursor.fetchone()
        cursor.close()
        if db_result is None:
            return False
        else:
            return True

    def has_row(self, tbl: str, member_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {tbl} WHERE id = ?", (member_id,))
        db_result = cursor.fetchone()
        cursor.close()
        if db_result is None:
            return False
        else:
            return True

    def update_by_id(self, tbl: str, server_id: str, params: dict) -> bool:
        if self.has_id_in_tbl(tbl, server_id) is False:
            return False
        try:
            columns = obj_to_string(params)
            # update query
            self.conn.execute(f"UPDATE {tbl} set {columns} where id='{server_id}'")
        except Exception as E:
            db_logger.error('Data Update Error : ', E)
            return False

        self.conn.commit()
        return True

    def insert_row_dat(self, tbl: str, params: dict) -> bool:
        # Create UUID
        # params["member_id"] = uuid.uuid4().hex
        # params["timestamp"] = round(time.time() * 1000)  # Current unix time in milliseconds
        columns = obj_to_tuple(params)
        # insert query
        try:
            query = (
                f'INSERT INTO {tbl} ({columns["keys"]}) VALUES ({columns["values"]})'
            )
            self.conn.execute(query, params)
            self.conn.commit()
        except (
                sqlite3.OperationalError,
                Exception
        ) as e:
            db_logger.error('Data Insert Error : ', e)
            return False
        return True

    def insert_row_t2(self, tbl: str, params: dict) -> bool:
        columns = obj_to_tuple(params)
        try:
            query = (
                f'INSERT INTO {tbl} ({columns["keys"]}) VALUES ({columns["values"]})'
            )
            self.conn.execute(query, params)
            self.conn.commit()
        except (
                sqlite3.OperationalError,
                Exception
        ) as e:
            db_logger.error('Data Insert Error : ', e)
            return False
        return True

    def get_member_res(self, tbl: str, server_id: str) -> dict:
        cursor = self.conn.cursor()
        _da = {}
        try:
            cursor.execute(f'SELECT res FROM {tbl} WHERE id = ?',
                           (server_id,))
            (res_01,) = cursor.fetchone()
            _da = json.loads(res_01)
        except json.JSONDecodeError as e:
            db_logger.error(e)
        except Exception as E:
            db_logger.error('Data Insert Error : ', E)
        return _da

    def get_host_info(self, tbl: str, server_id: str) -> Tuple[str, str, int]:
        cursor = self.conn.cursor()
        try:
            cursor.execute(f'SELECT host, user, port FROM {tbl} WHERE id = ?',
                           (server_id,))
            (host, user, port) = cursor.fetchone()
            return host, user, port
        except json.JSONDecodeError as ef:
            db_logger.error(ef)
        except Exception as E:
            db_logger.error('Data Insert Error : ', E)
        return ("", "", -1)

    def show_all_servers(self, tbl: str) -> list:
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT id, host, res FROM {tbl}")
        data = cursor.fetchall()
        cursor.close()
        return data

    def get_next_action(self, tbl: str, server_id: str) -> dict:
        cursor = self.conn.cursor()
        _da = {}
        next_action = None
        try:
            cursor.execute(f'SELECT id, next_action FROM {tbl} WHERE id = ?',
                           (server_id,))
            (tx_id, next_action) = cursor.fetchone()
        except Exception as E:
            db_logger.error('Data Insert Error : ', E)
        _da = json.loads(next_action)
        return _da

    def _is_what_ready_res(self, tble_member: str, address: str, key: str) -> bool:
        current_time = datetime.datetime.now().timestamp()
        current_time = int(current_time)
        from_dat = self.get_next_action(tble_member, address)
        if key in from_dat:
            time_next = from_dat[key]
            return current_time > time_next

        print(f"key {key} not exist. decision is OK.")
        return True

    def _check_point_update_res(self, tble_member: str, address: str, key: str, next_seconds: int = 3600):
        from_dat = self.get_next_action(tble_member, address)
        current_time = datetime.datetime.now().timestamp()
        current_time = int(current_time)
        from_dat.update({
            key: current_time + next_seconds
        })
        self.update_by_id(tble_member, address, {
            "next_action": json.dumps(from_dat)
        })

    def keepcopy(self, file_path: str, r: Response):
        try:
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        except FileNotFoundError:
            with open(file_path, 'a+') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)


this_folder_path = os.path.dirname(__file__)


class ServerRoom(CompanyUserBase):
    def __init__(self):
        self._tblembr = "server_room"
        path_db = os.path.join(Config.DATAPATH_BASE, 'cache.db')
        # redirect the schema path to this module package.
        schema = os.path.join(this_folder_path, 'schema.json')
        self.cache_db_path = path_db
        new_db = False if os.path.isfile(path_db) else True
        try:
            super().__init__(
                db_name=path_db,
                db_config_file_path=schema,
                same_thread=False
            )
            if new_db:
                self.create_table()
            self.server_id = ""
        except sqlite3.OperationalError as eh:
            print("--err0--")
            print(path_db)
            print(schema)
            print(eh)

    def check_df_ready(self) -> bool:
        return self._is_what_ready("df_management")

    def check_df_visit(self):
        self._check_point_update("df_management")

    def cert_install(self):
        self._update_what_installed("identity_cert_installed")

    def docker_ce_install(self):
        self._update_what_installed("docker_installed")

    def docker_compose_install(self):
        self._update_what_installed("docker_compose_installed")

    def docker_yacht_install(self):
        self._update_what_installed("yacht_installed")

    def python3_install(self):
        self._update_what_installed("python3_installed")

    def is_docker_compose_installed(self):
        return self._is_what_installed("docker_compose_installed")

    def is_docker_yacht_installed(self):
        return self._is_what_installed("yacht_installed")

    def is_docker_ce_installed(self):
        return self._is_what_installed("docker_installed")

    def is_python_installed(self):
        return self._is_what_installed("python3_installed")

    def is_cert_installed(self):
        return self._is_what_installed("identity_cert_installed")

    def get_info(self):
        return self.get_host_info(self._tblembr, self.server_id)

    def _check_point_update(self, key: str, how_long_seconds: int = 3600):
        self._check_point_update_res(self._tblembr, self.server_id, key, how_long_seconds)

    def _is_what_ready(self, key: str) -> bool:
        return self._is_what_ready_res(self._tblembr, self.server_id, key)

    def insert_new(self, update_params: dict) -> bool:
        return self.insert_row_dat(self._tblembr, update_params)

    def update_param(self, server_id: str, update_param: dict) -> bool:
        return self.update_by_id(self._tblembr, server_id, update_param)

    def has_this_server(self) -> bool:
        return self.has_id_in_tbl(self._tblembr, self.server_id)

    def _update_server_meta(self, server_id: str, res_file: dict):
        update_dic = {
            "res": json.dumps(res_file)
        }
        return self.update_param(server_id, update_dic)

    def _insert_server(self, host: str, id: str, password: str, user: str, port: int,
                       file: dict) -> bool:
        p = {
            "host": host,
            "id": id,
            "user": user,
            "pass": password,
            "port": port,
            "next_action": "{}",
            "description": "",
            "res": json.dumps(file)
        }
        return self.insert_new(p)

    def total_count(self, tbl: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT COUNT(*) as count FROM {tbl}")
        (count,) = cursor.fetchone()
        cursor.close()
        if count > 0:
            print(count)
        return count

    def show_all_serv(self) -> list:
        h = self.show_all_servers(self._tblembr)
        return h

    def set_server_id(self, server_id: str):
        self.server_id = server_id

    def update_profile(self, profile_res: dict):
        da = self.get_member_res(self._tblembr, self.server_id)
        da.update({"profile": profile_res})
        self._update_server_meta(self.server_id, da)

    def get_home_path(self) -> str:
        da = self.get_member_res(self._tblembr, self.server_id)
        if "home_path" in da:
            return da["home_path"]
        else:
            return ""

    def _update_what_installed(self, program_key: str):
        da = self.get_member_res(self._tblembr, self.server_id)
        da.update({program_key: True})
        self._update_server_meta(self.server_id, da)

    def _is_what_installed(self, program: str):
        return self.is_what_installed_full(program, self.server_id)

    def is_what_installed_full(self, program: str, server_id: str):
        da = self.get_member_res(self._tblembr, server_id)
        return True if program in da and da[program] is True else False

    def tipping_point(self, user: str, id: str, host: str, password: str, port: int = 22):
        """
        first time to receive profile data to the account and handle the creating the new one on the fly.
        """
        if self.has_this_server() is False:
            # first time registration
            self._insert_server(host, id, password, user, port, {})
        else:
            # update when the new data is found. but the ID cannot be updated.
            p = {
                "host": host,
                "user": user,
                "pass": password,
                "port": port,
            }
            return self.update_param(self.server_id, p)

    def set_invalidate_token(self):
        d = self.get_member_res(self._tblembr, self.server_id)
        d.update({
            "expires_in": 0
        })
        self._update_server_meta(self.server_id, d)

    def get_access_token(self):
        if self.has_this_server() is False:
            return ""
        d = self.get_member_res(self._tblembr, self.server_id)
        if "access_token" in d:
            current_time = datetime.datetime.now().timestamp()
            current_time = int(current_time)
            exp = d["expires_in"]
            return d["access_token"] if current_time < exp else ""
        else:
            return ""
