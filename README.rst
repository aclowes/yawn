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
  YAWN is separate from your code. You are responsible for how your code is released
  and what version of your code gets run.

State
  YAWN makes it hard to give state to your workflows and tasks. Your application
  is responsible for getting the inputs and saving the results of your tasks.
  The only inputs to a task that differentiate it from another run are the
  environment variables you give it. You can use the builtin YAWN_WORKFLOW_RUN_ID
  or a custom date or record id to work with.

Versioning
  The workflow is versioned, so you know what tasks were in each workflow run.

Stack
  YAWN combines the message queue and internal state into a single relational
  database, so its easier to reason about what is happening. It uses the new
  `SELECT ... FOR UPDATE SKIP LOCKED` statement to efficiently select from the queue
  table.

Components
----------

- Web server provides a user interface.
- Worker schedules and executes tasks.
- Postgres 9.5+ database stores state.

Concepts
--------

Workflow
  A set of Tasks that can depend on each other, forming what
  is popularly known as a directed acyclic graph (DAG). Workflows can be scheduled
  to run on a regular basis. Workflows are versioned so they can change over time.

Task
  A shell command that specifies the number of retries and a timeout. Belongs to a
  Workflow.

Workflow Run
  A manually triggered or scheduled run of a Workflow.

Queue
  A first-in, first-out list of Tasks to execute.

Worker
  Executes Tasks that it finds on a set of Queues, recording the results in an
  Execution.

Execution
  A single run of a Task, capturing the exit code and standard output
  and error.

Examples
--------

![Workflow screenshot](
https://cloud.githubusercontent.com/assets/910316/21969288/fe40baf0-db51-11e6-97f2-7e6875c1e575.png)

Contributing
------------

To develop on YAWN, fork the repository and checkout a local copy::

  git clone https://github.com/<you>/yawn

Install the backend Django_ dependencies and run its server::

  pip install -e .[test]
  ./manage.py runserver

Install the frontend create-react-app_ dependencies and run its server::

  cd frontend
  npm install
  npm start

Run the tests::

  pytest
  npm test

.. _create-react-app: https://github.com/facebookincubator/create-react-app
.. _Django: https://airflow.incubator.apache.org/

TODO
----

- WSGI + static file server wrapped in a ``yawn webserver`` command
- Config file for database connection, etc
