Contributing
============

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
  yarn install
  yarn start

Run the tests::

  pytest
  yarn test

Load some examples and run the worker to process them::

  yawn examples
  yawn worker

.. _create-react-app: https://github.com/facebookincubator/create-react-app
.. _Django: https://www.djangoproject.com/

Best Practices
--------------

* Write tests and keep coverage > 80%
* Submit a pull requests
* Get acknowledged in the changelog

Documentation
-------------

The README is in reStructuredText so it appears correctly on both GitHub and PyPI.
Read about reStructuredText_ and the `components in common`_ between it and Markdown.

.. _reStructuredText: http://docutils.sourceforge.net/docs/user/rst/quickref.html
.. _components in common: https://gist.github.com/dupuy/1855764

Debugging Javascript Tests
--------------------------

To open a CLI debugger inside a JS test, add the line ``debugger;`` inside a test
and run the following command to enter the debugger, where ``App.test.js`` specifies
the test to run::

  CI=1 node debug node_modules/react-scripts/scripts/test.js --runInBand --em src/tests/App.test.js

Making a Release
----------------

Tag the release_ on GitHub, naming it in the ``v0.0.0`` format. Increment the version in
``setup.py`` to match.

.. _release: https://github.com/aclowes/yawn/releases/new

Build the frontend code, then bundle and release a source tarball. Finally, test
installing it before uploading to the production PyPI server::

  (cd frontend/ && yarn build)
  ./setup.py sdist upload -r https://test.pypi.org/legacy/
  pip install -i https://testpypi.python.org/pypi yawns

  ./setup.py sdist upload -r https://upload.pypi.org/legacy/

