.PHONY: all release solution clean

all: release solution

release: Assignment.ipynb
Assignment.ipynb: Assignment\ Template.ipynb ipython_nbconvert_config.py
	ipython nbconvert "$<" --output="$@" --AssignmentPreprocessor.solution=False --AssignmentWriter.save_rubric=False

solution: Assignment\ Solution.ipynb rubric.json
Assignment\ Solution.ipynb rubric.json: Assignment\ Template.ipynb ipython_nbconvert_config.py
	ipython nbconvert "$<" --output="$@" --AssignmentPreprocessor.solution=True --AssignmentWriter.save_rubric=True

clean:
	rm -rf Assignment.ipynb
	rm -rf Assignment\ Solution.ipynb
	rm -rf rubric.json
