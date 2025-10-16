import os
import javalang

project_folder = os.path.expanduser("~/defects4j_experiments/Lang_1b_javalang")
src_folder = os.path.join(project_folder, "src/main/java")
output_file = os.path.join(project_folder, "all_condition_blocks.txt")

condition_nodes = {"IfStatement", "WhileStatement", "ForStatement", "DoStatement", "SwitchStatement"}

def extract_conditions(java_code):
    results = []
    try:
        tree = javalang.parse.parse(java_code)
        for path, node in tree.filter(javalang.tree.Statement):
            kind = type(node).__name__
            if kind in condition_nodes:
                results.append(f"{kind} at line {node.position}")
    except Exception as e:
        results.append(f"ParseError: {e}")
    return results

# Process all Java files
with open(output_file, "w", encoding="utf-8") as out_f:
    for root, dirs, files in os.walk(src_folder):
        for file in files:
            if file.endswith(".java"):
                file_path = os.path.join(root, file)
                out_f.write(f"\n=== File: {file_path} ===\n")
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        java_code = f.read()
                    conditions = extract_conditions(java_code)
                    for cond in conditions:
                        out_f.write(cond + "\n")
                except Exception as e:
                    out_f.write(f"ParseError: {e}\n")

print(f"All condition blocks extracted: {output_file}")
