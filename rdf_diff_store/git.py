"""Git."""

import asyncio
import base64
from contextlib import asynccontextmanager
import fcntl
import os
from typing import Any, AsyncGenerator, Optional

from git import Repo
from git.exc import GitCommandError, NoSuchPathError

from rdf_diff_store.models import Metadata


REPO_PATH = os.getenv("REPO_PATH", "diff-store-autodeleted-repo")


class PrehistoricError(Exception):
    """Error raised when requesting a timestamp preceding first diff in store."""

    pass


def acquire_lock() -> Any:
    """Lock for git repo usage."""
    f = open("rdf-diff-store-repo.lock", "w")
    fcntl.flock(f, fcntl.LOCK_EX)
    return f


@asynccontextmanager
async def lock() -> Any:
    """Lock.

    with async lock():
        # use repo
    """
    loop = asyncio.get_running_loop()
    f = await loop.run_in_executor(None, acquire_lock)
    try:
        yield
    finally:
        f.close()


def get_repo(timestamp: Optional[int] = None) -> Repo:
    """Get or create git repo."""
    try:
        repo = Repo(REPO_PATH)
        try:
            repo.git.checkout("master")
        except GitCommandError as e:
            # exception is ok if error is the following
            # (because no commits has been made to master yet).
            if (
                "error: pathspec 'master' did not match any file(s) known to git"
                not in f"{e}"
            ):
                raise e
    except NoSuchPathError:
        repo = Repo.init(REPO_PATH)

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
    if ref:
        repo.git.checkout(ref)
    else:
        raise PrehistoricError()


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
        try:
            repo = get_repo(timestamp)
        except PrehistoricError as e:
            raise FileNotFoundError() from e

        path = graph_path(repo, graph_filename(id))

        with open(path, "r") as f:
            return f.read()


async def iterate_all_graphs(timestamp: Optional[int]) -> AsyncGenerator[str, None]:
    """Iterate all graphs."""
    async with lock():
        try:
            repo = get_repo(timestamp)
        except PrehistoricError:
            # return + yield results in empty generator
            return
            yield

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


async def repo_metadata() -> Metadata:
    """Get diff store metadata."""
    async with lock():
        repo = get_repo()
        try:
            *_, first = repo.iter_commits()
            return Metadata(
                empty=False,
                start_time=first.committed_date,
            )
        # no commits in repo
        except ValueError:
            return Metadata(empty=True)
