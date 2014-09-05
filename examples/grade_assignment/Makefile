.PHONY: all grade

all: grade

grade: Graded\ Assignment.ipynb scores.json
Graded\ Assignment.ipynb scores.json: Submitted\ Assignment.ipynb example_autograder.py autograder_config.py
	ipython nbconvert --config autograder_config
