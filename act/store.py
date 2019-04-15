# -*- coding: utf-8 -*-
# API - act
# FileName: store.py
# Version: 1.0.0
# Create: 2018-10-17
# Modify: 2018-11-27
import pymysql
from . import default
import tablestore as ts
from .util import Format
from .exception import InvalidParam


class Database(object):
    pass


class StoreType(object):
    """
    OSS: Object Storage Service
    OTS: Table Store
    MYSQL: MySQL
    """
    OSS = 'OSS'
    OTS = 'OTS'
    MYSQL = 'MYSQL'

    __values__ = [
        OSS,
        OTS,
        MYSQL,
    ]

    __members__ = [
        'StoreType.OSS',
        'StoreType.OTS',
        'StoreType.MYSQL',
    ]


class OTSRowCondition(object):
    """
    IGNORE: Without check for existence
    EXPECT_EXIST: Expect row exists
    EXPECT_NOT_EXIST: Expect row does not exist
    """
    IGNORE = 'IGNORE'
    EXPECT_EXIST = 'EXPECT_EXIST'
    EXPECT_NOT_EXIST = 'EXPECT_NOT_EXIST'

    __values__ = [
        IGNORE,
        EXPECT_EXIST,
        EXPECT_NOT_EXIST,
    ]

    __members__ = [
        'RowCondition.IGNORE',
        'RowCondition.EXPECT_EXIST',
        'RowCondition.EXPECT_NOT_EXIST',
    ]


class OTSReturnType(ts.metadata.ReturnType):
    """
    RT_NONE: Return nothing
    RT_PK: Return primary key
    """
    pass


class LogicalOperator(object):
    def __init__(self, logical_operator):
        """
        :param str logical_operator: 'AND' / 'OR' / 'NOT'
        """
        logical_operator = logical_operator.strip()
        self.OTS = getattr(ts.LogicalOperator, logical_operator)
        self.MYSQL = logical_operator.lower()


class OTSRetryPolicy(ts.DefaultRetryPolicy):
    """
    Modify SDK class DefaultRetryPolicy here
    """
    max_retry_times = 2


class ComparatorType(object):
    """
    :param str comparator_type: '=' / '!=' / '>' / '>=' / '<' / '<='
    """
    __MAP__ = {
        '=': 'EQUAL',
        '!=': 'NOT_EQUAL',
        '>': 'GREATER_THAN',
        '>=': 'GREATER_EQUAL',
        '<': 'LESS_THAN',
        '<=': 'LESS_EQUAL',
    }

    def __init__(self, comparator_type):
        """
        :param str comparator_type: '=' / '!=' / '>' / '>=' / '<' / '<='
        """
        comparator_type = comparator_type.strip()
        comparator = Format.get(self.__MAP__, comparator_type)
        if comparator is None:
            raise InvalidParam(doc=self.__class__)
        self.OTS = getattr(ts.ComparatorType, comparator)
        self.MYSQL = comparator_type.replace('!=', '<>')


class StoreData(object):
    """
    :param list or tuple or dict or None data: Eg: [(key, value), (key, value, version)]
    """

    def __init__(self, data=None):
        """
        :param list or tuple or dict or None data: Eg: [(key, value), (key, value, version)]
        """
        self.dict = dict()
        self.list = list()
        self.version = dict()
        if data is not None:
            self.update(data)

    def update(self, data):
        """
        :param list or tuple or dict data: Eg: [(key, value), (key, value, version)]
        """
        if isinstance(data, dict):
            self.list = self.list + data.items()
            return self.dict.update(data)
        if not isinstance(data, (list, tuple)):
            raise InvalidParam(doc=self.__class__)
        self.list = self.list + list(data)
        for item in data:
            self.dict[item[0]] = item[1]
            if item[0] not in self.version:
                self.version[item[0]] = list()
            self.version[item[0]] += [(item[1], 0 if len(item) < 3 else item[2])]
        return self


