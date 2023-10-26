import psycopg2
import json
import time
from datetime import datetime


class PG_SQL:
    dbname = ''
    user = ''
    password = ''
    host = ''
    connection = None
    columns = {'cardNum': 'bigint',
               'drivers': 'text',
               'dates': 'int',
               'amounts': 'real',
               'prices': 'real',
               'sums': 'real',
               'posBrands': 'text',
               'latitude': 'real',
               'longitude': 'real',
               'posAddress': 'text',
               'serviceName': 'text'
               }
    read = None
    write = None

    def __init__(self):
        with open('config_SQL.json', encoding='utf-8') as p:
            config_sql = json.load(p)
        self.dbname = config_sql["db_name"]
        self.user = config_sql["user"]
        self.password = config_sql["password"]
        self.host = config_sql["host"]
        self.read = read_SQL()
        self.write = write_SQL()

    def _connect(self):
        try:
            self.connection = psycopg2.connect(dbname=self.dbname,
                                               user=self.user,
                                               password=self.password,
                                               host=self.host)
        except Exception as _ex_connect:
            print('Подключение к БД - ', _ex_connect)
        return self.connection

    def _disconnect(self):
        self.connection.close()


class read_SQL(PG_SQL):

    def __init__(self):
        with open('config_SQL.json', encoding='utf-8') as p:
            config_sql = json.load(p)
        self.dbname = config_sql["db_name"]
        self.user = config_sql["user"]
        self.password = config_sql["password"]
        self.host = config_sql["host"]

    def read_max_val_in_column(self, table, column, schema='', filters: dict = None):
        """
        :param filters: фильтр AND по колонкам {'Название колонки': 'Искомое значение'}. Колонок для фильтрации может
        быть несколько.
        :param schema: схема для подключения к таблице
        :param table: наименование таблицы
        :param column: столбец, по которому произвести сортировку (от макс. к мин.)
        :return: максимальное значение в столбце
        """
        sc = ''
        f = ''
        if schema != '':
            sc = f'{schema}.'
        if filters is not None:
            f = ' WHERE ' + ' AND '.join([f'{f_r}={filters[f_r]}' for f_r in filters.keys()])
        command = f'SELECT {column} FROM {sc}{table}{f} ORDER BY {column} DESC'
        self._connect()
        with self.connection.cursor() as cursor:
            try:

                cursor.execute(command)
                row = cursor.fetchone()
            except Exception as _ex:
                print('Чтение строк - ', _ex)
        self._disconnect()
        try:
            return row[0]
        except TypeError:
            return 0
        except UnboundLocalError:
            return 0

    def read_rows(self, table, col_s=None, schema='', filters: dict = None, limit=None):
        all_rows = []
        param = '*'
        sc = ''
        f = ''
        l = ''
        if schema != '':
            sc = f'{schema}.'
        if filters is not None:
            f = ' WHERE ' + ' AND '.join([f'{f_r}{filters[f_r]}' for f_r in filters.keys()])
        if col_s is not None:
            if len(col_s) > 1:
                param = ', '.join(col_s)
            elif len(col_s) == 1:
                param = str(col_s[0])
        if limit is not None:
            l = f' LIMIT {limit}'
        command = f'SELECT {param} FROM {sc}{table}{f}{l}'
        self._connect()
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(command)
                all_rows = cursor.fetchall()
            except Exception as _ex_read_rows:
                print('Чтение строк - ', _ex_read_rows)
        self._disconnect()
        return all_rows

    def read_table(self, table):
        all_rows = []
        command = f"SELECT * FROM INFORMATION_SCHEMA.COLUMNS where TABLE_NAME='{table}'"
        # print(command)
        self._connect()
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(command)
                all_rows = cursor.fetchall()
            except Exception as _ex_read_rows:
                print('Чтение строк - ', _ex_read_rows)
        self._disconnect()
        return all_rows


