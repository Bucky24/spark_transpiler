from transformer import TYPES

# turn to true for debug logs
LOG = False

def log(str):
    if LOG:
        print(str)

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

    context_list = []
    current_context = None

    def append_statement(statement):
        if current_context is None:
            active.append(statement)
        else:
            log("Appending " + statement['type'] + " to context")
            current_context['children'].append(statement)

    def append_context(statement):
        nonlocal current_context

        if current_context is not None:
            context_list.append(current_context)
        
        current_context = {
            "statement": statement,
            "spaces": statement["spaces"],
            "children": [],
        }

    def switch_env(env):
        nonlocal active
        if env == "frontend":
            active = frontend
        elif env == "backend":
            active = backend

    def pop_context():
        nonlocal current_context
        
        log("popping context")

        new_statement = None

        if current_context is not None:
            new_statement = {
                "type": TYPES['BLOCK'],
                "statement": current_context['statement'],
                "children": current_context['children'],
            }

        if len(context_list) == 0:
            current_context = None
        else:
            current_context = context_list.pop()

        if new_statement:
            append_statement(new_statement)

    for statement in tree:
        unwrapped_statement = unwrap_statement(statement)
        log("Proccessing " + unwrapped_statement['type'] + " context? " + ("empty" if current_context is None else "set"))

        if current_context is not None:
            if statement['spaces'] <= current_context['spaces']:
                pop_context()

        if unwrapped_statement['type'] == TYPES['PRAGMA']:
            pragma = unwrapped_statement['pragma']
            if pragma == 'frontend' or pragma == "backend":
                switch_env(pragma)
        elif unwrapped_statement['type'] in (TYPES['FOR'], TYPES['FOR_OF'], TYPES['IF'], TYPES['WHILE']):
            append_context(statement)
        else:
            append_statement(statement)
    pop_context()

    return {
        "frontend": frontend,
        "backend": backend,
    }