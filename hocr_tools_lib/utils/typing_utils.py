try:
    from _typeshed import SupportsRead
except ImportError:
    # Re-implementation of the original version.
    from typing import Protocol, TypeVar

    _T_co = TypeVar("_T_co", covariant=True)

    class SupportsRead(Protocol[_T_co]):  # type: ignore[no-redef]
        def read(self, __length: int = ...) -> _T_co:
            ...

    # For `lxml` support.
    class SupportsReadClose(SupportsRead[_T_co], Protocol[_T_co]):
        def close(self) -> None:
            ...


__all__ = [
    "SupportsRead",
]
