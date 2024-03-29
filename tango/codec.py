__all__ = ("loads", "dumps")


def loads(fmt, data):
    if fmt.startswith("pickle"):
        import pickle

        loads = pickle.loads
    elif fmt.startswith("json"):
        import json

        loads = json.loads
    else:
        raise TypeError(f"Format '{fmt}' not supported")
    return loads(data)


def dumps(fmt, obj):
    if fmt.startswith("pickle"):
        import pickle

        ret = fmt, pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
        return ret
    elif fmt.startswith("json"):
        import json

        return fmt, json.dumps(obj)
    raise TypeError(f"Format '{fmt}' not supported")
