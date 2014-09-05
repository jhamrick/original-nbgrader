.PHONY: all release solution

all: release solution

release: Assignment.ipynb
Assignment.ipynb: Assignment\ Template.ipynb release_config.py
	ipython nbconvert --config release_config.py

solution: Assignment\ Solution.ipynb
Assignment\ Solution.ipynb: Assignment\ Template.ipynb solutions_config.py
	ipython nbconvert --config solutions_config.py
