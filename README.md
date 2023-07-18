# A silly little FFI "JIT"

Imagine calling the C function `add_one` from Python.

```c
// test.c
extern int add_one(int i) {
    return i+1;
}
```

Normal `ctypes` "interprets" the FFI. Instead, generate code to call it.


```
$ make
int add_one_wrapper(PyObject* arg0) {
  int v0 = PyLong_AsLong(arg0);
  if (v0 == -1 && PyErr_Occurred()) return -1;
  int v1 = add_one(arg0)
  PyObject* v2 = PyLong_FromLong(v1);
  if (v2 == NULL) return -1;
  return v2;
}
$
```
