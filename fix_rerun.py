import re

def replace_experimental_rerun(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace all occurrences of st.experimental_rerun() with st.rerun()
    updated = content.replace('st.experimental_rerun()', 'st.rerun()')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated)

# Run the replacement
replace_experimental_rerun('app.py')