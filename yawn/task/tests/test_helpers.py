from yawn.task.helpers import delay


def some_function(*args):
    pass


class SomeClass:
    pass


def test_quoted_arg():
    task = delay(SomeClass, 'A small "taste" of chaos')
    assert task.template.command == 'yawn exec yawn.task.tests.test_helpers ' \
                                    'SomeClass \'A small "taste" of chaos\''


def test_many_args():
    task = delay(some_function, 'something', '1')
    assert task.template.command == "yawn exec yawn.task.tests.test_helpers " \
                                    "some_function something 1"


def test_deduplication():
    task1 = delay(some_function)
    task2 = delay(some_function)
    assert task1.template_id == task2.template_id


def test_queued():
    task = delay(SomeClass, queue='queue', max_retries=2, timeout=10)
    assert task.message_set.count() == 1
    assert task.message_set.first().queue.name == 'queue'
    assert task.template.max_retries == 2
    assert task.template.timeout == 10