class OTS(Database):
    def __init__(self, access_key_id, access_key_secret, end_point, instance_name, encoding=default.CODING,
                 retry_policy=OTSRetryPolicy(), socket_timeout=default.OTS_TIMEOUT, table_name=None, **kwargs):
        """
        :param str access_key_id: Access Key ID
        :param str access_key_secret: Access Key Secret
        :param str end_point: Table store server domain started with https://
        :param str instance_name: Instance name of table store
        :param str or None encoding: Encoding
        :param OTSRetryPolicy or None retry_policy: Retry policy
        :param int or float or None socket_timeout: Socket timeout
        :param str table_name: Default table name
        """
        self.table_name = table_name
        self.client = ts.OTSClient(
            end_point,
            access_key_id,
            access_key_secret,
            instance_name,
            encoding=encoding,
            retry_policy=retry_policy,
            socket_timeout=socket_timeout,
            **kwargs,
        )

    @staticmethod
    def format_update_row(index, column):
        """
        :param list or tuple index:
        :param list or tuple column:
        :return:
        """
        update_column = {
            'PUT': list(),
            'DELETE': list(),
            'DELETE_ALL': list(),
        }
        if column is None:
            column = tuple()
        for item in column:
            if item[1] is not None:
                update_column['PUT'].append(tuple(item))
                continue
            if len(item) > 2:
                update_column['DELETE'].append(tuple(item))
                continue
            update_column['DELETE_ALL'].append(tuple(item))
        return ts.Row(index, update_column)

    @staticmethod
    def filter(where=None, logical_operator=None):
        """
        :param list or tuple where: Filter. Eg: [('StartTime', ComparatorType('>='), 0)]
        :param LogicalOperator logical_operator: LogicalOperator('AND')
        :return:
        """
        if where is None:
            return None
        if logical_operator is None:
            logical_operator = LogicalOperator('AND')
        if not isinstance(where[0][1], ComparatorType):
            raise InvalidParam(doc=ComparatorType)
        column_filter = ts.CompositeColumnCondition(logical_operator.OTS)
        tuple(map(lambda c: column_filter.add_sub_condition(
            ts.SingleColumnCondition(c[0], c[2], c[1].OTS, *c[3:])), where))
        return column_filter

    def select(self, index, column=None, where=None, logical_operator=None, table_name=None,
               max_version=1, time_range=None, start_column=None, end_column=None, token=None):
        """
        :param list or tuple index: Primary key. Eg: [('ActID', 'abc')]
        :param list or tuple column: Column name. Eg: ['ActiveParty', 'PassiveParty']
        :param list or tuple where: Filter. Eg: [('StartTime', ComparatorType('>='), 0)]
        :param LogicalOperator logical_operator: LogicalOperator('AND')
        :param str table_name: Table name
        :param int max_version: Max version that you want to get
        :param int or tuple time_range: Filter with range of time, or get the specified version
        :param str start_column: Eg: columns => |a|b|c|, start_column => 'b', result => {'b': 'valueB', 'c': 'valueC'}
        :param str end_column: Eg: columns => |a|b|c|, end_column => 'b', result => {'a': 'valueA', 'b': 'valueB'}
        :param str token: Column token
        :return:
        """
        if table_name is None:
            table_name = self.table_name
        if logical_operator is None:
            logical_operator = LogicalOperator('AND')
        column_filter = self.filter(where, logical_operator)
        _, return_row, _ = self.client.get_row(
            table_name, index, column, column_filter,
            max_version, time_range, start_column, end_column, token)
        # Other parameters will not be processed for the time being.
        store_data = StoreData(getattr(return_row, 'primary_key', None))
        return store_data.update(getattr(return_row, 'attribute_columns', None))

    def insert(self, index, column=None, table_name=None, condition=None, return_type=None):
        """
        :param list or tuple index: Primary key. Eg: [('ActID', 'abc')]
        :param list or tuple column: Attribute column. Eg: [('StartTime', 0)]
        :param str table_name: Table name
        :param OTSRowCondition condition: Condition of existence of row
        :param OTSReturnType return_type: API return content
        :return:
        """
        if table_name is None:
            table_name = self.table_name
        if condition is None:
            condition = default.ROW_CONDITION
        elif not isinstance(condition, OTSRowCondition):
            raise InvalidParam(doc=OTSRowCondition)
        if return_type is not None and not isinstance(return_type, OTSReturnType):
            raise InvalidParam(doc=OTSReturnType)
        row = ts.Row(index, column)
        condition = ts.Condition(condition)
        _, return_row = self.client.put_row(table_name, row, condition, return_type)
        return StoreData(getattr(return_row, 'primary_key', None))

    def update(self, index, column, where=None, logical_operator=None,
               table_name=None, condition=None, return_type=None):
        """
        :param list or tuple index: Primary key. Eg: [('ActID', 'abc')]
        :param list or tuple column: Attribute column. Eg: [('PassiveParty', 'def', time.time() * 1000)]
        :param list or tuple where: Filter. Eg: [('StartTime', ComparatorType('>='), 0)]
        :param LogicalOperator logical_operator: LogicalOperator('AND')
        :param str table_name: Table name
        :param OTSRowCondition condition: Condition of existence of row
        :param OTSReturnType return_type: API return content
        :return:
        """
        column_filter = None
        if table_name is None:
            table_name = self.table_name
        if logical_operator is None:
            logical_operator = LogicalOperator('AND')
        if where is not None:
            if not isinstance(where[0][1], ComparatorType):
                raise InvalidParam(doc=ComparatorType)
            column_filter = ts.CompositeColumnCondition(logical_operator.OTS)
            tuple(map(lambda c: column_filter.add_sub_condition(
                ts.SingleColumnCondition(c[0], c[2], c[1].OTS, *c[3:])), where))
        if condition is None:
            condition = default.ROW_CONDITION
        elif not isinstance(condition, OTSRowCondition):
            raise InvalidParam(doc=OTSRowCondition)
        if return_type is not None and not isinstance(return_type, OTSReturnType):
            raise InvalidParam(doc=OTSReturnType)
        row = self.format_update_row(index, column)
        condition = ts.Condition(condition, column_filter)
        _, return_row = self.client.update_row(table_name, row, condition, return_type)
        return StoreData(getattr(return_row, 'primary_key', None))


