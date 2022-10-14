from concurrent.futures import process
from transformer import TYPES
from constants import FUNCTION_IMPORTS, CLASS_IMPORTS

# turn to true for debug logs
LOG = True

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

    custom_imports = {
        "frontend": {},
        "backend": {},
    }

    current_context = None

    def append_statement(statement):
        active.append(statement)

    def switch_env(new_env):
        nonlocal active, env
        env = new_env
        log("changing env to " + env)
        if env == "frontend":
            active = frontend
        elif env == "backend":
            active = backend

    def add_custom_import(class_name, value):
        existing_list = custom_imports[env]
        if class_name not in existing_list:
            existing_list[class_name] = []

        if value not in existing_list[class_name]:
            log("Adding custom import {} => {}".format(class_name, value))
            existing_list[class_name].append(value)

    # first split on frontend/backend and get custom imports out
    for statement in tree:
        unwrapped_statement = unwrap_statement(statement)
        log("Environment splitter processing " + unwrapped_statement['type'])

        if unwrapped_statement['type'] == TYPES['PRAGMA']:
            pragma = unwrapped_statement['pragma']
            if pragma == 'frontend' or pragma == "backend":
                switch_env(pragma)
            else:
                if "value" in unwrapped_statement:
                    add_custom_import(unwrapped_statement['pragma'], unwrapped_statement['value'])
                else:
                    add_custom_import(unwrapped_statement['pragma'], "*")

    # next started nesting statements by identation
    context_stack = []

    def append_statement_context()

    def bundle_code(tree):
        if not isinstance(tree, list):
            tree = [tree]

        for statement in tree:
            log("Processing " + statement['type'])

            if statement['type'] == TYPES["STATEMENT"]:

        return tree


    frontend = bundle_code(frontend)
    backend = bundle_code(backend)

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
                else:
                    process_code(unwrapped, env)
            elif item['type'] == TYPES['VARIABLE_ASSIGNMENT']:
                process_code(item['value'], env)
            elif item['type'] == TYPES['JSX_START_TAG']:
                add_import("Component")
                process_code(item['attributes'], env)
            elif item['type'] == TYPES['RETURN']:
                process_code(item['value'], env)
            elif item['type'] == TYPES["VARIABLE_CHAIN"]:
                # should only be possible to have an import at the first level
                add_import(item['chain'][0])
            elif item['type'] == TYPES['JSX_ATTRIBUTE']:
                process_code(item['right_hand'], env)

    process_code(frontend, "frontend")
    process_code(backend, "backend")

    return {
        "frontend": frontend,
        "backend": backend,
        "frontend_function_imports": imports['frontend'],
        "backend_function_imports": imports['backend'],
        "frontend_class_imports": class_imports['frontend'],
        "backend_class_imports": class_imports['backend'],
        "custom_imports_frontend": custom_imports['frontend'],
        "custom_imports_backend": custom_imports['backend'],
    }