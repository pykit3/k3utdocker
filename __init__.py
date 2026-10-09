# from .proc import CalledProcessError
# from .proc import ProcError

from .utdocker import (
    build_image,
    create_network,
    does_container_exist,
    get_client,
    pull_image,
    remove_container,
    start_container,
    stop_container,
)

__all__ = [
    "build_image",
    "create_network",
    "does_container_exist",
    "get_client",
    "pull_image",
    "remove_container",
    "start_container",
    "stop_container",
]


def __getattr__(name: str) -> str:
    # importlib.metadata takes about 20 ms to import, so it is loaded only
    # when __version__ is read
    if name != "__version__":
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    from importlib.metadata import version

    return version("k3utdocker")
