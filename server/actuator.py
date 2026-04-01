from RestrictedPython import compile_restricted, safe_globals
from RestrictedPython.Eval import default_guarded_getitem, default_guarded_getiter
from RestrictedPython.Guards import full_write_guard

SAFE_BUILTINS = {
    **safe_globals,
    "_getitem_": default_guarded_getitem,
    "_getiter_": default_guarded_getiter,
    "_write_": full_write_guard,
}


def build_tool_globals(extra_funcs: dict):
    g = SAFE_BUILTINS.copy()
    g.update(extra_funcs)
    return g


def run_restricted(code: str, arguments: dict, extra_funcs: dict):
    byte_code = compile_restricted(code, "<tool>", "exec")

    globals_dict = build_tool_globals(extra_funcs)
    locals_dict = {}

    exec(byte_code, globals_dict, locals_dict)

    run_func = locals_dict.get("run")
    if run_func is None:
        raise ValueError("The 'run' function is not defined")

    # ⚠️ 永远同步执行
    return run_func(**arguments)
