import datetime
import pytest

from .. import cron


@pytest.mark.parametrize('expression,expected', [
    ('*', list(range(7))),
    ('1-3', [1, 2, 3]),
    ('*/2', [0, 2, 4, 6]),
    ('2-5/2', [2, 4]),
    ('1,*/6', [0, 1, 6]),
])
def test_parse_valid(expression, expected):
    assert cron.parse(expression, 7) == expected


@pytest.mark.parametrize('expression', [
    '*-1', '1-', '-1',  # invalid range
    '2a',  # invalid integer
    '7',  # out of range
    '/2', '2/',  # empty numerator/denominator
    '2,',  # empty part
    '5/7,',  # no values
])
def test_parse_invalid(expression):
    with pytest.raises(ValueError):
        cron.parse(expression, 7)


@pytest.mark.parametrize('current_time,next_run', [
    # there is a run this hour
    (datetime.datetime(2016, 11, 28, 4, 15), datetime.datetime(2016, 11, 28, 4, 30)),
    # there is a run today
    (datetime.datetime(2016, 11, 28, 4, 59), datetime.datetime(2016, 11, 28, 5, 0)),
    # there is a run on another day
    (datetime.datetime(2016, 11, 28, 5, 59), datetime.datetime(2016, 11, 29, 2, 0)),
])
def test_cron_next_run(current_time, next_run):
    tab = cron.Crontab('*/15 2-5 1,2')
    assert tab.next_run(current_time) == next_run
