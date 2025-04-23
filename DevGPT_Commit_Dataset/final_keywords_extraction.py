import csv
import re

# Function to read the CSV containing keywords
def read_keywords_csv(filename):
    # Open the CSV file containing keywords in read mode
    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        # Create a set of keywords (convert to lowercase for uniformity)
        return {row[0].strip().lower() for row in reader if row}  # Return a set of keywords

# Function to read the CSV containing word frequencies
def read_frequencies_csv(filename):
    frequencies = {}
    # Open the CSV file containing word frequencies
    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        # Loop through each row in the frequency file
        for row in reader:
            if len(row) >= 2:
                word = row[0].strip().lower()  # Get the word (convert to lowercase)
                try:
                    frequency = int(row[1])  # Get the frequency count
                    frequencies[word] = frequency  # Add word and frequency to the dictionary
                except ValueError:
                    continue  # Skip rows with invalid frequency values (not an integer)
    return frequencies  # Return the word frequencies dictionary

# Function to compare keywords and frequencies, allowing for partial matches
def generate_final_csv(keywords_file, frequencies_file, output_file):
    # Read the keywords and frequencies from their respective files
    keywords = read_keywords_csv(keywords_file)
    frequencies = read_frequencies_csv(frequencies_file)

    common_keywords = {}

    # Loop through each keyword to find matching variations
    for keyword in keywords:
        # Create a regular expression pattern to match the keyword and its variations
        # Example: 'simplify' will match 'simplify', 'simplified', 'simplifying', etc.
        pattern = re.compile(r'\b' + re.escape(keyword) + r'\w*\b', re.IGNORECASE)
        
        # Loop through all the words in the frequencies dictionary to check for matches
        for word, frequency in frequencies.items():
            if pattern.match(word):  # If the word matches the pattern (e.g., simplify -> simplify, simplified)
                common_keywords[word] = frequency  # Add the matching word and its frequency to the result dictionary

    # Write the final list of common keywords and their frequencies to a new CSV file
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Keyword", "Frequency"])  # Write header row
        # Write each matching keyword and its frequency to the CSV file
        for keyword, frequency in common_keywords.items():
            writer.writerow([keyword, frequency])

    # Notify the user that the final list has been written to the output file
    print(f"✅ Final list of common keywords written to: {output_file}")

# File paths for input (keywords and frequencies) and output (final list of keywords)
keywords_file = 'literature_keywords.csv'
frequencies_file = 'word_frequencies.csv'
output_file = 'final_list_of_keywords.csv'

# Run the comparison and generate the final CSV with matching keywords and frequencies
generate_final_csv(keywords_file, frequencies_file, output_file)
