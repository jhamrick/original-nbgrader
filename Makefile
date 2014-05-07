.PHONY: install example
IPYDIR = $(HOME)/.ipython/extensions

install:
	cp autograder.py $(IPYDIR)/

develop:
	rm -f $(IPYDIR)/autograder.py
	ln autograder.py $(IPYDIR)/autograder.py

example:
	make -C example
