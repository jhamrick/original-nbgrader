.PHONY: help install develop uninstall examples
IPYDIR = $(HOME)/.ipython/extensions
PWD = $(shell pwd)

help:
	@echo "Targets (run 'make <target>')"
	@echo "-----------------------------"
	@echo "help      : print this list of targets"
	@echo "install   : copy extension files to standard locations"
	@echo "develop   : hardlink extension files to standard locations"
	@echo "uninstall : remove copied extension files"
	@echo "examples  : generate and grade the example notebook in the examples"

install: uninstall
	cp nbgrader_magic.py $(IPYDIR)/nbgrader.py

develop: uninstall
	ln nbgrader_magic.py $(IPYDIR)/nbgrader.py

uninstall:
	rm -f $(IPYDIR)/nbgrader.py
	rm -f $(IPYDIR)/nbgrader.pyc

examples:
	@PYTHONPATH="$(PWD):$(PYTHONPATH)" make -C examples
