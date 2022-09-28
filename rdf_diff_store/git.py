"""Git."""

import asyncio
import base64
from contextlib import asynccontextmanager
import fcntl
import os
from typing import Iterator, Optional

from git import Repo
from git.exc import NoSuchPathError


def acquire_lock():
    f = open("/rdf-diff-store.lock", "w")
    fcntl.flock(f, fcntl.LOCK_EX)
    return f


@asynccontextmanager
async def lock():
    loop = asyncio.get_running_loop()
    f = await loop.run_in_executor(None, acquire_lock)
    try:
        yield
    finally:
        f.close()


def get_repo(timestamp: Optional[int] = None) -> Repo:
    """Get or create git repo."""
    repo_path = "repo"
    try:
        repo = Repo(repo_path)
        repo.git.checkout("master")
    except NoSuchPathError:
        repo = Repo.init(repo_path)

    with repo.config_writer() as git_config:
        git_config.set_value("user", "email", "fellesdatakatalog@digdir.no")
        git_config.set_value("user", "name", "rdf-diff-store")

    if timestamp:
        checkout_timestamp(repo, timestamp)

    return repo


def checkout_timestamp(repo: Repo, timestamp: int) -> None:
    """Checkout commit that matches a specific timestamp in repo."""
    # Ensure no code injection, don't trust python.
    if not isinstance(timestamp, int):
        raise ValueError("timestamp not an integer")
    ref = repo.git.rev_list("--max-count", "1", "--before", f"{timestamp}", "HEAD")
    repo.git.checkout(ref)


def graph_filename(id: str) -> str:
    """Filename of graph."""
    valid_filename_chars = (
        base64.b64encode(id.encode("utf-8"))
        .decode("utf-8")
        .replace("/", "_")
        .replace("+", "-")
    )
    return f"{valid_filename_chars}.ttl"


def graphs_dir(repo: Repo) -> str:
    """Dir containing graphs within repo."""
    return str(repo.working_tree_dir)


def graph_path(repo: Repo, filename: str) -> str:
    """Path of graph within repo."""
    return os.path.join(str(repo.working_tree_dir), filename)


async def delete_graph(id: str) -> None:
    """Delete graph."""
    async with lock():
        repo = get_repo()
        filename = graph_filename(id)
        path = graph_path(repo, filename)

        os.remove(path)
        repo.index.remove([filename])
        repo.index.commit(f"delete: {id}")


async def load_graph(id: str, timestamp: Optional[int]) -> str:
    """Load graph."""
    async with lock():
        repo = get_repo(timestamp)
        path = graph_path(repo, graph_filename(id))

        with open(path, "r") as f:
            return f.read()


async def load_all_graphs(timestamp: Optional[int]) -> Iterator[str]:
    """Load all graph."""
    async with lock():
        repo = get_repo(timestamp)

        for filename in os.listdir(graphs_dir(repo)):
            try:
                with open(graph_path(repo, filename), "r") as f:
                    yield f.read()
            except IsADirectoryError:
                pass


async def store_graph(id: str, graph: str) -> None:
    """Store graph."""
    async with lock():
        repo = get_repo()
        filename = graph_filename(id)

        path = graph_path(repo, filename)
        with open(path, "w") as f:
            f.write(graph)

        repo.index.add([filename])
        repo.index.commit(f"update: {id}")

