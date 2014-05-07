from nose.tools import eq_ as assert_eq

@score(problem="hello", points=0.5)
def grade_hello1():
    """Grade 'hello' with input 'Jessica'"""
    msg = hello("Jessica")
    assert_eq(msg, "Hello, Jessica!")

@score(problem="hello", points=0.5)
def grade_hello2():
    """Grade 'hello' with input 'Python'"""
    msg = hello("Python")
    assert_eq(msg, "Hello, Python!")

@score(problem="goodbye", points=0.5)
def grade_goodbye1():
    """Grade 'goodbye' with input 'Jessica'"""
    msg = goodbye("Jessica")
    assert_eq(msg, "Goodbye, Jessica")

@score(problem="goodbye", points=0.5)
def grade_goodbye2():
    """Grade 'goodbye' with input 'Python'"""
    msg = goodbye("Python")
    assert_eq(msg, "Goodbye, Python")
