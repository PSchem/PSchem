PSchem
======

Pschem is an opensource and scriptable electronics schematics editor.
It's built on top of an open design database and uses Python for both
the implementation and user scripts.

Project Resources
-----------------

* [Project Page](https://github.com/PSchem/PSchem)
* [Wiki and Documentation](https://github.com/PSchem/PSchem/wiki).
* [Mailing List](http://groups.google.com/group/pschem).
* Public Git repository: git://github.com/PSchem/PSchem.git (read-only).

Supported Platforms
-------------------

* Windows
* Linux
* Other supported by the [Qt library](http://qt.nokia.com/) (not tested)

License
-------

PSchem is a copyrighted software. Please check `CONTRIBUTORS` file for
the list of authors.

You may use the program and its source code provided you comply with
terms of following licenses:

* GPL v3 - GUI, everything that uses Qt library (PSchem directory)
* LGPL v3 - Database backend (Database directory)
* other opensource licenses - third party code distributed together
  with Pschem (Thirdparty directory) 

PSchem is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.


Contributing
------------

* Contact us via the mailing list.
* Fix or update the wiki.
* Fork the repository and keep us informed about the changes. 

Installation
------------

Installation is not supported yet. For now, please run the program from
its directory.

To run the program you will need following components:

* [Python v2.6 or 2.7](http://python.org/) (v3 is not supported yet)
* [Qt v4.6 or higher](http://qt.nokia.com/)
* [PySide v1.0](http://www.pyside.org/) or
  [PyQt v4.6 or higher](http://www.riverbankcomputing.co.uk/software/pyqt/intro).

Usage
-----

*Note*: PSchem is in a very early stage of development.
It is not yet suitable for use in the electronic circuit design.

Use provided batch files or run the program directly:

    $ python pschem.py

There are no electronic component libraries available yet so you may want
to reuse some of [gEDA](http://www.gpleda.org/) designs.

*Note*: PSchem is not related to the gEDA project. Please do not report
problems with PSchem on the gEDA mailing list or issue trackers.
