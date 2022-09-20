from transformer import TYPES

def unwrap_statement(statement):
    if statement['type'] == TYPES['STATEMENT']:
        # a statement should only ever have 1 child
        return statement['statement']

    return statement

# this method handles all the pragmas as well as determining what statements fall under what blocks
def preprocess(tree):
    frontend = []
    backend = []

    active = backend

    def switch_env(env):
        nonlocal active
        if env == "frontend":
            active = frontend
        elif env == "backend":
            active = backend

    for statement in tree:
        unwrapped_statement = unwrap_statement(statement)
        if unwrapped_statement['type'] == TYPES['PRAGMA']:
            pragma = unwrapped_statement['pragma']
            if pragma == 'frontend' or pragma == "backend":
                switch_env(pragma)
        else:
            active.append(statement)

    return {
        "frontend": frontend,
        "backend": backend,
    }