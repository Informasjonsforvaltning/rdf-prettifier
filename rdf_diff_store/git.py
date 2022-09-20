"""Git."""

import os
from typing import Optional

from git import Repo
from git.exc import NoSuchPathError


def get_repo() -> Repo:
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

    return repo


def graph_filename(id: str) -> str:
    """Filename of graph."""
    return f"{id}.ttl"


def graph_path(repo: Repo, filename: str) -> str:
    """Path of graph within repo."""
    return os.path.join(str(repo.working_tree_dir), filename)


def delete_graph(id: str) -> None:
    """Delete graph."""
    repo = get_repo()
    filename = graph_filename(id)
    path = graph_path(repo, filename)

    os.remove(path)
    repo.index.remove([filename])
    repo.index.commit(f"delete: {id}")


def load_graph(id: str, timestamp: Optional[int]) -> str:
    """Load graph."""
    repo = get_repo()

    if timestamp:
        # Ensure no code injection, don't trust python.
        if not isinstance(timestamp, int):
            raise ValueError("timestamp not an integer")
        ref = repo.git.rev_list("--max-count", "1", "--before", f"{timestamp}", "HEAD")
        repo.git.checkout(ref)

    path = graph_path(repo, graph_filename(id))

    with open(path, "r") as f:
        return f.read()


def store_graph(id: str, graph: str) -> None:
    """Store graph."""
    repo = get_repo()
    filename = graph_filename(id)

    path = graph_path(repo, filename)
    with open(path, "w") as f:
        f.write(graph)

    repo.index.add([filename])
    repo.index.commit(f"update: {id}")
