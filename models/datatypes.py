from dataclasses import dataclass, asdict
from typing import List


@dataclass
class CommitInfo:
    sha: str
    message: str


@dataclass
class CodeRegion:
    filename: str
    code: str
    explanation: str = None  # Optional explanation for the code region

@dataclass
class PromptRow:
    repo: str
    issue_no: int
    summary: str
    bertopic: int

@dataclass
class PromptResponse:
    repo: str
    issue_no: int
    topic: str
    code_regions: List[CodeRegion]
    
    def __getitem__(self, key):
        return asdict(self)[key]

    def __iter__(self):
        return iter(asdict(self))

@dataclass
class ReflectionResponse:
    repo: str
    issue_no: int
    topic: str
    code_before: str
    code_after: str
    original_explanation: str
    reflection_response: str