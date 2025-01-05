import os
from typing import Optional
from datetime import datetime, UTC
from app.storage import write_object

def author_environ(
        author_name: str = "Author Name",
        author_email: str = "author@example.com",
        author_date: Optional[datetime] = None,
    ) -> str:
    author_name = os.environ.get("GIT_AUTHOR_NAME", author_name)
    author_email = os.environ.get("GIT_AUTHOR_EMAIL", author_email)
    author_date = os.environ.get("GIT_AUTHOR_DATE", author_date or datetime.now(UTC))
    return f"author {author_name} <{author_email}> {int(author_date.timestamp())} {author_date.strftime('%z')}"

def committer_environ(
        committer_name: str = "Committer Name",
        committer_email: str = "committer@example.com",
        committer_date: Optional[datetime] = None,
    ) -> str:
    committer_name = os.environ.get("GIT_COMMITTER_NAME", committer_name)
    committer_email = os.environ.get("GIT_COMMITTER_EMAIL", committer_email)
    committer_date = os.environ.get("GIT_COMMITTER_DATE", committer_date or datetime.now(UTC))
    return f"committer {committer_name} <{committer_email}> {int(committer_date.timestamp())} {committer_date.strftime('%z')}"

def create_commit(
        tree_sha: str,
        commit_sha: str,
        message: str):
    tree = f"tree {tree_sha}"
    parent = f"parent {commit_sha}"
    author = author_environ()
    committer = committer_environ()

    content = f"{tree}\n{parent}\n{author}\n{committer}\n\n{message}\n".encode()
    return write_object(content, "commit")