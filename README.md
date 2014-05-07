# nbgrader

IPython nbconvert preprocessor for grading notebooks.

> Currently, this only works with a development version of IPython,
> including pull requests
> [#5639](https://github.com/ipython/ipython/pull/5639) and
> [#5720](https://github.com/ipython/ipython/pull/5720), as the grader
> functionality relies on a nbconvert preprocessor for executing
> cells, and being able to then export to the notebook format.

## Overview

IPython notebooks are a great way to distribute combined programming
and written assignments for classes: students can write code in one
cell, and then interpret the results of that code in the
next. However, there is no straightforward way to *grade* those
notebooks, especially because not all code cells should actually be
graded. Thus, `nbgrader` was born: a framework for creating gradable
assignments in the IPython notebook, and then grading them.

There are two main features of `nbgrader`: an IPython extension magic,
and a nbconvert preprocessor:

* `autograder` extension magic: this provides a cell magic,
  `%%autograde` which will execute grading code in the cell using
  `nose`.
* `nbgrader.Grader` preprocessor: this is a nbconvert preprocessor
  which extracts cells marked for grading, runs them, and then grades
  them using the autograde magic.

## Example

This is an
[example assignment](http://nbviewer.ipython.org/github/jhamrick/nbgrader/blob/master/example/test1.ipynb). Certain
cells have metadata marking them for grading (`"grade": true`). When
run through `nbconvert`, a
[graded version of the notebook](http://nbviewer.ipython.org/github/jhamrick/nbgrader/blob/master/example/test1_graded.ipynb)
is produced and includes only the cells that were originally marked
for grading, in addition to a few cells at the bottom that load the
autograder magic and report successes/failures.

## Installing

Typing `make install` will copy `autograder.py` to your IPython
extensions directory (probably `~/.ipython/extensions`). You will
additionally need to include `nbgrader.py` somewhere on your
`PYTHONPATH`, i.e.:

```
export PYTHONPATH="/path/to/nbgrader.py:$PYTHONPATH"
```

## Magic usage

To use the autograde magic, you need to first load the extension with
`%load_ext autograder`. Then, create a cell with `%%autograde` at the
top, and [nose](https://nose.readthedocs.org/en/latest/) tests within
the cell. There are a few differences from standard `nose`:

1. Tests should be prefixed with "grade" or "Grade" rather than "test"
   or "Test".
2. You can decorate tests with `score`, which takes two arguments: the
   problem name, and the number of points it is worth. If the test
   passes, then those points are earned, otherwise, they are not. So,
   as the tests are run, points earned for each problem will be
   tracked and then reported after the grading is completed.

Here is an example:

```
%%autograde

@score(problem="problem1", score=1.0)
def grade_problem1():
    ... grading code here ...

@score(problem="problem1", score=0.5)
def grade_problem1_differently():
    ... more grading code here ...
```

## Preprocessor usage

The preprocessor does several things:

1. Extracts cells from the given notebook that are marked for grading
   (see [Creating an assignment](#Creating-an-assignment)).
2. Reads in grading code from a given file (specified via the
   `c.Grader.autograder` traitlet).
3. Adds new cells at the bottom of the notebook to load the
   `autograder` extension and to use the autograde magic along with
   the grading code loaded above.
4. Runs all cells, and saves the output.
5. Saves out the new notebook.

To run the preprocessor, create a file called
`ipython_nbconvert_config.py` in the same directory as your
notebook. See
[example/ipython_nbconvert_config.py](example/ipython_nbconvert_config.py)
for an example. Then, run `ipython nbconvert` at the command line.

### Creating an assignment

Technically, any IPython notebook is a valid assignment. However, to
actually grade that assignment, cells of the notebook must be marked
with special metadata.

1. In the IPython notebook, choose "Edit Metadata" from the "Cell
Toolbar" dropdown menu. Buttons at the top right of the cells will
appear. Note that they may not immediately appear for markdown or
header cells: go into edit mode for these cells, and you should then
see the button appear.

2. Click the "Edit Metadata" button for the cell you wish to be
gradable, and a dialogue will appear where you can edit the
metadata.

3. Add `"grade": true`, such that the metadata looks something like
this:

```
{
  "grade": true
}
```
