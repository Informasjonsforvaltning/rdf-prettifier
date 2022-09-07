"""Nox sessions."""
import sys

import nox
from nox_poetry import Session, session

python_versions = ["3.9", "3.10"]
nox.options.envdir = ".cache"
# To run consecutive nox sessions faster.
nox.options.reuse_existing_virtualenvs = False
nox.options.sessions = (
    "black",
    "lint",
    "mypy",
    "safety",
    "unit",
    "integration",
)


@session(python=python_versions)
def codegen(session: Session) -> None:
    """Generate code from API spec."""
    # TODO: https://github.com/koxudaxi/fastapi-code-generator/issues/186
    session.install("fastapi-code-generator")
    session.run(
        "fastapi-codegen", "--input", "openapi.yaml", "--output", "rdf_diff_store"
    )
    session.notify("black")


@session(python=python_versions[0])
def cache(session: Session) -> None:
    """Clear cache."""
    session.run(
        "bash",
        "-c",
        "for f in $(find . -maxdepth 1 -name '*cache*'); do rm -rf $f; done",
        external=True,
    )


@session(python=python_versions[0])
def black(session: Session) -> None:
    """Run black code formatter."""
    args = session.posargs or ["."]
    session.install("black")
    session.run("black", *args)


@session(python=python_versions[0])
def lint(session: Session) -> None:
    """Lint using flake8."""
    args = session.posargs or ["."]
    session.install(
        "flake8",
        "flake8-annotations",
        "flake8-bandit",
        "flake8-black",
        "flake8-builtins",
        "flake8-bugbear",
        "flake8-docstrings",
        "flake8-import-order",
        "flake8-isort",
        "flake8-rst-docstrings",
        "pep8-naming",
    )
    session.run("flake8", *args)


@session(python=python_versions)
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or ["rdf_diff_store", "tests"]
    session.install(".")
    session.install("mypy", "pytest")
    session.run("mypy", *args)
    # --python-executable to get nox/nox_poetry type information without installing in virtualenv.
    if not session.posargs:
        session.run("mypy", f"--python-executable={sys.executable}", "noxfile.py")


@session(python=python_versions)
def unit(session: Session) -> None:
    """Run the unit test suite."""
    args = session.posargs
    session.install(".")
    session.install("coverage[toml]", "pytest")
    # -rA shows extra test summary info regardless of test result
    try:
        session.run(
            "pytest",
            "-m",
            "unit",
            "-rA",
            *args,
        )
    finally:
        if session.interactive:
            session.notify("coverage")


@session(python=python_versions)
def integration(session: Session) -> None:
    """Run the integration test suite."""
    args = session.posargs
    session.install(".")
    session.install("coverage[toml]", "pytest")
    # -rA shows extra test summary info regardless of test result
    try:
        session.run(
            "pytest",
            "-m",
            "integration",
            "-rA",
            *args,
        )
    finally:
        if session.interactive:
            session.notify("coverage")


@session(python=python_versions[0])
def coverage(session: Session) -> None:
    """Produce the coverage report."""
    args = session.posargs or ["report"]
    session.install("coverage[toml]")
    session.run("coverage", *args)


@session(python=python_versions[0])
def codecov(session: Session) -> None:
    """Upload coverage data."""
    session.install("coverage[toml]", "codecov")
    # See pyproject.toml for configuration
    # --fail-under=0 to NOT fail in coverage, and upload regardless of coverage percent
    session.run("coverage", "xml", "--fail-under=0")
    session.run("codecov", *session.posargs)


@session(python=python_versions[0])
def safety(session: Session) -> None:
    """Scan dependencies for insecure packages."""
    ignore = [
        # rdflib
        "48547",
    ]
    ignore_args = [f"--ignore={i}" for i in ignore]
    requirements = session.poetry.export_requirements()
    session.install("safety")
    session.run(
        "safety", "check", "--full-report", f"--file={requirements}", *ignore_args
    )
