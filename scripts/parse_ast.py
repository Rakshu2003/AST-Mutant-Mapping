import javalang
import os

def extract_condition_blocks(java_file_path, output_file):
    """
    Extract all condition blocks (if, while, for, etc.) from a Java file
    and write them to the output file with metadata.
    """
    try:
        with open(java_file_path, 'r', encoding='utf-8') as file:
            java_code = file.read()
        
        # Parse the Java code
        tree = javalang.parse.parse(java_code)
        
        # Get the class name from the file
        file_name = os.path.basename(java_file_path)
        class_name = file_name.replace('.java', '')
        
        # Find the package name
        package_name = ""
        if tree.package:
            package_name = tree.package.name
        
        full_class_name = f"{package_name}.{class_name}" if package_name else class_name
        
        # Counter for condition blocks
        count = 0
        
        # Walk through the AST to find condition statements
        for path, node in tree:
            node_type = type(node).__name__
            
            # Check if it's a control flow statement
            if node_type in ['IfStatement', 'WhileStatement', 'ForStatement', 
                           'DoStatement', 'SwitchStatement', 'TernaryExpression']:
                
                # Get the line number
                line_number = None
                if hasattr(node, 'position') and node.position:
                    # node.position is a tuple (line, column)
                    if isinstance(node.position, tuple):
                        line_number = node.position[0]  # First element is line
                    elif hasattr(node.position, 'line'):
                        line_number = node.position.line
                
                # Extract the condition
                condition = None
                if hasattr(node, 'condition') and node.condition:
                    condition = str(node.condition)
                elif node_type == 'SwitchStatement' and hasattr(node, 'expression'):
                    condition = str(node.expression)
                elif node_type == 'TernaryExpression':
                    condition = str(node.condition) if hasattr(node, 'condition') else None
                
                # Write to output file
                output_file.write("=" * 50 + "\n")
                output_file.write(f"Class: {full_class_name}\n")
                output_file.write(f"Line: {line_number if line_number else 'Unknown'}\n")
                output_file.write(f"Node Type: {node_type}\n")
                output_file.write(f"Condition: {condition if condition else 'N/A'}\n")
                output_file.write("=" * 50 + "\n\n")
                
                count += 1
        
        return count
    
    except Exception as e:
        output_file.write(f"=== {os.path.basename(java_file_path)} Error: {str(e)} ===\n")
        return 0

def main():
    # Define paths - pointing to your actual project location
    project_folder = os.path.expanduser("~/defects4j_experiments/Lang_1b_javalang")
    source_dir = os.path.join(project_folder, "src/main/java")
    
    # Save output to the AST-Mutant-Mapping data folder
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file_path = os.path.join(base_dir, 'data', 'all_condition_blocks.txt')
    
    # Check if source directory exists
    if not os.path.exists(source_dir):
        print(f"Error: Source directory not found: {source_dir}")
        print("Please ensure the commons-lang project is in the correct location.")
        return
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    
    print(f"Scanning Java files in: {source_dir}")
    print(f"Output will be saved to: {output_file_path}")
    print("=" * 60)
    
    total_files = 0
    total_blocks = 0
    
    # Open output file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        # Walk through all Java files
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.java'):
                    java_file_path = os.path.join(root, file)
                    print(f"Processing: {file}...", end=" ")
                    
                    blocks_found = extract_condition_blocks(java_file_path, output_file)
                    
                    if blocks_found > 0:
                        print(f"✓ Found {blocks_found} condition blocks")
                        total_files += 1
                        total_blocks += blocks_found
                    else:
                        print("✗ No blocks or error")
    
    print("=" * 60)
    print(f"\n✅ Extraction complete!")
    print(f"📁 Processed {total_files} files")
    print(f"📊 Found {total_blocks} condition blocks")
    print(f"💾 Output saved to: {output_file_path}")

if __name__ == "__main__":
    main()