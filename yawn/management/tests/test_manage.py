from unittest import mock

from yawn import manage


@mock.patch.object(manage, 'execute_from_command_line')
def test_manage(mock_execute):
    manage.main()
    assert mock_execute.called
