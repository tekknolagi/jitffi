import ctypes

libtest = ctypes.CDLL("./testlib.so")


# def abi(idx, argtype):
#     if argtype == ctypes.c_int:
#         return ("rdi", "rsi", "rdx", "rcx", "r8", "r9")[idx]
#     raise NotImplementedError(f"unhandled arg type {argtype}")


def errval(ty):
    if ty == ctypes.c_int:
        return "-1"
    if ty == ctypes.py_object:
        return "NULL"
    raise NotImplementedError(f"unhandled arg type {ty}")


def cname(ty):
    if ty.__name__.startswith("c_"):
        return ty.__name__.removeprefix("c_")
    if ty == ctypes.py_object:
        return "PyObject*"
    raise NotImplementedError(f"unhandled type {ty}")


def boxed(ty):
    if ty == ctypes.c_int:
        return ctypes.py_object
    if ty == ctypes.py_object:
        raise RuntimeError("can't re-box PyObject*")
    raise NotImplementedError(f"unhandled type {ty}")


class Jit:
    def __init__(self, fptr, argtypes, restype):
        self.i = 0
        self.code = []
        self.fptr = fptr
        self.argtypes = argtypes
        self.restype = restype

    def emit(self, code: str) -> None:
        self.code.append(code)

    def gensym(self) -> str:
        result = f"v{self.i}"
        self.i += 1
        return result

    def check(self, vreg, ty):
        if ty == ctypes.c_int:
            self.emit(
                f"if ({vreg} == {errval(ty)} && PyErr_Occurred()) return {errval(self.restype)};"
            )
        else:
            self.emit(f"if ({vreg} == {errval(ty)}) return {errval(self.restype)};")

    def unbox(self, reg, ty) -> str:
        if ty == ctypes.c_int:
            vreg = self.gensym()
            self.emit(f"{cname(ty)} {vreg} = PyLong_AsLong({reg});")
            self.check(vreg, ty)
            return vreg
        else:
            raise NotImplementedError(f"unhandled type {ty}")

    def box(self, reg, ty) -> str:
        if ty == ctypes.c_int:
            vreg = self.gensym()
            self.emit(f"{cname(ctypes.py_object)} {vreg} = PyLong_FromLong({reg});")
            self.check(vreg, ctypes.py_object)
            return vreg
        else:
            raise NotImplementedError(f"unhandled type {ty}")

    def jit(self):
        args = []
        for idx, argtype in enumerate(self.argtypes):
            arg = f"arg{idx}"
            args.append(arg)
            self.unbox(arg, argtype)
        unboxed_result = self.gensym()
        self.emit(
            f"{cname(self.restype)} {unboxed_result} = {self.fptr.__name__}({', '.join(args)})"
        )
        result = self.box(unboxed_result, self.restype)
        self.emit(f"return {result};")
        return result

    def __repr__(self):
        result = []
        argtypes = ", ".join(
            f"{cname(boxed(argtype))} arg{idx}"
            for idx, argtype in enumerate(self.argtypes)
        )
        sig = f"{cname(boxed(self.restype))} {self.fptr.__name__}_wrapper({argtypes}) {{"
        result.append(sig)
        for line in self.code:
            result.append("  " + line)
        result.append("}")
        return "\n".join(result)


j = Jit(libtest.add_one, [ctypes.c_int], ctypes.c_int)
j.jit()
print(j)
