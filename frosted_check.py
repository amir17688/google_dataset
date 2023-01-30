"""Check Python-code with frosted."""
import frosted.api


def check(file_staged_for_commit, options):
    if file_staged_for_commit.is_python_code():
        status = frosted.api.check(
            file_staged_for_commit.contents,
            file_staged_for_commit.path,
        )
        return status == 0
    else:
        return True
