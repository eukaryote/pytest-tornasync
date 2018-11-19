Changes
=======

0.6.0 (2018-11-19)
------------------

 - minor updates to avoid a pytest warning under pytest 4
 - repo switch to using a 'src' dir


0.5.0 (2018-05-28)
------------------

 - updated to work with Tornado 5, which is now the minimum required version
 - require pytest >= 3.0
 - the `io_loop` fixture always refers to a `tornado.ioloop.IOLoop instance` now
 - the `io_loop_asyncio` and `io_loop_tornado` fixtures have been removed, since
   now that Tornado 5 always uses asyncio under Python 3, there would be no
   difference between the two fixtures, so `io_loop` is all that is needed
 - tox tests now test more versions of Tornado (5.0.* and latest 5.*),
   Pytest (3.0.* and latest 3.*), and Python (3.5, 3.6, 3.7, and pypy3).