class MySQL(Database):
    def __init__(self, user, password, charset=default.MYSQL_CHARSET, db=None,
                 host=default.MYSQL_HOST, port=default.MYSQL_PORT, table_name=None):
        """
        :param str user: User name of mysql server
        :param str password: Password of current user
        :param str charset: Charset
        :param str db: Name of database
        :param str host: Host. Default localhost
        :param int port: Port. Default 3306
        :param str table_name: Default table name
        """
        self.user = user
        self.password = password
        self.charset = charset
        self.db = db
        self.host = host
        self.port = port
        self.table_name = table_name
        self.connect_param = {
            'user': self.user,
            'password': self.password,
            'charset': self.charset,
            'db': self.db,
            'host': self.host,
            'port': self.port,
            'cursorclass': pymysql.cursors.DictCursor,
        }

    def execute(self, sql, *args, **kwargs):
        """
        :param str sql: Eg: 'select COLUMN from TABLE where KEY="{}"'
        :param tuple args: Args for sql. Eg: sql.format(*args)
        :param dict kwargs: dict connect_param: pymysql.connect(default, **connect_param)
        :param dict kwargs: bool escape: escape_string(*args)
        :return: Eg: [{'column': 'valueA'}, {'column': 'valueB'}]
        """
        sql = Format.mysql(sql, *args, escape=kwargs.get('escape', True))
        connect_param = self.connect_param.copy()
        connect_param.update(kwargs.get('connect_param', dict()))
        connect = pymysql.connect(**connect_param)
        try:
            cur = connect.cursor()
            results = cur.execute(sql)
            connect.commit()
        finally:
            connect.close()
        return list(cur.fetchmany(results))

    def select(self, index, column=None, where=None, logical_operator=None, table_name=None):
        """
        :param list or tuple index: Primary key. Eg: [('ActID', 'abc')]
        :param list or tuple column: Column name. Eg: ['ActiveParty', 'PassiveParty']
        :param list or tuple where: Filter. Eg: [('StartTime', ComparatorType('>='), 0)]
        :param LogicalOperator logical_operator: LogicalOperator('AND')
        :param str table_name: Table name
        :return:

        `[*list, *tuple]` instead of `list + tuple`
        """
        if column is None:
            column = ['*']
        if where is None:
            where = [('0', ComparatorType('='), 0)]
        if table_name is None:
            table_name = self.table_name
        if logical_operator is None:
            logical_operator = LogicalOperator('AND')
        if not isinstance(where[0][1], ComparatorType):
            raise InvalidParam(doc=ComparatorType)
        param = map(lambda i: i[-1], (*index, *where))
        index = tuple(map(
            lambda i: '{}={{}}'.format(i[0])
            if isinstance(i[1], int) else '{}="{{}}"'.format(i[0]), index))
        where = tuple(map(
            lambda i: '{0}{1}{{}}'.format(i[0], i[1].MYSQL)
            if isinstance(i[2], int) else '{0}{1}"{{}}"'.format(i[0], i[1].MYSQL), where))
        # [('PassiveParty', '=', 'ABC'), ('StartTime', '>=', 0)] => ['PassiveParty="{}"', 'StartTime>={}']
        index += ((' {} '.format(logical_operator.MYSQL)).join(where),)
        where_str = (' {} '.format(LogicalOperator('AND').MYSQL)).join(index)
        sql = 'SELECT {0} FROM {1} WHERE {2}'.format(','.join(column), table_name, where_str)
        # ((execute() => []) or [None])[0] => None
        return StoreData((self.execute(sql, *param) or [None])[0])

    def insert(self, index, column=None, table_name=None):
        """
        :param list or tuple index: Primary key. Eg: [('ActID', 'abc')]
        :param list or tuple column: Attribute column. Eg: [('StartTime', 0)]
        :param str table_name: Table name
        :return:
        """
        if column is None:
            column = tuple()
        if table_name is None:
            table_name = self.table_name
        param = map(lambda i: i[-1], [*index, *column])
        key_str = ','.join(tuple(map(
            lambda i: '{}={{}}'.format(i[0])
            if isinstance(i[1], int) else '{}="{{}}"'.format(i[0]), [*index, *column])))
        self.execute('INSERT INTO {0} SET {1}'.format(table_name, key_str), *param)

    def update(self, index, column, where=None, logical_operator=None, table_name=None):
        """
        :param list or tuple index: Primary key. Eg: [('ActID', 'abc')]
        :param list or tuple column: Attribute column. Eg: [('ActiveParty', 'abc')]
        :param list or tuple where: Filter. Eg: [('StartTime', ComparatorType('>='), 0)]
        :param LogicalOperator logical_operator: LogicalOperator('AND')
        :param str table_name: Table name
        :return:
        """
        if where is None:
            where = (('0', ComparatorType('='), 0),)
        if table_name is None:
            table_name = self.table_name
        if logical_operator is None:
            logical_operator = LogicalOperator('AND')
        if not isinstance(where[0][1], ComparatorType):
            raise InvalidParam(doc=ComparatorType)
        param = tuple(map(lambda i: i[1], column))
        param += tuple(map(lambda i: i[-1], (*index, *where)))
        column = tuple(map(
            lambda i: '{}={{}}'.format(i[0])
            if isinstance(i[1], int) else '{}="{{}}"'.format(i[0]), column))
        index = tuple(map(
            lambda i: '{}={{}}'.format(i[0])
            if isinstance(i[1], int) else '{}="{{}}"'.format(i[0]), index))
        where = tuple(map(
            lambda i: '{0}{1}{{}}'.format(i[0], i[1].MYSQL)
            if isinstance(i[2], int) else '{0}{1}"{{}}"'.format(i[0], i[1].MYSQL), where))
        index += ((' {} '.format(logical_operator.MYSQL)).join(where),)
        where_str = (' {} '.format(LogicalOperator('AND').MYSQL)).join(index)
        self.execute('UPDATE {0} SET {1} WHERE {2}'.format(table_name, ','.join(column), where_str), *param)
