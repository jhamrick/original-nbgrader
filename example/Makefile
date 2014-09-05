.PHONY: all release solution grade

all: release solution grade

release: Assignment.ipynb
Assignment.ipynb: Assignment\ Template.ipynb release_config.py
	ipython nbconvert --config release_config.py

solution: Assignment\ Solution.ipynb
Assignment\ Solution.ipynb: Assignment\ Template.ipynb solutions_config.py
	ipython nbconvert --config solutions_config.py

grade: Graded\ Assignment.ipynb scores.json
Graded\ Assignment.ipynb scores.json: Submitted\ Assignment.ipynb example_autograder.py autograder_config.py
	ipython nbconvert --config autograder_config
