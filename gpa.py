"""
gpa.py

This script processes a PDF transcript to calculate GPA (European and US systems) 
and extract details about courses. It handles courses from the main institution and 
excludes courses from other institutions. It is developed to work with the system of TU/e.

Author: knk125
Date: 27-11-2024
License: GNU General Public License v3.0

Description:
- Extracts course information, including course code, name, date, grade, and credits.
- Calculates European GPA and US GPA based on grades and credits.
- Filters out courses from other institutions.
- Processes and includes manual entries for additional courses if necessary.

Usage:
Run this script in an environment with the required dependencies (`pypdf`, `re`).

Dependencies:
- Python 3.x
- pypdf

Contact:
For questions or contributions, please reach out at https://github.com/knk125.

"""


import re
from pypdf import PdfReader

# Read the PDF file (Put the path to your PDF file here)
reader = PdfReader('transcript.pdf')

# Regular expression pattern to extract course information( if the pattern does not match, the course will be skipped( you can adjust the pattern as needed))
regular_pattern = re.compile(
    r'([A-Za-z0-9]{5,})\s+(.*?)(\d{2}-\d{2}-\d{4})\s+([A-Za-z0-9.]+)\s+(\d+\.\d+|\d+)' # Handles course code, name, date, grade, and credits
)

# Initialize variables for calculations
total_weighted_grades = 0
total_credits = 0
total_ects = 0
included_courses = []  # List to track included courses


def convert_to_us_gpa(grade):
    """
    Convert a European grade to the equivalent US GPA value.

    Parameters:
    grade (float): The grade in the European grading system.

    Returns:
    float: The corresponding GPA value in the US grading system.
    """
    if grade >= 9:
        return 4.0  # A+
    elif grade >= 8:
        return 3.7  # A
    elif grade >= 7:
        return 3.0  # B
    elif grade >= 6:
        return 2.0  # C
    elif grade >= 5.5:
        return 1.0  # D
    else:
        return 0.0  # F


def preprocess_text(text):
    """
    Preprocess the input text by cleaning and formatting it for parsing.

    Steps include:
    - Removing hyphenated newlines.
    - Replacing newline characters with spaces.
    - Ensuring a space exists after course codes.

    Parameters:
    text (str): The raw text extracted from the PDF.

    Returns:
    str: The cleaned and preprocessed text.
    """
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)  # Remove hyphenated newlines
    text = re.sub(r'\n', ' ', text)  # Replace newlines with spaces
    text = re.sub(r'(\d\w{4,})([A-Za-z])', r'\1 \2', text)  # Ensure space after course codes
    return text

# Manually add extra courses here in the format: ("course", "dd-mm-yyyy", grade, credits)
manual_courses = [
    # Example:
    ("01 ", "01-01-2024", 10.0, 6.0),
    # Add more courses as needed
]

# Add manually entered courses
for course, date, grade, credits in manual_courses:
    included_courses.append((course, date, grade, credits))
    total_weighted_grades += grade * credits
    total_credits += credits
    total_ects += credits

# Iterate through all pages of the PDF
for page in reader.pages:
    # Extract text from the page
    text = page.extract_text()

    # Preprocess text
    text = preprocess_text(text)

    # Ensure only relevant content is parsed
    if "Grades Final examination" in text:
        text = text.split("Grades Final examination")[1]

    # Parse regular courses
    matches = regular_pattern.findall(text)
    for match in matches:
        try:
            course, name, date, grade, credits = match
            grade = float(grade)
            credits = float(credits)

            # Skip courses with fewer than 5 ECTS (if this is not needed, you can remove this condition)
            if credits < 5:
                continue

            # Include course
            included_courses.append((course + " " + name, date, grade, credits))

            # Update totals
            total_weighted_grades += grade * credits
            total_credits += credits
            total_ects += credits
        except ValueError:
            continue  # Skip invalid entries

# # Output included courses (you can remove this if you don't need it)
# print("Included Courses:")
# for course in included_courses:
#     print(f"Course: {course[0]}, Date: {course[1]}, Grade: {course[2]}, Credits: {course[3]}")

# Calculate and print GPA values
if total_credits > 0:
    european_gpa = total_weighted_grades / total_credits
    print(f'\nTotal ECTS: {total_ects}')
    print(f'Average Grade (European System): {european_gpa:.2f}')
    print(f'US GPA: {convert_to_us_gpa(european_gpa):.2f}')
else:
    print('No valid courses found for GPA calculation.')
