from dataclasses import dataclass
from typing import List


@dataclass
class CommitInfo:
    sha: str
    message: str


@dataclass
class CodeRegion:
    filename: str
    code: str

@dataclass
class PromptRow:
    repo: str
    issue_no: int
    summary: str
    bertopic: int