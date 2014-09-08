.PHONY: all release solution clean

all: release solution

release: Assignment.ipynb
Assignment.ipynb: Assignment\ Template.ipynb ipython_nbconvert_config.py
	ipython nbconvert "$<" --output="$@" --ReleasePreprocessor.solution=False

solution: Assignment\ Solution.ipynb
Assignment\ Solution.ipynb: Assignment\ Template.ipynb ipython_nbconvert_config.py
	ipython nbconvert "$<" --output="$@" --ReleasePreprocessor.solution=True

clean:
	rm -rf Assignment.ipynb
	rm -rf Assignment\ Solution.ipynb
