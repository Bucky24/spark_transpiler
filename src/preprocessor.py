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

    context_list = []
    current_context = None

    def append_statement(statement):
        if current_context is None:
            active.append(statement)
        else:
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

        new_statement = None

        if current_context is not None:
            new_statement = {
                "type": TYPES['BLOCK'],
                "statement": current_context['statement'],
                "children": current_context['children'],
            }

        if len(context_list) == 0:
            current_context = None

        if new_statement:
            append_statement(new_statement)

    for statement in tree:
        if current_context is not None:
            if statement['spaces'] <= current_context['spaces']:
                pop_context()
        
        unwrapped_statement = unwrap_statement(statement)
        if unwrapped_statement['type'] == TYPES['PRAGMA']:
            pragma = unwrapped_statement['pragma']
            if pragma == 'frontend' or pragma == "backend":
                switch_env(pragma)
        elif unwrapped_statement['type'] in (TYPES['FOR'], TYPES['FOR_OF']):
            append_context(statement)
        else:
            append_statement(statement)

    pop_context()

    return {
        "frontend": frontend,
        "backend": backend,
    }