from grammar import Tree, Token

def print_tree(root, indent=0):
    if isinstance(root, Token):
        print("\t"*indent + str(root))
    elif isinstance(root, Tree):
        print("\t"*indent + "Tree(\"" + root.name + "\", [")
        if len(root.children) == 0:
            print("])")
        else:
            #print("\n")
            for child in root.children:
                print_tree(child, indent+1)
            print("\t"*indent + "])")