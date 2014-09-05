# nbgrader

IPython nbconvert preprocessor for grading notebooks.

Author: Jessica B. Hamrick

> Currently (as of 09/04/2014), this only works with a development
> version of IPython, as the grader functionality relies on a
> nbconvert preprocessor for executing cells, and being able to then
> export to the notebook format.

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

* `autograder` extension magic: this provides a line magic, `%grade
  <problem>` which will execute all tests that have been marked as
  tests for the problem with name `<problem>`.
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

To use the autograde magic, you need to do several things: write
tests, and then run the magic.

### Writing grading scripts

First, create a python file with
[nose](https://nose.readthedocs.org/en/latest/) tests for the problems
you want to grade. There are two important ways the tests must be written:

1. The name of each test must begin with "grade" or "Grade".
2. Each test must be decorated with a `@score` decorator, which takes
   as arguments the name of the problem that the test corresponds to,
   and the number of points that it is worth.

Additionally, if you are using the magic in coordination with the
nbconvert preprocessor, you should use problem names that correspond
to the headings that they are nested beneath.

See [example tests](example/test1_autograder.py) for grading the
[example assignment](http://nbviewer.ipython.org/github/jhamrick/nbgrader/blob/master/example/test1.ipynb).

### Using the magic

Once the tests are written, there are three steps you must take. If
you are using the nbconvert preprocessor, these will be done for you
automatically, otherwise you must do them manually:

1. Load the extension with `%load_ext autograder`, and load the file
   with your nose tests with `%load_autograder my_autograder.py`,
   where `my_autograder.py` is the filename of the file with the tests
   in it.
2. Run any cells containing code to be tested.
3. Create a new cell, and use the line magic as `%grade <problem>`,
   where `<problem>` is the name of the problem you want to
   grade. Messages will be displayed indicating which tests are being
   run, and then a table will be shown that indicates the number of
   points earned.

## Preprocessor usage

The preprocessor does several things:

1. Extracts cells from the given notebook that are marked for grading
   (see [Creating an assignment](#Creating-an-assignment)).
2. Reads in grading code from a given file (specified via the
   `c.Grader.autograder_file` traitlet).
3. Adds new cells at the bottom of the notebook to load the
   `autograder` extension and to use the autograde magic along with
   the grading code loaded above.
4. Runs all cells, and updates the notebook with the output.
5. Optionally saves out the scores to a file (specified via the
   `c.Grader.scores_file` traitlet).
6. Saves out the new notebook.

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
