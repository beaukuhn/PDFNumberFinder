#!/usr/bin/env python3
import re
import os
from collections import namedtuple
import fitz

NumberFound = namedtuple(
    "NumberFound", ["value", "original_text", "page_num", "context"]
)
ScaledNumber = namedtuple(
    "ScaledNumber", ["value", "original_text", "scaling_factor", "page_num", "context"]
)


class PDFNumberFinder:
    """A class to find and analyze numbers in PDF documents."""

    def __init__(self, pdf_path):
        """Initialize with path to PDF file."""
        self.pdf_path = pdf_path
        self.page_texts = []
        self.unscaled_numbers = []
        self.scaled_numbers = []

        # Regex for matching numbers: matches numbers with commas as thousand separators,
        # with optional decimal part, not preceded or followed by alphanumeric or dot
        self.number_pattern = r"(?<![a-zA-Z0-9.])(?:[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)(?![a-zA-Z0-9.])"

        # Define scaling patterns and their multiplication factors
        self.scaling_patterns = [
            (
                r"([-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)\s*trillion",
                1e12,
                "trillion",
            ),
            (r"([-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)\s*billion", 1e9, "billion"),
            (r"([-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)\s*million", 1e6, "million"),
            (
                r"([-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)\s*thousand",
                1e3,
                "thousand",
            ),
        ]

        # Define context scaling phrases
        self.context_scaling = [
            (
                r"(?:dollars|amounts|figures|values)\s+in\s+trillions",
                1e12,
                "trillions (from context)",
            ),
            (r"in\s+trillions(?:\s+of\s+dollars)?", 1e12, "trillions (from context)"),
            (
                r"(?:dollars|amounts|figures|values)\s+in\s+billions",
                1e9,
                "billions (from context)",
            ),
            (r"in\s+billions(?:\s+of\s+dollars)?", 1e9, "billions (from context)"),
            (
                r"(?:dollars|amounts|figures|values)\s+in\s+millions",
                1e6,
                "millions (from context)",
            ),
            (r"in\s+millions(?:\s+of\s+dollars)?", 1e6, "millions (from context)"),
            (
                r"(?:dollars|amounts|figures|values)\s+in\s+thousands",
                1e3,
                "thousands (from context)",
            ),
            (r"in\s+thousands(?:\s+of\s+dollars)?", 1e3, "thousands (from context)"),
        ]

    def process(self):
        """Process the PDF file and find numbers."""
        if not self._validate_file():
            return False

        # Process the PDF file
        self._extract_text_from_pdf()
        self._find_unscaled_numbers()
        self._find_scaled_numbers()
        return True

    def _validate_file(self):
        """Validate that the PDF file exists."""
        if not os.path.exists(self.pdf_path):
            print(f"Error: File '{self.pdf_path}' not found")
            return False
        return True

    def _extract_text_from_pdf(self):
        """Extract text from each page of the PDF."""
        # Open PDF
        doc = fitz.open(self.pdf_path)
        print(f"PDF has {len(doc)} pages")

        # Extract text from each page
        for page_num, page in enumerate(doc):
            text = page.get_text()
            self.page_texts.append((page_num + 1, text))

            # Print progress every 10 pages
            if (page_num + 1) % 10 == 0:
                print(f"Processed {page_num + 1} pages...")

        doc.close()

    def _get_context(self, text, match_start, match_end, context_size=50):
        """Extract context around a number."""
        context_start = max(0, match_start - context_size)
        context_end = min(len(text), match_end + context_size)
        context = text[context_start:context_end].replace("\n", " ")
        return re.sub(r"\s+", " ", context).strip()

    def _find_unscaled_numbers(self):
        """Find all unscaled numbers in the document."""
        print("Finding unscaled numbers...")

        for page_num, text in self.page_texts:
            for match in re.finditer(self.number_pattern, text):
                number_text = match.group(0)

                # Clean the number for value comparison
                clean_number = number_text.replace(",", "")

                try:
                    value = float(clean_number)

                    # Get surrounding context
                    context = self._get_context(text, match.start(), match.end())

                    # Add to our collection
                    self.unscaled_numbers.append(
                        NumberFound(value, number_text, page_num, context)
                    )
                except ValueError:
                    continue

    def _find_scaled_numbers(self):
        """Find numbers with scaling factors (million, billion, etc.)."""
        print("Finding scaled numbers...")

        # Process each page
        for page_num, text in self.page_texts:
            # First, look for direct scaling (like "X million")
            self._find_direct_scaled_numbers(page_num, text)

            # Then check for contextual scaling phrases
            self._find_context_scaled_numbers(page_num, text)

    def _find_direct_scaled_numbers(self, page_num, text):
        """Find numbers with explicit scaling terms (like '5 million')."""
        for pattern, multiplier, factor_name in self.scaling_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                num_str = match.group(1)
                clean_num = num_str.replace(",", "")

                try:
                    value = float(clean_num) * multiplier

                    # Get context
                    context = self._get_context(text, match.start(), match.end())

                    self.scaled_numbers.append(
                        ScaledNumber(value, num_str, factor_name, page_num, context)
                    )
                except ValueError:
                    continue

    def _find_context_scaled_numbers(self, page_num, text):
        """Find numbers in contexts that indicate scaling (like 'in millions')."""
        for pattern, multiplier, factor_name in self.context_scaling:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Find a section of text around this phrase
                section_start = max(0, match.start() - 200)
                section_end = min(len(text), match.end() + 200)
                section = text[section_start:section_end]

                # Look for numbers in this section
                for num_match in re.finditer(self.number_pattern, section):
                    num_str = num_match.group(0)
                    clean_num = num_str.replace(",", "")

                    try:
                        # Apply the scaling factor
                        value = float(clean_num) * multiplier

                        # Get context around the number
                        context = self._get_context(
                            section, num_match.start(), num_match.end()
                        )
                        context += f" [NOTE: {factor_name}]"

                        self.scaled_numbers.append(
                            ScaledNumber(value, num_str, factor_name, page_num, context)
                        )
                    except ValueError:
                        continue

    def check_for_specific_number(self, target_value=35110):
        """Check if a specific number exists in the results."""
        deduplicated_unscaled = self._deduplicate_unscaled_numbers()
        for number in deduplicated_unscaled:
            if abs(number.value - target_value) < 0.1:
                print(f"\n=== FOUND TARGET NUMBER {target_value} ===")
                print(f"Value: {number.value}")
                print(f"Original text: {number.original_text}")
                print(f"Page: {number.page_num}")
                print(f"Context: {number.context}")
                return True

        print(f"\nWARNING: Target number {target_value} not found in results")
        return False

    def _deduplicate_unscaled_numbers(self):
        """Remove duplicates from unscaled numbers list."""
        unique_unscaled = {}
        for num in self.unscaled_numbers:
            key = (num.value, num.original_text, num.page_num)
            if key not in unique_unscaled or unique_unscaled[key].value < num.value:
                unique_unscaled[key] = num

        return list(unique_unscaled.values())

    def _deduplicate_scaled_numbers(self):
        """Remove duplicates from scaled numbers list."""
        unique_scaled = {}
        for num in self.scaled_numbers:
            key = (num.value, num.original_text, num.page_num)
            if key not in unique_scaled or unique_scaled[key].value < num.value:
                unique_scaled[key] = num

        return list(unique_scaled.values())

    def display_results(self, top_n=5):
        """Display the top N largest unscaled and scaled numbers."""
        deduplicated_unscaled = self._deduplicate_unscaled_numbers()
        sorted_unscaled = sorted(
            deduplicated_unscaled, key=lambda x: x.value, reverse=True
        )

        deduplicated_scaled = self._deduplicate_scaled_numbers()
        sorted_scaled = sorted(deduplicated_scaled, key=lambda x: x.value, reverse=True)

        print("\n=== TOP UNSCALED NUMBERS (DEDUPLICATED) ===")
        for i, number in enumerate(sorted_unscaled[:top_n], 1):
            print(f"{i}. Value: {number.value}")
            print(f"   Original text: {number.original_text}")
            print(f"   Page: {number.page_num}")
            print(f"   Context: {number.context[:150]}...")
            print()

        print("\n=== TOP SCALED NUMBERS (DEDUPLICATED) ===")
        for i, number in enumerate(sorted_scaled[:top_n], 1):
            print(f"{i}. Scaled value: {number.value}")
            print(f"   Original text: {number.original_text}")
            print(f"   Scaling factor: {number.scaling_factor}")
            print(f"   Page: {number.page_num}")
            print(f"   Context: {number.context[:150]}...")
            print()

    def print_summary(self):
        """Print a summary of the results."""
        deduplicated_unscaled = self._deduplicate_unscaled_numbers()
        deduplicated_scaled = self._deduplicate_scaled_numbers()

        print("\n=== SUMMARY ===")
        print(
            f"Total unscaled numbers found: {len(self.unscaled_numbers)} (Deduplicated: {len(deduplicated_unscaled)})"
        )
        print(
            f"Total scaled numbers found: {len(self.scaled_numbers)} (Deduplicated: {len(deduplicated_scaled)})"
        )

        largest_unscaled = (
            max(deduplicated_unscaled, key=lambda x: x.value)
            if deduplicated_unscaled
            else None
        )
        largest_scaled = (
            max(deduplicated_scaled, key=lambda x: x.value)
            if deduplicated_scaled
            else None
        )

        if largest_unscaled:
            print(f"\nLargest unscaled number: {largest_unscaled.value}")
            print(f"Original text: {largest_unscaled.original_text}")
            print(f"Page: {largest_unscaled.page_num}")

        if largest_scaled:
            print(f"\nLargest scaled number: {largest_scaled.value}")
            print(f"Original text: {largest_scaled.original_text}")
            print(f"Scaling factor: {largest_scaled.scaling_factor}")
            print(f"Page: {largest_scaled.page_num}")

    @property
    def largest_unscaled(self):
        """Get the largest unscaled number after deduplication."""
        if not self.unscaled_numbers:
            return None

        deduplicated_unscaled = self._deduplicate_unscaled_numbers()
        return (
            max(deduplicated_unscaled, key=lambda x: x.value)
            if deduplicated_unscaled
            else None
        )

    @property
    def largest_scaled(self):
        """Get the largest scaled number after deduplication."""
        if not self.scaled_numbers:
            return None

        deduplicated_scaled = self._deduplicate_scaled_numbers()
        return (
            max(deduplicated_scaled, key=lambda x: x.value)
            if deduplicated_scaled
            else None
        )


def main():
    """Main function to run the number extraction process."""
    pdf_path = "FY25 Air Force Working Capital Fund.pdf"

    # Create and process
    finder = PDFNumberFinder(pdf_path)
    if not finder.process():
        return

    # Display results
    finder.display_results(top_n=5)

    # Print summary
    finder.print_summary()


if __name__ == "__main__":
    main()
