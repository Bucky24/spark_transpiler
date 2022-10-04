from transformer import TYPES
from constants import FUNCTION_IMPORTS, CLASS_IMPORTS

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
    env = "backend"

    context_list = []
    current_context = None

    def append_statement(statement):
        if current_context is None:
            active.append(statement)
        else:
            log("Appending " + statement['type'] + " to context for env " + env)
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

    def switch_env(new_env):
        nonlocal active
        pop_all_context()
        env = new_env
        log("changing env to " + env)
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

    def pop_all_context():
        while current_context is not None:
            pop_context()

    for statement in tree:
        unwrapped_statement = unwrap_statement(statement)
        log("Processing " + unwrapped_statement['type'] + " context? " + ("empty" if current_context is None else "set"))

        if current_context is not None:
            if statement['spaces'] <= current_context['spaces']:
                pop_context()

        if unwrapped_statement['type'] == TYPES['PRAGMA']:
            pragma = unwrapped_statement['pragma']
            if pragma == 'frontend' or pragma == "backend":
                switch_env(pragma)
        elif unwrapped_statement['type'] in (TYPES['FOR'], TYPES['FOR_OF'], TYPES['IF'], TYPES['WHILE'], TYPES['FUNCTION'], TYPES['CLASS']):
            append_context(statement)
        else:
            append_statement(statement)
    pop_all_context()

    # now that we have them all in nice groups, let's figure out what imports we need
    imports = {
        "frontend": {},
        "backend": {},
    }
    class_imports = {
        "frontend": {},
        "backend": {},
    }

    def process_code(code, env):
        if not isinstance(code, list):
            code = [code]

        def add_import(function_name):
            add_function_import(function_name)
            add_class_import(function_name)

        def add_function_import(function_name):
            if function_name not in FUNCTION_IMPORTS:
                return
            
            new_import = FUNCTION_IMPORTS[function_name]
            existing_list = imports[env]
            if new_import not in existing_list:
                existing_list[new_import] = []

            if function_name not in existing_list[new_import]:
                existing_list[new_import].append(function_name)

        def add_class_import(class_name):
            if class_name not in CLASS_IMPORTS:
                return
            
            new_import = CLASS_IMPORTS[class_name]
            existing_list = class_imports[env]
            if new_import not in existing_list:
                existing_list[new_import] = []

            if class_name not in existing_list[new_import]:
                existing_list[new_import].append(class_name)
        
        for item in code:
            log("Import processing: " + item['type'])

            if item['type'] == TYPES['BLOCK']:
                process_code(item['children'], env)
            elif item['type'] == TYPES['STATEMENT']:
                if isinstance(item['statement'], dict):
                    process_code(item['statement'], env)
            elif item['type'] == TYPES['CALL_FUNC']:
                process_code(item['function'], env)
                process_code(item['parameters'], env)
            elif item['type'] == TYPES['FUNCTION_NAME']:
                unwrapped = unwrap_statement(item['name'])
                if isinstance(unwrapped, str):
                    add_import(unwrapped)
            elif item['type'] == TYPES['VARIABLE_ASSIGNMENT']:
                process_code(item['value'], env)

    process_code(frontend, "frontend")
    process_code(backend, "backend")

    return {
        "frontend": frontend,
        "backend": backend,
        "frontend_function_imports": imports['frontend'],
        "backend_function_imports": imports['backend'],
        "frontend_class_imports": class_imports['frontend'],
        "backend_class_imports": class_imports['backend'],
    }