import traceback

def exception_str(e):
    return str(type(e)) + ": " + str(e) + "\n" + '\n'.join(traceback.format_tb(e.__traceback__))
