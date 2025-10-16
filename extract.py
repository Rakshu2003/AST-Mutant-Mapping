import pandas as pd
import os
from pathlib import Path

experiments_dir = Path.home() / "defects4j_experiments"

run_folders = [f for f in experiments_dir.iterdir() if f.is_dir() and "Lang_1b_" in f.name]
if not run_folders:
    raise FileNotFoundError("No Lang_1b experiment folders found in defects4j_experiments!")

latest_run = max(run_folders, key=os.path.getctime)
print(f" Latest run folder detected: {latest_run}")


mutants_log = latest_run / "mutants.log"
if not mutants_log.exists():
    raise FileNotFoundError(f"No mutants.log found in {latest_run}")


data = []
with open(mutants_log, "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        
        
        parts = line.split("|==>")
        before = parts[0].strip()
        after = parts[1].strip() if len(parts) > 1 else ""
        
        
        fields = before.split(":")
        if len(fields) >= 7:
            mutant_id = fields[0]
            operator = fields[1]
            extra = fields[2]
            pos_neg = fields[3]
            class_name = fields[4]
            line_number = fields[5]
            original = fields[6]
            
            data.append({
                "MutantID": mutant_id,
                "Operator": operator,
                "Extra": extra,
                "POS_NEG": pos_neg,
                "Class": class_name,
                "Line": int(line_number),
                "Original": original,
                "Mutated": after
            })

df = pd.DataFrame(data)
print(df.head())

output_csv = latest_run / "mutants_dataframe.csv"
df.to_csv(output_csv, index=False)
print(f"\n Mutants data saved to: {output_csv}")
