.PHONY: help install develop examples clean
IPYDIR=$(shell ipython locate)

install:
	python setup.py install
	cp nbgrader/assignment_toolbar.js $(IPYDIR)/nbextensions/assignment.js
	cp nbgrader/assignment_toolbar.css $(IPYDIR)/nbextensions/assignment.css

develop:
	pip install -e .
	ln nbgrader/assignment_toolbar.js $(IPYDIR)/nbextensions/assignment.js
	ln nbgrader/assignment_toolbar.css $(IPYDIR)/nbextensions/assignment.css

examples:
	make -C examples

clean:
	make -C examples clean
	rm -f $(IPYDIR)/nbextensions/assignment.js
	rm -f $(IPYDIR)/nbextensions/assignment.css
