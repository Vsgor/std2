from __future__ import annotations

from asyncio.locks import Lock
from sqlite3 import Connection, Cursor, Row, connect
from typing import (
    Any,
    AsyncContextManager,
    AsyncIterable,
    AsyncIterator,
    Callable,
    Iterable,
    Iterator,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
    cast,
)

from .executor import Executor

T = TypeVar("T")

SQL_TYPES = Union[int, float, str, bytes, None]


def sql_escape(param: str, nono: Set[str], escape: str) -> str:
    def cont() -> Iterator[str]:
        for char in iter(param):
            if char in nono:
                yield escape
            yield char

    return "".join(cont())


class ACursor(AsyncContextManager[ACursor], AsyncIterable[Row]):
    def __init__(self, chan: Executor, cursor: Cursor) -> None:
        self._chan = chan
        self._cursor = cursor

    async def __aexit__(self, *_: Any) -> None:
        await self._chan.run(self._cursor.close)

    def __aiter__(self) -> AsyncIterator[Row]:
        async def cont() -> AsyncIterator[Row]:
            while rows := await self._chan.run(self._cursor.fetchmany):
                for row in rows:
                    yield row

        return cont()

    @property
    def lastrowid(self) -> Optional[int]:
        return cast(Optional[int], self._cursor.lastrowid)

    async def fetch_one(self) -> Row:
        return await self._chan.run(self._cursor.fetchone)


class AConnection(AsyncContextManager[None]):
    def __init__(self, database: str = ":memory:") -> None:
        self._exe = Executor()
        self._lock = Lock()

        def cont() -> Connection:
            conn = connect(database, isolation_level=None)
            conn.row_factory = Row
            return conn

        self._conn = self._exe.run_sync(cont)

    async def __aenter__(self) -> None:
        await self._lock.acquire()

    async def __aexit__(self, *_: Any) -> None:
        self._lock.release()

    @property
    def isolation_level(self) -> Optional[str]:
        return cast(Optional[str], self._conn.isolation_level)

    @property
    def in_transaction(self) -> bool:
        return cast(bool, self._conn.in_transaction)

    @property
    def row_factory(self) -> Optional[Type]:
        return cast(Optional[Type], self._conn.row_factory)

    async def cursor(self) -> ACursor:
        def cont() -> ACursor:
            cursor = self._conn.cursor()
            return ACursor(self._exe, cursor=cursor)

        return await self._exe.run(cont)

    async def commit(self) -> None:
        return await self._exe.run(self._conn.commit)

    async def rollback(self) -> None:
        return await self._exe.run(self._conn.rollback)

    async def close(self) -> None:
        return await self._exe.run(self._conn.close)

    async def execute(self, sql: str, params: Iterable[SQL_TYPES] = ()) -> ACursor:
        def cont() -> ACursor:
            cursor = self._conn.execute(sql, params)
            return ACursor(self._exe, cursor=cursor)

        return await self._exe.run(cont)

    async def execute_many(
        self, sql: str, params: Iterable[Iterable[SQL_TYPES]] = ()
    ) -> ACursor:
        def cont() -> ACursor:
            cursor = self._conn.executemany(sql, params)
            return ACursor(self._exe, cursor=cursor)

        return await self._exe.run(cont)

    async def execute_script(self, script: str) -> ACursor:
        def cont() -> ACursor:
            cursor = self._conn.executescript(script)
            return ACursor(self._exe, cursor=cursor)

        return await self._exe.run(cont)

    async def create_function(
        self,
        name: str,
        num_params: int,
        func: Callable[..., SQL_TYPES],
        deterministic: bool,
    ) -> None:
        def cont() -> None:
            self._conn.create_function(
                name, num_params=num_params, deterministic=deterministic, func=func
            )

        return await self._exe.run(cont)

    async def create_aggregate(
        self, name: str, num_params: int, aggregate_class: Type
    ) -> None:
        def cont() -> None:
            self._conn.create_aggregate(
                name, num_params=num_params, aggregate_class=aggregate_class
            )

        return await self._exe.run(cont)

    async def create_collation(
        self, name: str, callable: Callable[..., SQL_TYPES]
    ) -> None:
        def cont() -> None:
            self._conn.create_collation(name, callable=callable)

        return await self._exe.run(cont)

    def interrupt(self) -> None:
        self._conn.interrupt()

    async def with_raw_cursor(self, block: Callable[[Cursor], T]) -> T:
        def cont() -> T:
            cursor = self._conn.cursor()
            try:
                return block(cursor)
            finally:
                cursor.close()

        return await self._exe.run(cont)
