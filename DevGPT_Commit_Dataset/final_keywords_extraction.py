import csv

# Function to read the CSV containing keywords
def read_keywords_csv(filename):
    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        return {row[0].strip().lower() for row in reader if row}  # Set of keywords

# Function to read the CSV containing word frequencies
def read_frequencies_csv(filename):
    frequencies = {}
    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            if len(row) >= 2:
                word = row[0].strip().lower()
                try:
                    frequency = int(row[1])
                    frequencies[word] = frequency
                except ValueError:
                    continue  # Skip rows with invalid numbers
    return frequencies

# Function to compare keywords and frequencies, then write the result to a new CSV
def generate_final_csv(keywords_file, frequencies_file, output_file):
    keywords = read_keywords_csv(keywords_file)
    frequencies = read_frequencies_csv(frequencies_file)

    # Find common keywords (exact match, lowercase)
    common_keywords = {word: frequencies[word] for word in keywords if word in frequencies}

    # Write to output CSV
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Keyword", "Frequency"])
        for keyword, frequency in common_keywords.items():
            writer.writerow([keyword, frequency])

    print(f"✅ Final list of common keywords written to: {output_file}")

# File paths
keywords_file = 'literature_keywords.csv'
frequencies_file = 'word_frequencies.csv'
output_file = 'final_list_of_keywords.csv'

# Run the comparison
generate_final_csv(keywords_file, frequencies_file, output_file)
