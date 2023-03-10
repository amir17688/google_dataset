# third-party imports
import chronos
import mock


def test_no_args(runner):
    result = runner(['cron'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output


def test_help(runner):
    result = runner(['cron', '--help'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output
    assert 'Manage Chronos Jobs' in result.output


@mock.patch.object(chronos.ChronosClient, 'list')
def test_show(mock_chronos_client, runner, json_fixture):
    mock_chronos_client.return_value = json_fixture("chronos_jobs")

    result = runner(['cron', 'show'], env={
        'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
    })

    assert '"name": "foo-job"' in result.output
    assert '"name": "bar-job"' in result.output
    assert result.exit_code == 0


@mock.patch.object(chronos.ChronosClient, 'list')
def test_show_job_name(mock_chronos_client, runner, json_fixture):
    mock_chronos_client.return_value = json_fixture("chronos_jobs")

    result = runner(['cron', 'show', '--job-name', 'foo-job'], env={
        'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
    })

    assert '"name": "foo-job"' in result.output
    assert '"name": "bar-job"' not in result.output
    assert result.exit_code == 0


@mock.patch.object(chronos.ChronosClient, 'list')
@mock.patch.object(chronos.ChronosClient, 'add')
def test_set(mock_chronos_add, mock_chronos_list, runner, json_fixture):
    mock_chronos_list.return_value = []
    mock_chronos_add.return_value = True

    result = runner(['cron', 'set', '--template', 'tests/test-chronos.json.tmpl'], env={
        'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
        'SHPKPR_CHRONOS_JOB_NAME': 'shpkpr-test-job',
    })

    assert mock_chronos_add.called
    assert result.exit_code == 0


@mock.patch.object(chronos.ChronosClient, 'list')
@mock.patch.object(chronos.ChronosClient, 'add')
def test_set_multiple(mock_chronos_add, mock_chronos_list, runner):
    mock_chronos_list.return_value = []
    mock_chronos_add.return_value = True

    result = runner(
        [
         'cron', 'set',
         '--template', 'tests/test-chronos.json.tmpl',
         '--template', 'tests/test-chronos-2.json.tmpl'
        ],
        env={
            'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
            'SHPKPR_CHRONOS_JOB_NAME': 'shpkpr-test-job',
            'SHPKPR_CHRONOS_JOB_2_NAME': 'shpkpr-test-job-2',
        },
    )

    assert mock_chronos_add.called_twice
    assert result.exit_code == 0


@mock.patch.object(chronos.ChronosClient, 'list')
@mock.patch.object(chronos.ChronosClient, 'update')
@mock.patch.object(chronos.ChronosClient, 'add')
def test_set_update(mock_chronos_add, mock_chronos_update, mock_chronos_list, runner):
    mock_chronos_list.return_value = [{'name': 'shpkpr-test-job'}]
    mock_chronos_update.return_value = True

    result = runner(['cron', 'set', '--template', 'tests/test-chronos.json.tmpl'], env={
        'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
        'SHPKPR_CHRONOS_JOB_NAME': 'shpkpr-test-job',
    })

    mock_chronos_add.assert_not_called()

    assert mock_chronos_update.called
    assert result.exit_code == 0


@mock.patch.object(chronos.ChronosClient, 'delete')
def test_delete(mock_chronos_client, runner):
    mock_chronos_client.return_value = True

    result = runner(["cron", "delete", "test-job"], env={
        'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
    })

    mock_chronos_client.assert_called_with('test-job')
    assert result.exit_code == 0


@mock.patch.object(chronos.ChronosClient, 'delete_tasks')
def test_delete_tasks(mock_chronos_client, runner):
    mock_chronos_client.return_value = True

    result = runner(["cron", "delete-tasks", "test-job"], env={
        'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
    })

    mock_chronos_client.assert_called_with('test-job')
    assert result.exit_code == 0


@mock.patch.object(chronos.ChronosClient, 'run')
def test_run(mock_chronos_client, runner):
    mock_chronos_client.return_value = True

    result = runner(["cron", "run", "test-job"], env={
        'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
    })

    mock_chronos_client.assert_called_with('test-job')
    assert result.exit_code == 0
