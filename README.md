# AST-Mutant-Mapping

This project focuses on improving **fault localization** using **Gated Graph Neural Networks (GGNN)** by integrating **mutation testing behavior**.  
It extracts conditional AST nodes (like `if`, `for`, `while`) and maps them with corresponding mutation data to analyze patterns in code behavior.

---

## 📁 Project Structure

AST-Mutant-Mapping/  
│  
├─ scripts/  
│   ├─ extract.py        # Extracts mutant information from mutants.log  
│   ├─ parse_ast.py      # Parses Java code to extract all condition blocks  
│   ├─ map_mutants.py    # Maps mutants with corresponding AST condition blocks  
│  
├─ data/  
│   ├─ all_condition_blocks.txt   # Extracted condition nodes from Java source files  
│   ├─ mutants_dataframe.csv      # Parsed mutant data with class, line, and operator  
│   ├─ mutants_mapped.csv         # Output after mapping mutants to AST conditions  
│  
└─ README.md

---

## ⚙️ How It Works

### 1. Run Defects4J Experiment
Checks out a buggy project and runs mutation testing.  

```bash
# Checkout project
defects4j checkout -p Lang -v 1b -w ~/defects4j_experiments/Lang_1b

# Compile the project
defects4j compile

# Run tests
defects4j test

# Run mutation testing
defects4j mutation
