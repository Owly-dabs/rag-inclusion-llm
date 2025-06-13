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