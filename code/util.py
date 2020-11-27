import operator

def get_key(my_dict, val):
    for key, value in my_dict.items():
        if val == value:
            return key

def combine_dicts(a, b, op=operator.add):
    return dict(a.items() + b.items() +
        [(k, op(a[k], b[k])) for k in set(b) & set(a)])