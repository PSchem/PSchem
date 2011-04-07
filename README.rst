======
PSchem
======

Pschem is an opensource and scriptable electronics schematics editor.
It's built on top of an open design database and uses Python for both
the implementation and user scripts.

Project Resources
=================

:Project Page: https://github.com/PSchem/PSchem
:Wiki: https://github.com/PSchem/PSchem/wiki
:Mailing List: http://groups.google.com/group/pschem
:Git: git://github.com/PSchem/PSchem.git (read-only)

Supported Platforms
===================

* Windows
* Linux
* Other supported by the `Qt library`_ (not tested)

.. _`Qt library`: http://qt.nokia.com/

License
=======

PSchem is a copyrighted software. Please check ``CONTRIBUTORS`` file for
the list of authors.

You may use the program and its source code provided you comply with
terms of following licenses:

* `GPL v3`_ - GUI, everything that uses Qt library (``PSchem`` directory)
* `LGPL v3`_ - Database backend (``Database`` directory)
* other opensource licenses - third party code distributed together
  with Pschem (``Thirdparty`` directory) 

.. _`GPL v3`: http://www.gnu.org/licenses/gpl-3.0.html
.. _`LGPL v3`: http://www.gnu.org/licenses/lgpl-3.0.html

::

  PSchem is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

Contributing
============

* Contact us via the mailing list
* Fix or update the wiki
* Fork the repository and keep us informed about the changes

Installation
============

Installation is not supported yet. For now, please run the program from
its directory.

To run the program you will need following components:

* Python_, v2.6 or 2.7 (v3 is not supported yet)
* Qt_, v4.6 or higher
* PySide_, v1.0 or
  PyQt_, v4.6 or higher

.. _Python: http://python.org/
.. _Qt: http://qt.nokia.com/
.. _PySide: http://www.pyside.org/
.. _PyQt: http://www.riverbankcomputing.co.uk/software/pyqt/intro

Usage
=====

**Note**
  PSchem is in a very early stage of development.
  It is not yet suitable for the design of electronic circuits.

Use provided batch files or run the program directly::

$ python pschem.py

There are no electronic component libraries available yet so you may want
to reuse some of gEDA_ [#]_ designs.

.. _gEDA: http://www.gpleda.org/

.. [#] PSchem is not related to the gEDA project. Please do not report
       problems with PSchem on the gEDA mailing list or issue trackers.
