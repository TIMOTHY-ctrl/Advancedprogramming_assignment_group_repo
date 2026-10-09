from contextlib import AbstractContextManager
from src.Infrastructure.InMemoryStore import InMemoryStore


class InMemoryUnitOfWork:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def transaction(self) -> AbstractContextManager[None]:
        return self._store.transaction()
