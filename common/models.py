# -*- coding: utf-8 -*-

"""
@author: Mr_zhang
@software: PyCharm
@file: models.py
@time: 2020/8/9 12:56
"""

from common.connproxy import StoreContext


class BaseModel(object):
    """
    DataBaseModel
    """

    async def query(self, query, params=None):
        """
        :return: returns a row list for the given query and parameters.
        """
        with StoreContext() as store:
            cur = await store.execute(query, params)
            res = cur.fetchall()
        return res

    async def get(self, query, params=None):
        """
        Returns the (singular) row returned by the given query.
        If the query has no results, returns None.  If it has
        more than one result, raises an exception.
        """
        rows = await self.query(query, params)
        if not rows:
            return {}
        elif len(rows > 1):
            raise Exception("Multiple rows returned for Database.get() query")
        else:
            return rows[0]

    async def execute_lastrowid(self, query, params=None):
        """
        Executes the given query, returning the lastrowid from the query.
        """
        with StoreContext() as store:
            cur = await store.execute(query, params)
            res = cur.lastrowid
        return res

    async def execute_rowcount(self, query, params):
        """
        Executes the given query, returning the rowcount from the query.
        """
        with StoreContext() as store:
            cur = await store.execute(query, params)
            res = cur.rowcount
        return res

    async def begin(self):
        """
        Start transaction
        Wait to get connection and returns `Transaction` object.
        :return: Future[Transaction]
        """
        with StoreContext() as store:
            ctx = await store.begin()
        return ctx

    async def executemany_rowcount(self, query, params=None):
        with StoreContext() as store:
            conn = await store._get_conn()
            try:
                cur = conn.cursor()
                await cur.executemany(query, params)
                await cur.close()
            except:
                store._close_conn(conn)
            else:
                store._put_conn(conn)
            return cur.rowcount

    async def executemany_lastrowid(self, query, params=None):
        with StoreContext() as store:
            conn = await store._get_conn()
            try:
                cur = conn.cursor()
                await cur.executemany(query, params)
                await cur.close()
            except:
                store._close_conn(conn)
                raise
            else:
                store._put_conn(conn)
            return cur.rowcount

    async def ctx_executemany(self, ctx, query, params=None):
        ctx._ensure_conn()
        cur = ctx._conn.cursor()
        await cur.executemany(query, params)
        return cur

    insert = execute_lastrowid
    insertmany = executemany_lastrowid
    update = execute_rowcount
    updatemany = executemany_rowcount
    delete = execute_rowcount

