# test_kwargs.py
def fun1a(**kwargs):
    for key, val in kwargs.items():
        print(f"fun1a: {key}={val}")
    
def fun1(**kwargs):
    print(f"fun1: **kwargs({kwargs}")
    for key, val in kwargs.items():
        print(f"fun1: {key}={val}")
    print("fun1 calling  fun1a(**kwargs)")
    fun1a(**kwargs)
    
kargs = {"key_1": "key_1_val", "key_2": "key_2_val", "key_3": "key_3_val"}
print("\ncall:", 'fun1(a="a_arg", b="b_arg", c="c_arg")')
fun1(a="a_arg", b="b_arg", c="c_arg")
print("\ncall:fun1(**kargs)")
fun1(**kargs)
print("\ncall:fun1(kwargs=kargs)")
fun1(kwargs=kargs)