class write_SQL(PG_SQL):

    def __init__(self):
        with open('config_SQL.json', encoding='utf-8') as p:
            config_sql = json.load(p)
        self.dbname = config_sql["db_name"]
        self.user = config_sql["user"]
        self.password = config_sql["password"]
        self.host = config_sql["host"]

    def append_rows(self, table, rows, columns=None, schema=''):
        sc = ''
        if schema != '':
            sc = f'{schema}.'
        if columns is not None:
            col_s = f"({', '.join(columns)})"
        else:
            col_s = f"({', '.join([key for key in rows.keys()])})"
        count = len(rows[[key for key in rows.keys()][0]])
        # data = [tuple([str(value[i]) for value in rows.values()]) for i in range(count)]
        # rows_records = ', '.join(["%s"] * len(data))
        for i in range(count):
            rows_records = tuple([str(value[i]) for value in rows.values()])
            command = f'INSERT INTO {sc}{table}{col_s} VALUES {rows_records}'
            print(command)
            self._connect()
            with self.connection.cursor() as cursor:
                try:
                    cursor.execute(command)
                    self.connection.commit()
                    print(f'Строка {i+1} из {count} занесена в {table}')
                except Exception as _ex_append_rows:
                    pass
            self._disconnect()

    def append_row(self, schema, table, value):
        command = f"INSERT INTO {schema}.{table} VALUES ('{value}')"
        self._connect()
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(command)
                self.connection.commit()
                self._disconnect()
                return True, 'Строка добавлена'
            except Exception as _ex_append_rows:
                return False, _ex_append_rows

    def delete_row(self, schema, table, value, column):
        command = f"DELETE FROM {schema}.{table} WHERE {column} = {value}"
        self._connect()
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(command)
                self.connection.commit()
                self._disconnect()
                return True, 'Строка удалена'
            except Exception as _ex_append_rows:
                return False, _ex_append_rows


    def update_rows(self, schema, table, value, column):
        command = f"UPDATE {schema}.{table} SET {column} = '{value}'"
        self._connect()
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(command)
                self.connection.commit()
                self._disconnect()
                return True, 'Строка обновлена'
            except Exception as _ex_append_rows:
                return False, _ex_append_rows


def get_trusted_terminals():
    sql = PG_SQL()
    rows = sql.read.read_rows(table='confirmed_terminal_list', schema='public')
    terminals = '\n'.join([str(row[0]) for row in rows])
    current_time = datetime.fromtimestamp(time.time()).strftime('%d-%m-%Y %H.%M.%S')
    filename = f'{current_time} trusted terminals.txt'
    with open(filename, 'w') as file:
        file.write(terminals)
    return filename


def append_terminal(terminal):
    sql = PG_SQL()
    if check_terminal(terminal):
        return False, f"Терминал {terminal} уже есть в БД"
    else:
        result, reason = sql.write.append_row(value=terminal, table='confirmed_terminal_list', schema='public')
        if result:
            return result, 'Терминал добавлен.'
        else:
            return result, reason


def delete_terminal(terminal):
    sql = PG_SQL()
    if not check_terminal(terminal):
        return False, f"Терминал {terminal} отсутствует в БД"
    else:
        result, reason = sql.write.delete_row(value=terminal, table='confirmed_terminal_list', schema='public', column='terminal')
        if result:
            return result, 'Терминал удален.'
        else:
            return result, reason


def check_terminal(terminal):
    sql = PG_SQL()
    rows = sql.read.read_rows(table='confirmed_terminal_list', schema='public')
    terminals = [str(row[0]) for row in rows]
    if str(terminal) in terminals:
        return True
    else:
        return False


def check_token():
    sql = PG_SQL()
    rows = sql.read.read_rows(table='api_key', schema='public')
    return rows[0][0], rows[0][1]


def update_token(token):
    sql = PG_SQL()
    result, reason = sql.write.update_rows(value=token, table='api_key', schema='public',
                                          column='api_key')
    result, reason = sql.write.update_rows(value=True, table='api_key', schema='public',
                                           column='status')
    if result:
        return result, 'Токен обновлен.'
    else:
        return result, reason



if __name__ == '__main__':
    sql = PG_SQL()
    print(check_token())
    # print(update_token('61ffc39253cc2d2fe46a33ae2a0286c70C3DF3011A9691F64E4A056FAEB65F3FED86A5E9'))
    print(check_token())
    # print(sql.read.read_rows(table='confirmed_terminal_list', schema='public'))
    # print(sql.read.read_rows(table='refuelings', schema='refuelings'))
    # print(check_terminal(123456789))
    # append_terminal(326777889)
    # print(delete_terminal(123456789))
    # sql.write.append_row('public', 'confirmed_terminal_list', 326777888)
    # append_terminal(123456780)
    # print(check_terminal(123456789))
    # get_trusted_terminals()
    # print(sql.read.read_table(table='confirmed_terminal_list'))
