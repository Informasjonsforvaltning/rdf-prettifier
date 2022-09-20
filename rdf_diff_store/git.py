"""Git."""

import base64
import os

from git import Repo
from git.exc import NoSuchPathError


def get_repo() -> Repo:
    """Get or create git repo."""
    repo_path = "repo"
    try:
        repo = Repo(repo_path)
    except NoSuchPathError:
        repo = Repo.init(repo_path)

    with repo.config_writer() as git_config:
        git_config.set_value("user", "email", "fellesdatakatalog@digdir.no")
        git_config.set_value("user", "name", "rdf-diff-store")

    return repo


def graph_filename(id: str) -> str:
    """Filename of graph."""
    valid_filename_chars = (
        base64.b64encode(id.encode("utf-8"))
        .decode("utf-8")
        .replace("/", "_")
        .replace("+", "-")
    )
    return f"{valid_filename_chars}.ttl"


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


def load_graph(id: str) -> str:
    """Load graph."""
    path = graph_path(get_repo(), graph_filename(id))

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
