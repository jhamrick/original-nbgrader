.PHONY: help install develop examples clean

install:
	python setup.py install

develop:
	pip install -e .

examples:
	make -C examples

clean:
	make -C examples clean
