import csv

# Function to read the CSV containing keywords
def read_keywords_csv(filename):
    with open(filename, mode='r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        return {row[0]: 1 for row in reader}  # Create a dictionary with keywords as keys

# Function to read the CSV containing word frequencies
def read_frequencies_csv(filename):
    frequencies = {}
    with open(filename, mode='r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            word, frequency = row[0], int(row[1])
            frequencies[word] = frequency
    return frequencies

# Function to compare keywords and frequencies, then write the result to a new CSV
def generate_final_csv(keywords_file, frequencies_file, output_file):
    # Read the keywords from the literature file
    keywords = read_keywords_csv(keywords_file)
    
    # Read the frequencies from the commit messages file
    frequencies = read_frequencies_csv(frequencies_file)

    # Find common keywords and their frequencies
    common_keywords = {word: frequencies[word] for word in keywords if word in frequencies}

    # Write the common keywords and their frequencies to the output CSV
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Keyword", "Frequency"])  # Header row
        
        # Write each common keyword and its frequency
        for keyword, frequency in common_keywords.items():
            writer.writerow([keyword, frequency])

    print(f"Final list of common keywords written to {output_file}")

# Define the filenames of the input CSVs and the output CSV
keywords_file = 'keywords.csv'  # Literature keywords CSV
frequencies_file = 'word_frequencies.csv'  # Word frequency CSV from commit messages
output_file = 'final_list_of_keywords.csv'  # The output CSV for common keywords

# Call the function to generate the final CSV
generate_final_csv(keywords_file, frequencies_file, output_file)
