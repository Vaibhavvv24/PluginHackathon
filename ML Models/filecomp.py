import difflib

def preprocess_text(file_path):
    with open(file_path, 'r') as file:
        text = file.read()
    # Remove full stops and spaces
    text = text.replace('.', '').replace(' ', '')
    return text

def compare_files(file1_path, file2_path):
    text1 = preprocess_text(file1_path)
    text2 = preprocess_text(file2_path)

    # Tokenize by spaces
    words1 = text1.split()
    words2 = text2.split()

    # Compare the lists of words
    diff = list(difflib.ndiff(words1, words2))
    
    additions = 0
    deletions = 0
    replacements = 0

    # We need to track additions and deletions for replacement handling
    pending_deletion = None
    
    for i, change in enumerate(diff):
        if change.startswith('+ '):
            additions += 1  # Word added in file2
            if pending_deletion:
                # If there was a pending deletion, count as a replacement
                replacements += 1
                pending_deletion = None
        elif change.startswith('- '):
            deletions += 1  # Word deleted in file1
            pending_deletion = change[2:]  # Store the word deleted from file1
        elif change.startswith('? '):
            # Handle replacements by checking if the word was deleted and added back
            if pending_deletion:
                replacements += 1
                pending_deletion = None

    return additions, deletions, replacements

# Example usage
file1_path = 'sample.txt'
file2_path = 'corrected_output.txt'

additions, deletions, replacements = compare_files(file1_path, file2_path)

# print(f'Additions: {additions}')
# print(f'Deletions: {deletions}')
print(f'Replacements: {replacements}')
