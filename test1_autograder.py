@score("hello", 1.0)
def grade_hello():
    """Example passing test"""
    msg = hello("Jessica")
    assert msg == "Hello, Jessica!"

@score("hello", 1.0)
def grade_hello2():
    """Example failing test"""
    msg = hello("Jesica")
    assert msg == "Hello, Jessica!"
