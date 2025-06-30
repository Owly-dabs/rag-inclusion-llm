def is_test_file(filename: str) -> bool:
    """
    Return True if a filename appears to be a test file.

    Handles cases like:
    - test_*.py
    - tests/test_*.py
    - src/tests/utils/test_api.js
    """
    parts = filename.lower().split('/')
    return any(
        part.startswith('test_') or part in {'test', 'tests'}
        for part in parts
    )

def is_valid_file(filename: str) -> bool:
    """
    Return True if a filename is valid for processing.
    """
    return not is_test_file(filename) and not any(
        filename.endswith(ext) for ext in (
            '.md', '.rst', '.txt',  # Documentation files
            '.json', '.yaml', '.yml', '.ini',  # Configuration files
            '.yml', '.yaml', '.gitlab-ci.yml', '.github/workflows/', '.gitignore', # CI/CD files
            'Dockerfile', 'Jenkinsfile', 'Makefile',  # Other CI/CD related files
            '.xml', '.properties',  # Additional configuration files
            '.env',  # Environment variable files
            '.log',  # Log files
            '.sh',  # Shell scripts
            '.bat',  # Batch files
        )
    )