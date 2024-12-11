from gramformer import Gramformer
import os
import re

def initialize_gramformer():
    """
    Initialize the Gramformer model.
    """
    gf = Gramformer(models=1, use_gpu=False)  # Use GPU if available
    return gf

def count_errors(original, corrected):
    """
    Count the number of errors based on differences between the original and corrected sentences.

    Args:
        original (str): Original sentence.
        corrected (str): Corrected sentence.

    Returns:
        tuple: The count of errors and a list of error details.
    """
    # Remove trailing punctuation marks for comparison
    original = original.rstrip('.,!?')
    corrected = corrected.rstrip('.,!?')

    original_words = original.split()
    corrected_words = corrected.split()

    error_count = 0
    error_details = []
    seen_errors = set()  # To track errors only once

    # Compare words in the original and corrected sentences
    for i in range(min(len(original_words), len(corrected_words))):
        if original_words[i] != corrected_words[i]:
            # If this word pair hasn't been seen yet, add as error
            if (original_words[i], corrected_words[i]) not in seen_errors:
                error_count += 1
                error_details.append(f"Replaced: [{original_words[i]}] -> [{corrected_words[i]}]")
                seen_errors.add((original_words[i], corrected_words[i]))

    # If the sentences are of different lengths, count the extra words as errors
    if len(original_words) < len(corrected_words):
        for i in range(len(original_words), len(corrected_words)):
            if corrected_words[i] not in seen_errors:
                error_count += 1
                error_details.append(f"Inserted: [{corrected_words[i]}]")
                seen_errors.add((None, corrected_words[i]))  # mark as inserted
    elif len(original_words) > len(corrected_words):
        for i in range(len(corrected_words), len(original_words)):
            if original_words[i] not in seen_errors:
                error_count += 1
                error_details.append(f"Deleted: [{original_words[i]}]")
                seen_errors.add((original_words[i], None))  # mark as deleted

    return error_count, error_details

def correct_sentence_with_error_count(sentence):
    """
    Correct a sentence and count the errors.

    Args:
        gf (Gramformer): Initialized Gramformer model.
        sentence (str): Original sentence to correct.

    Returns:
        tuple: (corrected_sentence, error_count, error_details)
    """
    gf = initialize_gramformer()
    corrections = list(gf.correct(sentence))
    corrected_sentence = corrections[0] if corrections else sentence
    error_count, error_details = count_errors(sentence, corrected_sentence)
    
    return corrected_sentence, error_count, error_details

def process_text_file(incorrect:list[str]):
    """
    Process a text file, calculate grammar errors, and save the corrected output.

    Args:
        file_path (str): Path to the input text file.
        output_path (str): Path to save the corrected output file.

    Returns:
        dict: A dictionary with error count, total sentences, and grammar score.
    """
    # if not os.path.exists(file_path):
    #     raise FileNotFoundError(f"File '{file_path}' does not exist.")

    # with open(file_path, "r", encoding="utf-8") as file:
    #     lines = file.readlines()

    corrected_sentences = []
    total_sentences = 0
    total_errors = 0
    all_error_details = []

    gf = initialize_gramformer()

    # Process each sentence
    for line in incorrect:
        # Split on punctuation (periods, exclamation marks, question marks) and new lines
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!|\n)', line.strip())
        for sentence in sentences:
            if sentence.strip():  # Ignore empty sentences
                total_sentences += 1
                corrected, errors, error_details = correct_sentence_with_error_count(gf, sentence.strip())
                corrected_sentences.append(corrected)
                total_errors += errors
                all_error_details.extend(error_details)

    # # Save corrected sentences to output file
    # with open(output_path, "w", encoding="utf-8") as file:
    #     file.write("\n".join(corrected_sentences))

    # Return the results
    return {
        "total_sentences": total_sentences,
        "total_errors": total_errors,
        "grammar_score": total_errors,  # Number of errors as grammar score
        # "output_file": output_path,
        "error_details": all_error_details,
        "corrected_sentences": corrected_sentences
    }

def compare_files(original_file, corrected_file):
    """
    Compare original and corrected files and count the differences (errors).
    
    Args:
        original_file (str): Path to the original file.
        corrected_file (str): Path to the corrected file.
    
    Returns:
        tuple: Error count and detailed error list.
    """
    with open(original_file, "r", encoding="utf-8") as file:
        original_text = file.read()

    with open(corrected_file, "r", encoding="utf-8") as file:
        corrected_text = file.read()

    original_sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!|\n)', original_text.strip())
    corrected_sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!|\n)', corrected_text.strip())

    error_count = 0
    error_details = []

    for original, corrected in zip(original_sentences, corrected_sentences):
        errors, details = count_errors(original.strip(), corrected.strip())
        error_count += errors
        error_details.extend(details)

    # Final consolidated error count
    final_error_count = len(set(error_details))  # Deduplicate errors (same error reported multiple times)

    return final_error_count, error_details

def main():
    """
    Main function to process a text file, calculate grammar errors, and save corrected output.
    """
    print("Initializing the grammar correction model...")
    gf = initialize_gramformer()
    print("Model initialized successfully!")

    # Specify the input and output file paths
    input_file = r"C:\Users\mitta\OneDrive - iiit-b\Documents\PluginHack\ML Models\sample.txt"  # Replace with your input file path
    output_file = "corrected_output.txt"  # Output file created by Gramformer
    final_output_file = "final_corrected_output.txt"  # Corrected output after comparing

    try:
        # First, process the file and get the corrected output
        results = process_text_file(input_file, output_file, gf)

        print("\n--- Grammar Score Report ---")
        print(f"Total Sentences: {results['total_sentences']}")
        print(f"Errors Detected: {results['total_errors']}")
        print(f"Grammar Score (Number of Errors): {results['grammar_score']}")
        print(f"Corrected output saved to: {results['output_file']}")

        print("\n--- Detailed Errors ---")
        for error in results["error_details"]:
            print(error)

        # Now, compare the original and corrected files and count the errors
        error_count, error_details = compare_files(input_file, output_file)

        print("\n--- Final Error Count ---")
        print(f"Total Errors: {error_count}")
        print(f"Corrected output compared and errors counted.")
        print("\n--- Detailed Final Errors ---")
        for error in error_details:
            print(error)

    except FileNotFoundError as e:
        print(e)

if __name__ == "__main__":
    main()
