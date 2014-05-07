# nbgrader

Description: IPython nbconvert preprocessor for grading notebooks.  
Author: Jessica B. Hamrick (jhamrick@berkeley.edu)

> Currently, this only works with a development version of IPython,
> including pull requests
> [#5639](https://github.com/ipython/ipython/pull/5639) and
> [#5720](https://github.com/ipython/ipython/pull/5720), as the grader
> functionality relies on both being able to execute cells, and being
> able to export to the notebook format.

## Example

This is an
[example assignment](http://nbviewer.ipython.org/github/jhamrick/nbgrader/blob/master/test1.ipynb). Certain
cells have metadata marking them for grading (`"grade": true`). When
run through `nbconvert`, a
[graded version of the notebook](http://nbviewer.ipython.org/github/jhamrick/nbgrader/blob/master/test1_graded.ipynb)
is produced and includes only the cells that were originally marked
for grading, in addition to a few cells at the bottom that load an
autograder magic and report successes/failures.
