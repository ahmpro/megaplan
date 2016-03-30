Megaplan
========

.. image:: https://travis-ci.org/derfenix/megaplan.svg?branch=master
    :target: https://travis-ci.org/derfenix/megaplan

--

API library for the Megaplan - Russian CRM system

--

Usage
-----

    >>> api = API.configure("account", "login", "password")
    >>> #api = API.configure("account", "login", "password", https=False)  # For http requests instead of https
    >>> # Different ways to call method
    >>> # res = api.call('Employee_Card', Id=10006)
    >>> # res = api('Employee_Card', Id=100006)
    >>> res = api.Employee_Card(Id=100006)
    >>> print(res['employee']['email'])
