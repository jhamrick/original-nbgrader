.PHONY: all grade clean

all: grade

grade: Graded\ Assignment.ipynb scores.json
Graded\ Assignment.ipynb scores.json: Submitted\ Assignment.ipynb example_autograder.py ipython_nbconvert_config.py
	ipython nbconvert

clean:
	rm -rf Graded\ Assignment.ipynb
	rm -rf scores.json
