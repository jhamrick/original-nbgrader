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
	cp autograder.py $(IPYDIR)/

develop: uninstall
	ln autograder.py $(IPYDIR)/autograder.py

uninstall:
	rm -f $(IPYDIR)/autograder.py
	rm -f $(IPYDIR)/autograder.pyc

examples:
	@PYTHONPATH="$(PWD):$(PYTHONPATH)" make -C examples
