# Creating an assignment

Often, instructors will want to create a *release* version of an
assignment, and a *solutions* version -- one which will be given to
students to complete, and one which will be given out only after
students have submitted their completed assignments. This creates a
problem for instructors who want to keep the release version and the
solution version synchronized.

One remedy for this problem is to have one master version -- a
"template" version -- which is then converted to either a release
version or a solution version.

## Master Version

In this example, the master version is in the file
[Assignment Template.ipynb](http://nbviewer.ipython.org/github/jhamrick/nbgrader/blob/master/examples/create_assignment/Assignment
Template.ipynb). By default, everything in the master version will go
in both the release version and in the solutions version. Exceptions
can be made using the following syntax:

```
{% if solution %}
solution text/code goes here
(any number of lines is fine)
{% else %}
whatever default text/code or prompt you want to display in the
release version goes here
{% endif %}
```

## Release Version

At the command line, run:

```
ipython nbconvert --config release_config.py
```

This will produce a new notebook called
[Assignment.ipynb](http://nbviewer.ipython.org/github/jhamrick/nbgrader/blob/master/examples/create_assignment/Assignment.ipynb)
which only includes the release parts of the master version.

## Solutions Version

At the command line, run:

```
ipython nbconvert --config solutions_config.py
```

This will produce an HTML file called
[Assignment Solution.html](Assignment Solution.html) which only
includes the solution parts of the master version. In addition, it
specifically highlights cells for written answers, to make them stand
out from the rest of the assignment.
