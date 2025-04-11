#!/usr/bin/env python3
import pytest
from pdf_number_finder import PDFNumberFinder

@pytest.fixture
def nist_finder():
    """Pytest fixture that provides a PDFNumberFinder for NIST_Numbers.pdf."""
    pdf_path = "NIST_Numbers.pdf"
    finder = PDFNumberFinder(pdf_path)
    finder.process()
    return finder

def test_nist_numbers_pdf_analysis(nist_finder):
    """Test that analyzes NIST_Numbers.pdf for the largest numbers."""
    assert len(nist_finder.unscaled_numbers) > 0, "No unscaled numbers found"
    
    largest_unscaled = nist_finder.largest_unscaled
    assert largest_unscaled is not None, "No unscaled numbers found"
    
    largest_scaled = nist_finder.largest_scaled
    
    print("\n=== NIST_Numbers.pdf Analysis Results ===")
    print(f"Largest unscaled number: {largest_unscaled.value}")
    print(f"Original text: {largest_unscaled.original_text}")
    print(f"Page: {largest_unscaled.page_num}")
    
    if largest_scaled:
        print(f"\nLargest scaled number: {largest_scaled.value}")
        print(f"Original text: {largest_scaled.original_text}")
        print(f"Scaling factor: {largest_scaled.scaling_factor}")
        print(f"Page: {largest_scaled.page_num}")
    else:
        print("\nNo scaled numbers found in the document.")
    
    return {
        "largest_unscaled_value": largest_unscaled.value if largest_unscaled else None,
        "largest_scaled_value": largest_scaled.value if largest_scaled else None
    }

def test_number_properties(nist_finder):
    """Test specific properties of the numbers found in NIST_Numbers.pdf."""
    assert len(nist_finder.unscaled_numbers) > 10, "Should find more than 10 unscaled numbers"
    
    largest_unscaled = nist_finder.largest_unscaled
    
    assert largest_unscaled.value > 1000, "Largest number should be significant"
    
    assert len(largest_unscaled.context) > 0, "Context should not be empty"
    
    print(f"\nLargest number details:")
    print(f"Value: {largest_unscaled.value}")
    print(f"Original text: {largest_unscaled.original_text}")
    print(f"Page: {largest_unscaled.page_num}")
    print(f"Context: {largest_unscaled.context}")

if __name__ == "__main__":
    pdf_path = "NIST_Numbers.pdf"
    finder = PDFNumberFinder(pdf_path)
    finder.process()
    
    test_results = test_nist_numbers_pdf_analysis(finder)
    test_number_properties(finder)
    
    print(f"\nTest Results: {test_results}") 