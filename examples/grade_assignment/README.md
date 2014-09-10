# Grading an assignment

This example shows how to use nbgrader to create an assignment *that
was also generated using nbgrader*.

First, the submitted version of the assignment is in the file
[Submitted Assignment.ipynb](http://nbviewer.ipython.org/github/jhamrick/nbgrader/blob/master/examples/grade_assignment/Submitted%20Assignment.ipynb).

To grade this assignment, run:

```
make
```

This will produce
[Graded Assignment.ipynb](http://nbviewer.ipython.org/github/jhamrick/nbgrader/blob/master/examples/grade_assignment/Graded%20Assignment.ipynb),
which is a version of the notebook including autograding tests
(sourced from [autograder_tests.json](autograder_tests.json), which
was produced by nbgrader when the assignment was created).

For each test, the output is printed, along with the number of points
earned. If the test failed, then no points were earned, if it passed,
full points are earned.
