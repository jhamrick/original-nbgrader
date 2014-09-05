.PHONY: all release solution clean

all: release solution

release: Assignment.ipynb
Assignment.ipynb: Assignment\ Template.ipynb release_config.py
	ipython nbconvert --config release_config.py

solution: Assignment\ Solution.html
Assignment\ Solution.html: Assignment\ Template.ipynb solutions_config.py
	ipython nbconvert --config solutions_config.py

clean:
	rm -rf Assignment.ipynb
	rm -rf Assignment\ Solution.html
