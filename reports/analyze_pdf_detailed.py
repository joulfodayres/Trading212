#!/usr/bin/env python3
"""
Enhanced PDF Structure Analysis - Extract detailed content from Trading 212 PDFs
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import pdfplumber

# UTF-8 support on Windows
sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

class DetailedPDFAnalyzer:
    """Deep analysis of PDF content and structure"""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.filename = os.path.basename(pdf_path)
        self.pdf = pdfplumber.open(pdf_path)
        self.content = {
            'header': {},
            'sections': [],
            'tables': [],
            'full_text': ''
        }

    def extract_header_info(self):
        """Extract header/metadata from first page"""
        print(f"  📋 Extracting header info...")
        first_page = self.pdf.pages[0]
        text = first_page.extract_text() or ""

        # Extract common header fields
        lines = text.split('\n')[:20]  # First 20 lines

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Parse key-value pairs
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key, value = parts[0].strip(), parts[1].strip()
                    self.content['header'][key] = value

        return self.content['header']

    def extract_all_text_by_page(self):
        """Extract full text with page markers"""
        print(f"  📄 Extracting text from {len(self.pdf.pages)} pages...")

        full_text = ""
        page_texts = []

        for i, page in enumerate(self.pdf.pages):
            text = page.extract_text() or ""
            full_text += f"\n\n{'='*80}\nPAGE {i+1} of {len(self.pdf.pages)}\n{'='*80}\n\n{text}"
            page_texts.append({
                'page': i + 1,
                'text': text,
                'length': len(text)
            })

        self.content['full_text'] = full_text
        self.content['pages'] = page_texts

        return page_texts

    def extract_tables_detailed(self):
        """Extract tables with detailed analysis"""
        print(f"  📊 Extracting tables...")

        all_tables = []

        for page_num, page in enumerate(self.pdf.pages, 1):
            tables = page.extract_tables() or []

            for table_idx, table in enumerate(tables):
                if not table:
                    continue

                table_info = {
                    'page': page_num,
                    'table_index': table_idx,
                    'rows': len(table),
                    'cols': len(table[0]) if table else 0,
                    'headers': self._clean_row(table[0]) if table else [],
                    'data_rows': [self._clean_row(row) for row in table[1:]] if len(table) > 1 else [],
                    'data_sample': [self._clean_row(row) for row in table[:min(3, len(table))]],
                }

                all_tables.append(table_info)

        self.content['tables'] = all_tables
        print(f"    Found {len(all_tables)} tables")

        return all_tables

    def _clean_row(self, row):
        """Clean row data"""
        return [str(cell).strip() if cell else '' for cell in row]

    def identify_sections(self):
        """Identify major sections in document"""
        print(f"  🔍 Identifying sections...")

        text = self.content['full_text']
        lines = text.split('\n')

        sections = []
        current_section = None

        for i, line in enumerate(lines):
            line_clean = line.strip()

            # Detect section headers (uppercase, multi-word)
            if len(line_clean) > 10 and line_clean.isupper() and not any(c.isdigit() for c in line_clean[:5]):
                if current_section and current_section['content']:
                    sections.append(current_section)

                current_section = {
                    'name': line_clean,
                    'page': self._estimate_page(i),
                    'line_start': i,
                    'content': [],
                    'field_count': 0,
                }
            elif current_section:
                if line_clean and not line_clean.startswith('---'):
                    current_section['content'].append(line_clean)

                    # Count fields (lines with ":" in them)
                    if ':' in line_clean:
                        current_section['field_count'] += 1

        if current_section and current_section['content']:
            sections.append(current_section)

        self.content['sections'] = sections
        print(f"    Found {len(sections)} sections")

        return sections

    def _estimate_page(self, line_num):
        """Estimate which page a line number is on"""
        # Rough estimate based on ~40 lines per page
        return (line_num // 40) + 1

    def generate_detailed_report(self):
        """Generate detailed analysis report"""
        lines = []

        lines.append("# Detailed Trading 212 PDF Structure Analysis\n")
        lines.append(f"## File: {self.filename}\n")
        lines.append(f"- **Total Pages:** {len(self.pdf.pages)}")
        lines.append(f"- **Total Text Length:** {len(self.content['full_text']):,} characters")
        lines.append(f"- **Sections Identified:** {len(self.content['sections'])}")
        lines.append(f"- **Tables Found:** {len(self.content['tables'])}\n")

        # Header info
        if self.content['header']:
            lines.append("## Header Information\n")
            for key, value in sorted(self.content['header'].items()):
                lines.append(f"- **{key}:** {value}")
            lines.append('')

        # Sections
        if self.content['sections']:
            lines.append("## Identified Sections\n")
            for i, section in enumerate(self.content['sections'], 1):
                lines.append(f"### Section {i}: {section['name']}")
                lines.append(f"- **Estimated Page:** {section['page']}")
                lines.append(f"- **Fields Found:** {section['field_count']}")
                lines.append(f"- **Content Lines:** {len(section['content'])}")
                if section['content'][:3]:
                    lines.append(f"- **Sample Content:**")
                    for sample_line in section['content'][:3]:
                        lines.append(f"  - {sample_line[:80]}")
                lines.append('')

        # Tables
        if self.content['tables']:
            lines.append("## Tables Extracted\n")
            lines.append("| Page | Table # | Rows | Cols | Headers |")
            lines.append("|------|---------|------|------|---------|")
            for table in self.content['tables']:
                headers_str = ', '.join(table['headers'][:3])
                if len(table['headers']) > 3:
                    headers_str += f", +{len(table['headers'])-3} more"
                lines.append(f"| {table['page']} | {table['table_index']} | {table['rows']} | {table['cols']} | {headers_str} |")

            lines.append('')

            # Detailed table info
            lines.append("## Table Details\n")
            for table in self.content['tables']:
                lines.append(f"### Table {table['table_index']} (Page {table['page']})\n")
                lines.append(f"**Dimensions:** {table['rows']} rows × {table['cols']} columns\n")

                if table['headers']:
                    lines.append("**Headers:**")
                    for header in table['headers']:
                        lines.append(f"- {header}")
                    lines.append('')

                if table['data_sample']:
                    lines.append("**Data Sample (First 3 rows):**")
                    for row_idx, row in enumerate(table['data_sample'], 1):
                        lines.append(f"- Row {row_idx}: {' | '.join(row[:5])}{'...' if len(row) > 5 else ''}")
                    lines.append('')

        return '\n'.join(lines)

    def close(self):
        """Close PDF"""
        if self.pdf:
            self.pdf.close()


def main():
    """Main execution"""
    print("\n" + "="*80)
    print("  DETAILED TRADING 212 PDF STRUCTURE ANALYSIS")
    print("="*80 + "\n")

    pdf_path_1 = r"C:\claude\401. Trading 212 Hub\reports\Activity-Statement-2026-06-01-2026-06-30.pdf"
    pdf_path_2 = r"C:\claude\401. Trading 212 Hub\reports\Activity-Statement-2026-09-01-2026-09-01.pdf"
    output_dir = r"C:\claude\401. Trading 212 Hub\reports"

    reports = []

    for pdf_path in [pdf_path_1, pdf_path_2]:
        if not os.path.exists(pdf_path):
            print(f"✗ File not found: {pdf_path}")
            continue

        print(f"\n📄 Analyzing: {os.path.basename(pdf_path)}\n")

        analyzer = DetailedPDFAnalyzer(pdf_path)
        analyzer.extract_header_info()
        analyzer.extract_all_text_by_page()
        analyzer.extract_tables_detailed()
        analyzer.identify_sections()

        report = analyzer.generate_detailed_report()
        reports.append(report)

        # Save individual report
        filename = os.path.basename(pdf_path).replace('.pdf', '')
        output_path = os.path.join(output_dir, f"{filename}_DETAILED_ANALYSIS.md")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n✓ Report saved: {output_path}\n")

        analyzer.close()

    # Save combined report
    print("="*80)
    print("💾 Saving combined analysis...\n")

    combined_report = "\n\n" + "="*80 + "\n\n".join(reports)

    combined_path = os.path.join(output_dir, "DETAILED_STRUCTURE_COMPARISON.md")
    with open(combined_path, 'w', encoding='utf-8') as f:
        f.write("# Trading 212 Activity Statements - Detailed Structure Comparison\n\n")
        f.write("**Analysis Date:** 2026-09-20\n\n")
        f.write("This document contains detailed structure analysis of both PDF files.\n\n")
        f.write(combined_report)

    print(f"✓ Combined report saved: {combined_path}\n")
    print("="*80 + "\n")

    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
