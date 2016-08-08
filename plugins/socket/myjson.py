import jsonpickle

def dumps(obj, **args):
    return jsonpickle.encode(obj, unpicklable=False)

def loads(json, **args):
    return jsonpickle.decode(json)