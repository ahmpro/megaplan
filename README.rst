Megaplan
========
--

API library

--

Usage
-----

    >>> api = API.configure("login", "password")
    >>> commerce_ml_document = "...."
    >>> # Different ways to call method
    >>> # res = api.call('deal_createFromOnlineStore', commerce_ml_docuent)
    >>> # res = api('deal_createFromOnlineStore', commerce_ml_docuent)
    >>> res = api.deal_createFromOnlineStore(commerce_ml_docuent)
    >>> for deal in res['Deals']:
    >>>     print deal['id']

