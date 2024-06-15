import os
import time
from flask import Flask, request, render_template, redirect
from werkzeug.utils import secure_filename

# Initialize the Flask application
app = Flask(__name__)
# Set the folder where uploaded files will be stored
app.config['UPLOAD_FOLDER'] = 'uploads'

# Function to read words from a file and return them as a list
def read_words(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file]

# Helper function to determine if a word can be formed by other words in the set
def can_form_word(word, words_set, memo):
    if word in memo:
        return memo[word]  # Return cached result if available

    # Check each possible prefix-suffix split
    for i in range(1, len(word)):
        prefix = word[:i]
        suffix = word[i:]
        if prefix in words_set and (suffix in words_set or can_form_word(suffix, words_set, memo)):
            memo[word] = True  # Cache the result
            return True
    
    memo[word] = False  # Cache the result
    return False

# Function to find the longest and second-longest compound words from a list of words
def find_compound_words(words):
    words_set = set(words)
    compound_words = []
    memo = {}

    # Check each word in the list
    for word in words:
        if can_form_word(word, words_set, memo):
            compound_words.append(word)

    # Sort the compound words by length in descending order
    compound_words.sort(key=len, reverse=True)
    longest_word = compound_words[0] if compound_words else None
    second_longest_word = compound_words[1] if len(compound_words) > 1 else None

    return longest_word, second_longest_word

# Route for handling the upload form and processing the files
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file1' not in request.files or 'file2' not in request.files:
            return redirect(request.url)  # Redirect if files are not found

        file1 = request.files['file1']
        file2 = request.files['file2']

        if file1.filename == '' or file2.filename == '':
            return redirect(request.url)  # Redirect if filenames are empty

        if file1 and file2:
            filename1 = secure_filename(file1.filename)
            filename2 = secure_filename(file2.filename)
            file1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))  # Save the first file
            file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))  # Save the second file

            words1 = read_words(os.path.join(app.config['UPLOAD_FOLDER'], filename1))  # Read words from the first file
            words2 = read_words(os.path.join(app.config['UPLOAD_FOLDER'], filename2))  # Read words from the second file

            start_time = time.time()
            longest1, second_longest1 = find_compound_words(words1)  # Find compound words in the first list
            longest2, second_longest2 = find_compound_words(words2)  # Find compound words in the second list
            end_time = time.time()
            time_taken = (end_time - start_time) * 1000  # Convert time taken to milliseconds

            # Render the results in the template
            return render_template(
                'index.html', 
                longest1=longest1, second_longest1=second_longest1,
                longest2=longest2, second_longest2=second_longest2,
                time_taken=time_taken
            )

    return render_template('index.html')  # Render the upload form template

# Create the uploads folder if it does not exist and run the application
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
