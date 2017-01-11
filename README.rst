YAWN: Yet Another Workflow Engine
=================================

YAWN provides a framework for executing a set of shell commands with dependencies
in a distributed manner and on a repeating schedule. Other tools do similar things and
are inspirations for this one; particularly Celery_ and Airflow_.

.. _Celery: http://www.celeryproject.org/
.. _Airflow: https://airflow.incubator.apache.org/

Components
----------

- Webservers provide a user interface.
- Workers schedule and execute tasks.
- A Postgres 9.5+ database stores state.

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

Usage
-----

Create config file (`yawn.cfg`) specifying the Postgres 9.5+ database to connect to::

  DATABASE_HOST=localhost
  DATABASE_PORT=5432
  DATABASE_USER=
  DATABASE_PASSWORD=

Install the package using PIP and run the webserver and worker separately::

  pip install https://github.com/aclowes/yawn
  yawn webserver
  yawn worker

Examples
--------

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
