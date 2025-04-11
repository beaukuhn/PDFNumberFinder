# PDF Number Finder

A Python tool for finding the largest numbers in PDF documents, with support for scaled values.

## Overview

This tool analyzes PDF documents to identify the largest numerical values, handling both raw numbers and numbers with scaling factors (such as millions or billions). It's particularly useful for analyzing financial documents, reports, and other PDFs containing numerical data.

## Features

- Finds all numbers in a document, regardless of size or format
- Detects scaled numbers with explicit indicators (e.g., "9.6 billion")
- Recognizes contextual scaling from phrases like "in millions" or "dollars in billions"
- Handles comma-delimited numbers correctly
- Provides context for each number to help verify its meaning
- Deduplicates numbers to avoid counting the same value multiple times
- Identifies both the largest raw number and the largest scaled number

## Code Characteristics

- Organized into a class-based structure for modularity
- Includes test suite to validate functionality
- Focused on performance and accuracy

## Requirements

- Python 3.6 or higher
- PyMuPDF (also known as fitz)
- pytest (for running tests)

## Installation

1. Clone this repository or download the files.

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the script with Python:

```bash
python pdf_number_finder.py
```

For testing with the NIST_Numbers.pdf sample document:

```bash
python test_pdf_number_finder.py
```

By default, the script will:

1. Look for a file named `FY25 Air Force Working Capital Fund.pdf` in the current directory
2. Process all pages in the document
3. Find the largest unscaled and scaled numbers
4. Display the top 5 unscaled and scaled numbers with their context
5. Print a summary of the results

### Customization

To analyze a different PDF file or change other behavior, you can modify the `main()` function in the script:

```python
def main():
    pdf_path = "your_document.pdf"  # Change this to your file path

    finder = PDFNumberFinder(pdf_path)
    if not finder.process():
        return

    # Check for a specific number (optional)
    finder.check_for_specific_number(12345)  # Add this if you want to find a specific number

    # Display top N results
    finder.display_results(top_n=10)  # Change to show more or fewer results

    # Print summary
    finder.print_summary()
```

## How It Works

The script uses a class-based approach with the following process:

1. **PDF Text Extraction**: Each page of the PDF is processed using PyMuPDF to extract its text content.

2. **Number Detection**:

   - All numbers are found using regex pattern matching
   - Explicit scaling (like "5 million") is detected with specialized patterns
   - Contextual scaling is applied when phrases like "in millions" are found

3. **Deduplication**: Numbers with the same value, original text, and page number are combined to avoid duplicates.

4. **Results Presentation**: The largest numbers are identified and presented with their context.

## Output Example

```
=== TOP UNSCALED NUMBERS ===
1. Value: 6000000.0
   Original text: 6,000,000
   Page: 93
   Context: costing between $250,000 and $6,000,000) and are designed...

2. Value: 1754801.0
   Original text: 1,754,801
   Page: 29
   Context: Number of Receipts 1,754,801 1,712,815 1,641,568...

...

=== TOP SCALED NUMBERS (DEDUPLICATED) ===
1. Scaled value: 30704100000.0
   Original text: 30,704.1
   Scaling factor: millions (from context)
   Page: 13
   Context: FY 2025 Total Revenue T 28,239.2 29,176.6 30,704.1 Cost of Goods...

...

=== SUMMARY ===
Total unscaled numbers found: 4680
Total scaled numbers found: 515 (Deduplicated: 327)

Largest unscaled number: 6000000.0
Original text: 6,000,000
Page: 93

Largest scaled number: 30704100000.0
Original text: 30,704.1
Scaling factor: millions (from context)
Page: 13
```

## Advanced Usage

The `PDFNumberFinder` class can be imported and used in other Python scripts:

```python
from pdf_number_finder import PDFNumberFinder

# Initialize and process
finder = PDFNumberFinder("document.pdf")
finder.process()

# Access results
largest_unscaled = finder.largest_unscaled
largest_scaled = finder.largest_scaled

# Process results
if largest_unscaled:
    print(f"Largest value: {largest_unscaled.value}")

# Check for specific numbers if needed
finder.check_for_specific_number(12345)
```

## Testing

A test suite is included to validate functionality with the NIST_Numbers.pdf test document:

```bash
pytest test_pdf_number_finder.py
```

## License

[MIT License](LICENSE)
