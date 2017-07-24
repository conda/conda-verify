def error(filepath, code, message):
    """"""
    return '{}: {}: {}' .format(filepath, code, message)


C100 = error('./meta.yaml', 'C100', 'something')

print(C100)