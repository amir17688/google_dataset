"""Check files with flake8."""
import flake8.main


DEFAULTS = {
    'ignore': 'E226',
    # TODO (evvers@ya.ru): Change complexity to 11 when mccabe=0.2.2 released
    # https://github.com/flintwork/mccabe/issues/5
    'complexity': '12'
}


def check(file_staged_for_commit, options):
    if file_staged_for_commit.is_python_code():
        status = flake8.main.check_code(
            file_staged_for_commit.contents,
            ignore=(
                c for c in options.flake8_ignore.split(',') if c
            ),
            complexity=int(options.flake8_complexity),
        )
        return status == 0
    else:
        return True
