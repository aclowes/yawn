YAWN: Yet Another Workflow Engine
=================================

YAWN provides a framework for executing a set of shell commands with dependencies
in a distributed manner and on a repeating schedule. Other tools do similar things and
are inspirations for this one; particularly Celery_ and Airflow_.

.. _Celery: http://www.celeryproject.org/
.. _Airflow: https://airflow.incubator.apache.org/

Principles
----------

What is different from existing tools and why?

Code separation
  YAWN runs your commands as sub-processes, so there is no co-mingling of your python code
  with the YAWN code. You are responsible for how your code is released and what version of your
  code gets run.

State separation
  Environment variables are the only state that can be passed to your commands. Your application
  should key off just a date or record ID and get more complex state from its data sources.

Versioning
  The workflow configuration and every run is versioned, so you have a complete history.

Broker
  YAWN uses Postgres to store internal state and as a message queue. Using only Postgres allows
  for simple setup and configuration. YAWN uses the new ``SELECT ... FOR UPDATE SKIP LOCKED``
  statement to efficiently select from the queue table.

Components
----------

Web Servers
  The website provides a user interface to view the workflows and tasks running within them.
  It allows you to run an existing workflow or re-run a failed task. The web server also provides
  a REST API to programatically create and run workflows.

Workers
  The worker schedules and executes tasks. The worker uses ``subprocess.Popen`` to run tasks and
  capture stdout and stderr.

Concepts
--------

Workflow
  A set of Tasks that can depend on each other, forming what is popularly known as a directed
  acyclic graph (DAG). Workflows can be scheduled to run on a regular basis and they are versioned
  so they can change over time.

Run
  A manually triggered or scheduled run of a Workflow.

Task
  A shell command that specifies the upstream tasks it depends on, the number times to retry, and a
  timeout. The task is given environment variables configured in the workflow and run.

Execution
  A single execution of a Task's command, capturing the exit code and standard output and error.

Queue
  A first-in, first-out list of Tasks to execute.

Worker
  A process that reads from a set of Queues and executes the associated Tasks, recording the
  results in an Execution.

Examples
--------

Run ``yawn examples`` to populate two workflows into the database.

Here is a screenshot of the page for a single workflow:

.. image:: https://cloud.githubusercontent.com/assets/910316/21969288/fe40baf0-db51-11e6-97f2-7e6875c1e575.png

REST API
--------

Browse the API by going to http://127.0.0.1:8000/api/ in a browser.

When creating a workflow, the format is (shown as YAML for readability)::

    name: Example
    parameters:
      ENVIRONMENT: production
      CALCULATION_DATE: 2017-01-01
    schedule: 0 0 *
    schedule_active: True

    tasks:
    - name: task_1
      queue: default
      max_retries: 1
      timeout: 30
      command: python my_awesome_program.py $ENVIRONMENT
    - name: task_2
      queue: default
      command: echo $CALCULATION_DATE | grep 2017
      upstream:
      - task_1

``/api/workflows/``
  GET a list of versions or a single workflow version. POST to create or update a workflow
  using the schema show above. PATCH to change the ``schedule``, ``schedule_active``, or
  ``parameters`` fields only.

  * POST - use the schema shown above
  * PATCH ``{"schedule_active": false}``

``/api/runs/``
  GET a list of runs, optionally filtering to a particular workflow using ``?workflow=<id>``.
  POST to create a new run. PATCH to change the parameters.

  * POST ``{"workflow_id": 1, "parameters": null}``
  * PATCH ``{"parameters": {"ENVIRONMENT": "test"}}``

``/api/tasks/<id>/``
  GET a single task from a workflow run, and its executions with their status and logging
  information. PATCH to enqueue a task or kill a running execution.

  * PATCH ``{"enqueue": true}``
  * PATCH ``{"terminate": <execution_id>}``

Python API
----------

Import and use the Django models to create your workflow::

    from yawn.workflow.models import WorkflowName
    from yawn.task.models import Template

    name, _ = WorkflowName.objects.get_or_create(name='Simple Workflow Example')
    workflow = name.new_version(parameters={'MY_OBJECT_ID': '1', 'SOME_SETTING': 'false'})
    task1 = Template.objects.create(workflow=workflow, name='start', command='echo Starting...')
    task2 = Template.objects.create(workflow=workflow, name='task2', command='echo Working on $MY_OBJECT_ID')
    task2.upstream.add(task1)
    task3 = Template.objects.create(workflow=workflow, name='task3',
                                    command='echo Another busy thing && sleep 20')
    task3.upstream.add(task1)
    task4 = Template.objects.create(workflow=workflow, name='done', command='echo Finished!')
    task4.upstream.add(task2, task3)

    workflow.submit_run(parameters={'child': 'true'})

Alternatively, use the serializer to give tasks as a dictionary in the format used
by the API. This method checks if a version of the Workflow exists with the same structure,
and will return the existing version if so::

    from yawn.workflow.serializers import WorkflowSerializer

    serializer = WorkflowSerializer(data=test_views.data())
    serializer.is_valid(raise_exception=True)
    workflow = serializer.save()
    workflow.submit_run()

Contributing
------------

To develop on YAWN, fork the repository and checkout a local copy::

  git clone https://github.com/<you>/yawn

Install the backend Django_ dependencies and run its server. Your database should be at
``postgres://localhost:5432/yawn`` by default. The ``yawn`` command is a wrapper on Django's
``manage.py``::

  pip install -e .[test]
  createdb yawn
  yawn migrate
  yawn runserver

Install the frontend create-react-app_ dependencies and run its server::

  cd frontend
  npm install
  npm start

Run the tests::

  pytest
  npm test

Load some examples and run the worker to process them::

  yawn examples
  yawn worker

.. _create-react-app: https://github.com/facebookincubator/create-react-app
.. _Django: https://airflow.incubator.apache.org/


