.PHONY: all grade clean

all: grade

grade: Graded\ Assignment.ipynb
Graded\ Assignment.ipynb: Submitted\ Assignment.ipynb autograder_tests.json ipython_nbconvert_config.py
	ipython nbconvert

clean:
	rm -rf Graded\ Assignment.ipynb
