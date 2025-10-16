import pandas as pd
import re
import os

def parse_condition_blocks(file_path):
    """
    Parse all_condition_blocks.txt to extract condition blocks with metadata.
    Returns a list of dictionaries with class, line, node_type, and condition.
    """
    condition_blocks = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by separator lines
    blocks = content.split('=' * 50)
    
    for block in blocks:
        if not block.strip():
            continue
            
        lines = block.strip().split('\n')
        
        # Extract metadata from first few lines
        class_name = None
        line_number = None
        node_type = None
        condition = None
        
        for line in lines:
            if line.startswith('Class:'):
                class_name = line.replace('Class:', '').strip()
            elif line.startswith('Line:'):
                line_str = line.replace('Line:', '').strip()
                # Handle different formats:
                # Format 1: "123"
                # Format 2: "Position(line=123, column=5)"
                if 'Position' in line_str:
                    # Extract line number from Position(line=123, column=5)
                    match = re.search(r'line=(\d+)', line_str)
                    if match:
                        line_number = int(match.group(1))
                elif line_str.isdigit():
                    line_number = int(line_str)
                elif line_str != 'Unknown':
                    # Try to extract any number
                    match = re.search(r'\d+', line_str)
                    if match:
                        line_number = int(match.group())
            elif line.startswith('Node Type:'):
                node_type = line.replace('Node Type:', '').strip()
            elif line.startswith('Condition:'):
                condition = line.replace('Condition:', '').strip()
        
        if class_name and line_number and node_type:
            condition_blocks.append({
                'class': class_name,
                'line': line_number,
                'node_type': node_type,
                'condition': condition or ''
            })
    
    return condition_blocks

def map_mutants_to_blocks(mutants_df, condition_blocks):
    """
    Map each mutant to its corresponding condition block.
    """
    # Create a lookup dictionary for faster mapping
    # Key: (class, line) -> condition block info
    block_lookup = {}
    for block in condition_blocks:
        key = (block['class'], block['line'])
        if key not in block_lookup:
            block_lookup[key] = []
        block_lookup[key].append(block)
    
    # Add new columns to mutants dataframe
    mutants_df['AST_NodeType'] = None
    mutants_df['AST_Condition'] = None
    mutants_df['MappingStatus'] = 'Not Mapped'
    
    # Map each mutant
    for idx, row in mutants_df.iterrows():
        # Strip method signature from class name (remove @method part)
        mutant_class_full = row['Class']
        mutant_class = mutant_class_full.split('@')[0] if '@' in mutant_class_full else mutant_class_full
        mutant_line = row['Line']
        
        key = (mutant_class, mutant_line)
        
        if key in block_lookup:
            # Found exact match
            blocks = block_lookup[key]
            if len(blocks) == 1:
                mutants_df.at[idx, 'AST_NodeType'] = blocks[0]['node_type']
                mutants_df.at[idx, 'AST_Condition'] = blocks[0]['condition']
                mutants_df.at[idx, 'MappingStatus'] = 'Exact Match'
            else:
                # Multiple blocks at same line (rare)
                mutants_df.at[idx, 'AST_NodeType'] = blocks[0]['node_type']
                mutants_df.at[idx, 'AST_Condition'] = blocks[0]['condition']
                mutants_df.at[idx, 'MappingStatus'] = 'Multiple Matches'
        else:
            # Try to find nearest condition block (within +/- 2 lines)
            nearest_block = None
            min_distance = float('inf')
            
            for line_offset in range(-2, 3):
                nearby_key = (mutant_class, mutant_line + line_offset)
                if nearby_key in block_lookup:
                    if abs(line_offset) < min_distance:
                        min_distance = abs(line_offset)
                        nearest_block = block_lookup[nearby_key][0]
            
            if nearest_block:
                mutants_df.at[idx, 'AST_NodeType'] = nearest_block['node_type']
                mutants_df.at[idx, 'AST_Condition'] = nearest_block['condition']
                mutants_df.at[idx, 'MappingStatus'] = f'Nearby Match (±{min_distance} lines)'
            else:
                mutants_df.at[idx, 'MappingStatus'] = 'No Match Found'
    
    return mutants_df

def main():
    # Define paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    
    condition_blocks_file = os.path.join(data_dir, 'all_condition_blocks.txt')
    mutants_csv = os.path.join(data_dir, 'mutants_dataframe.csv')
    output_csv = os.path.join(data_dir, 'mutants_mapped.csv')
    
    # Check if input files exist
    if not os.path.exists(condition_blocks_file):
        print(f"Error: {condition_blocks_file} not found!")
        print("Please run parse_ast.py first to generate all_condition_blocks.txt")
        return
    
    if not os.path.exists(mutants_csv):
        print(f"Error: {mutants_csv} not found!")
        print("Please run extract.py first to generate mutants_dataframe.csv")
        return
    
    print("Reading condition blocks...")
    condition_blocks = parse_condition_blocks(condition_blocks_file)
    print(f"Found {len(condition_blocks)} condition blocks")
    
    print("\nReading mutants dataframe...")
    mutants_df = pd.read_csv(mutants_csv)
    print(f"Found {len(mutants_df)} mutants")
    
    print("\nMapping mutants to condition blocks...")
    mapped_df = map_mutants_to_blocks(mutants_df, condition_blocks)
    
    # Save result
    mapped_df.to_csv(output_csv, index=False)
    print(f"\n✅ Mapping complete! Saved to: {output_csv}")
    
    # Print statistics
    print("\n" + "="*60)
    print("MAPPING STATISTICS")
    print("="*60)
    print(mapped_df['MappingStatus'].value_counts())
    print("\nSample of mapped data:")
    print(mapped_df[['MutantID', 'Class', 'Line', 'AST_NodeType', 'MappingStatus']].head(10))
    
    # Summary by node type
    if mapped_df['AST_NodeType'].notna().any():
        print("\n" + "="*60)
        print("MUTANTS BY AST NODE TYPE")
        print("="*60)
        print(mapped_df['AST_NodeType'].value_counts())

if __name__ == "__main__":
    main()