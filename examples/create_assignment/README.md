# Creating an assignment

This example shows how to use nbgrader to create an assignment. The
master version of the assignment is in the file
[Assignment Template.ipynb](http://nbviewer.ipython.org/github/jhamrick/nbgrader/blob/master/examples/create_assignment/Assignment%20Template.ipynb). I
recommend opening this up in the notebook and using the
[Create Assignment toolbar](../../docs/assignment-toolbar.md) to look
at the metadata associated with each cell.

There is also a
[header notebook](http://nbviewer.ipython.org/github/jhamrick/nbgrader/blob/master/examples/create_assignment/header.ipynb)
which gets prepended to the master notebook when it is converted
either to the solution version or release version.

## Creating the release version

To create the release version, run:

```
make release
```

This will produce
[Assignment.ipynb](http://nbviewer.ipython.org/github/jhamrick/nbgrader/blob/master/examples/create_assignment/Assignment.ipynb),
which is the release version of the notebook.

## Creating the solution version

To create the release version, run:

```
make solution
```

This will produce
[Assignment Solution.ipynb](http://nbviewer.ipython.org/github/jhamrick/nbgrader/blob/master/examples/create_assignment/Assignment%20Solution.ipynb),
which is the release version of the notebook, as well as
[rubric.json](rubric.json), which is a rubric specifying the point
breakdown for each part of the assignment.
