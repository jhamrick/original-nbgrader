.PHONY: help install develop uninstall example
IPYDIR = $(HOME)/.ipython/extensions
PWD = $(shell pwd)

help:
	@echo "Targets (run 'make <target>')"
	@echo "-----------------------------"
	@echo "help      : print this list of targets"
	@echo "install   : copy extension files to standard locations"
	@echo "develop   : hardlink extension files to standard locations"
	@echo "uninstall : remove copied extension files"
	@echo "example   : grade the example notebook in example"

install: uninstall
	cp autograder.py $(IPYDIR)/

develop: uninstall
	ln autograder.py $(IPYDIR)/autograder.py

uninstall:
	rm -f $(IPYDIR)/autograder.py
	rm -f $(IPYDIR)/autograder.pyc

example:
	@PYTHONPATH="$(PWD):$(PYTHONPATH)" make -C example
