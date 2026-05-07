"""
===
App
===

:Author: Reuven Mol

a Dash app to run the simulation
"""

from north.webapp.north_app import app


if __name__ == "__main__":
    app.run(debug=True)
