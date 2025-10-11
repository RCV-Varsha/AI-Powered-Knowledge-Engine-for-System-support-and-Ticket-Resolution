import ast

def find_all_functions(filepath):
    """Parses a Python file and returns a list of all function names, including nested ones."""
    with open(filepath, "r", encoding="utf-8") as file:  # 👈 added encoding
        source_code = file.read()

    tree = ast.parse(source_code)
    functions = []

    class FunctionVisitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            functions.append(node.name)
            self.generic_visit(node)

    FunctionVisitor().visit(tree)
    return functions


file_path = r"C:\Users\CHAKRA VARSHINI\Desktop\AI PROJECT_BATCH1\src\kb_processor.py"
all_functions = find_all_functions(file_path)
print(all_functions)
