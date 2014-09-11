.PHONY: all release solution clean

all: release solution

release: Assignment.ipynb
Assignment.ipynb: Assignment\ Template.ipynb ipython_nbconvert_config.py
	ipython nbconvert "$<" --output="$@" --AssignmentPreprocessor.solution=False

solution: Assignment\ Solution.ipynb rubric.json autograder_tests.json
Assignment\ Solution.ipynb rubric.json autograder_tests.json: Assignment\ Template.ipynb ipython_nbconvert_config.py
	ipython nbconvert "$<" --output="$@" --AssignmentPreprocessor.solution=True

clean:
	rm -rf Assignment.ipynb
	rm -rf Assignment\ Solution.ipynb
	rm -rf rubric.json
	rm -rf autograder_tests.json
