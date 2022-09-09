"""Git."""

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
    return f"{id}.ttl"


def graph_path(repo: Repo, filename: str) -> str:
    """Path of graph within repo."""
    return os.path.join(str(repo.working_tree_dir), filename)


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
