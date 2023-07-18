# A silly little FFI "JIT"

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
