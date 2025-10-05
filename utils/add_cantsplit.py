#!/usr/bin/env python3
"""
Post-processing script to add cantSplit property to all table rows in a DOCX file.
This prevents tables from splitting across pages.
"""

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import sys


def add_cantsplit_to_tables(docx_path, output_path=None):
    """
    Add cantSplit property to all table rows in a DOCX document.

    Args:
        docx_path: Path to input DOCX file
        output_path: Path to output DOCX file (if None, overwrites input)
    """
    doc = Document(docx_path)

    # Iterate through all tables in the document
    for table in doc.tables:
        for row in table.rows:
            # Get or create table row properties (trPr)
            tr = row._tr
            trPr = tr.get_or_add_trPr()

            # Add cantSplit element if it doesn't exist
            cantSplit = OxmlElement('w:cantSplit')
            trPr.append(cantSplit)

    # Save the modified document
    if output_path is None:
        output_path = docx_path

    doc.save(output_path)
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_cantsplit.py <input.docx> [output.docx]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    result = add_cantsplit_to_tables(input_file, output_file)
    print(f"Successfully added cantSplit to tables in: {result}")
