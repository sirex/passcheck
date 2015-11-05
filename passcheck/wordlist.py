import os.path


def load(path, required=False):
    if required or os.path.exists(path):
        with open(path) as f:
            return {w.strip().lower().encode(): i for i, w in enumerate(f, 1)}
    else:
        return {}
