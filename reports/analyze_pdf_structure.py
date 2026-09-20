#!/usr/bin/env python3
"""
PDF Structure Analysis Tool for Trading 212 Activity Statements

Analyzes two PDF files (monthly and daily) and produces:
1. Full text extraction
2. Section/structure identification
3. Table extraction and analysis
4. Comprehensive comparison report
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

class PDFStructureAnalyzer:
    """Analyzes PDF structure, sections, and content"""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.filename = os.path.basename(pdf_path)
        self.pdf = None
        self.text = ""
        self.pages = []
        self.sections = []
        self.tables = []

    def load(self):
        """Load and extract PDF content"""
        print(f"📖 Loading: {self.filename}")
        try:
            self.pdf = pdfplumber.open(self.pdf_path)
            print(f"   ✓ Pages: {len(self.pdf.pages)}")

            # Extract full text
            for i, page in enumerate(self.pdf.pages):
                text = page.extract_text() or ""
                self.text += f"\n--- PAGE {i+1} ---\n{text}"
                self.pages.append({
                    'number': i + 1,
                    'text': text,
                    'tables': page.extract_tables() or []
                })

            print(f"   ✓ Total text extracted: {len(self.text)} chars")
            return True
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False

    def identify_sections(self):
        """Identify major sections in the PDF"""
        print(f"🔍 Identifying sections in {self.filename}...")

        # Common section headers
        section_patterns = [
            (r'^[A-Z\s]{20,}$', 'HEADER'),
            (r'^(ACCOUNT|Position|Trade|Order|Activity|Statement|Summary)', 'SECTION'),
            (r'^(\d+\.[\s\S]*?)(?=^\d+\.|$)', 'NUMBERED_SECTION'),
        ]

        lines = self.text.split('\n')
        current_section = None

        for i, line in enumerate(lines):
            line_clean = line.strip()
            if not line_clean or len(line_clean) < 3:
                continue

            # Detect section headers
            if len(line_clean) > 20 and line_clean.isupper():
                section_name = line_clean
                current_section = {
                    'name': section_name,
                    'start_line': i,
                    'content': [],
                    'fields': []
                }
                self.sections.append(current_section)
            elif current_section and any(re.match(p, line_clean) for p, _ in section_patterns):
                if current_section and len(current_section['content']) > 0:
                    current_section = None

            if current_section:
                current_section['content'].append(line_clean)

                # Extract field-like patterns (Key: Value)
                if ':' in line and len(line.split(':')) == 2:
                    key, value = line.split(':', 1)
                    current_section['fields'].append((key.strip(), value.strip()))

        print(f"   ✓ Found {len(self.sections)} major sections")
        for section in self.sections:
            print(f"      - {section['name'][:60]}... ({len(section['fields'])} fields)")

        return self.sections

    def extract_tables(self):
        """Extract and analyze tables from PDF"""
        print(f"📊 Extracting tables from {self.filename}...")

        for page_num, page_info in enumerate(self.pages, 1):
            tables = page_info['tables']

            for table_idx, table in enumerate(tables):
                if not table or len(table) == 0:
                    continue

                # Get table dimensions
                rows = len(table)
                cols = max(len(row) for row in table) if table else 0

                # Extract headers (assume first row is header)
                headers = []
                if rows > 0:
                    headers = [str(cell).strip() if cell else '' for cell in table[0]]

                table_info = {
                    'page': page_num,
                    'table_index': table_idx,
                    'rows': rows,
                    'cols': cols,
                    'headers': headers,
                    'data': table[1:] if rows > 1 else [],  # Skip header row
                    'raw': table
                }

                self.tables.append(table_info)
                print(f"   ✓ Page {page_num}, Table {table_idx}: {rows}x{cols}")
                if headers:
                    print(f"      Headers: {headers[:5]}{'...' if len(headers) > 5 else ''}")

        print(f"   ✓ Total tables found: {len(self.tables)}")
        return self.tables

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics"""
        return {
            'filename': self.filename,
            'total_pages': len(self.pdf.pages) if self.pdf else 0,
            'total_text_length': len(self.text),
            'sections_count': len(self.sections),
            'tables_count': len(self.tables),
            'sections': [
                {
                    'name': s['name'],
                    'fields_count': len(s['fields']),
                    'field_names': [f[0] for f in s['fields'][:10]]
                }
                for s in self.sections
            ],
            'tables': [
                {
                    'page': t['page'],
                    'rows': t['rows'],
                    'cols': t['cols'],
                    'headers': t['headers']
                }
                for t in self.tables
            ]
        }

    def close(self):
        """Close PDF"""
        if self.pdf:
            self.pdf.close()


class PDFComparator:
    """Compares two PDF structures"""

    def __init__(self, pdf1: PDFStructureAnalyzer, pdf2: PDFStructureAnalyzer):
        self.pdf1 = pdf1
        self.pdf2 = pdf2
        self.comparison = {}

    def compare(self) -> Dict[str, Any]:
        """Compare two PDFs"""
        print("\n📋 Comparing PDF structures...")

        summary1 = self.pdf1.get_summary()
        summary2 = self.pdf2.get_summary()

        self.comparison = {
            'pdf1': summary1,
            'pdf2': summary2,
            'differences': {
                'page_count': summary1['total_pages'] != summary2['total_pages'],
                'section_count': summary1['sections_count'] != summary2['sections_count'],
                'table_count': summary1['tables_count'] != summary2['tables_count'],
            },
            'sections_comparison': self._compare_sections(),
            'tables_comparison': self._compare_tables(),
        }

        return self.comparison

    def _compare_sections(self) -> List[Dict]:
        """Compare sections between PDFs"""
        sections1 = {s['name']: s for s in self.pdf1.sections}
        sections2 = {s['name']: s for s in self.pdf2.sections}

        all_section_names = set(sections1.keys()) | set(sections2.keys())

        comparison = []
        for name in sorted(all_section_names):
            in_pdf1 = name in sections1
            in_pdf2 = name in sections2

            fields1 = [f[0] for f in sections1[name]['fields']] if in_pdf1 else []
            fields2 = [f[0] for f in sections2[name]['fields']] if in_pdf2 else []

            comparison.append({
                'section_name': name,
                'in_pdf1': in_pdf1,
                'in_pdf2': in_pdf2,
                'fields_pdf1': fields1,
                'fields_pdf2': fields2,
                'field_differences': {
                    'only_in_pdf1': list(set(fields1) - set(fields2)),
                    'only_in_pdf2': list(set(fields2) - set(fields1)),
                }
            })

        return comparison

    def _compare_tables(self) -> List[Dict]:
        """Compare tables between PDFs"""
        comparison = []

        # Group tables by approximate structure
        for i, (t1, t2) in enumerate(zip(self.pdf1.tables, self.pdf2.tables)):
            comparison.append({
                'table_index': i,
                'pdf1': {
                    'page': t1['page'],
                    'rows': t1['rows'],
                    'cols': t1['cols'],
                    'headers': t1['headers']
                },
                'pdf2': {
                    'page': t2['page'],
                    'rows': t2['rows'],
                    'cols': t2['cols'],
                    'headers': t2['headers']
                },
                'headers_match': t1['headers'] == t2['headers'],
                'cols_match': t1['cols'] == t2['cols']
            })

        return comparison


class MarkdownReportGenerator:
    """Generates markdown comparison report"""

    def __init__(self, comparator: PDFComparator):
        self.comparator = comparator
        self.report = []

    def generate(self) -> str:
        """Generate full report"""
        self.report = []

        self._add_header()
        self._add_executive_summary()
        self._add_file_overview()
        self._add_pages_sections()
        self._add_sections_comparison()
        self._add_tables_comparison()
        self._add_field_analysis()
        self._add_parser_recommendations()
        self._add_raw_structure_data()

        return '\n'.join(self.report)

    def _add_header(self):
        """Add document header"""
        self.report.append('# Trading 212 Activity Statement - PDF Structure Analysis\n')
        self.report.append('**Analysis Date:** 2026-09-20')
        self.report.append('**Purpose:** Extract and compare structure of monthly vs. daily Trading 212 Activity Statements\n')

    def _add_executive_summary(self):
        """Add executive summary"""
        c = self.comparator.comparison
        pdf1_summary = c['pdf1']
        pdf2_summary = c['pdf2']

        self.report.append('## 📊 Executive Summary\n')
        self.report.append('| Aspect | PDF 1 (Monthly) | PDF 2 (Daily) | Match? |')
        self.report.append('|--------|-----------------|--------------|--------|')
        self.report.append(f"| **Pages** | {pdf1_summary['total_pages']} | {pdf2_summary['total_pages']} | {'✓' if c['differences']['page_count'] == False else '✗'} |")
        self.report.append(f"| **Sections** | {pdf1_summary['sections_count']} | {pdf2_summary['sections_count']} | {'✓' if c['differences']['section_count'] == False else '✗'} |")
        self.report.append(f"| **Tables** | {pdf1_summary['tables_count']} | {pdf2_summary['tables_count']} | {'✓' if c['differences']['table_count'] == False else '✗'} |")
        self.report.append(f"| **Text Length** | {pdf1_summary['total_text_length']:,} chars | {pdf2_summary['total_text_length']:,} chars | - |\n")

    def _add_file_overview(self):
        """Add file information"""
        self.report.append('## 📁 File Overview\n')
        self.report.append('### PDF 1: Activity-Statement-2026-06-01-2026-06-30.pdf')
        self.report.append('- **Type:** Monthly Activity Statement')
        self.report.append('- **Period:** June 1 - June 30, 2026')
        self.report.append('- **Size:** 395.7 KB')
        self.report.append(f"- **Pages:** {self.comparator.pdf1.get_summary()['total_pages']}\n")

        self.report.append('### PDF 2: Activity-Statement-2026-09-01-2026-09-01.pdf')
        self.report.append('- **Type:** Daily Activity Statement')
        self.report.append('- **Period:** September 1, 2026 (single day)')
        self.report.append('- **Size:** 278.3 KB')
        self.report.append(f"- **Pages:** {self.comparator.pdf2.get_summary()['total_pages']}\n")

    def _add_pages_sections(self):
        """Add page and section details"""
        self.report.append('## 📄 Pages & Sections\n')

        self.report.append('### PDF 1 - Sections Detected\n')
        for section in self.comparator.pdf1.sections:
            self.report.append(f"#### {section['name']}")
            self.report.append(f"- **Fields Found:** {len(section['fields'])}")
            if section['fields']:
                field_names = [f[0] for f in section['fields'][:8]]
                self.report.append(f"- **Sample Fields:** {', '.join(field_names)}")
            self.report.append('')

        self.report.append('### PDF 2 - Sections Detected\n')
        for section in self.comparator.pdf2.sections:
            self.report.append(f"#### {section['name']}")
            self.report.append(f"- **Fields Found:** {len(section['fields'])}")
            if section['fields']:
                field_names = [f[0] for f in section['fields'][:8]]
                self.report.append(f"- **Sample Fields:** {', '.join(field_names)}")
            self.report.append('')

    def _add_sections_comparison(self):
        """Add sections comparison"""
        self.report.append('## 🔄 Section-by-Section Comparison\n')

        for comp in self.comparator.comparison['sections_comparison']:
            name = comp['section_name']
            self.report.append(f"### {name}\n")
            self.report.append(f"- **In PDF 1 (Monthly):** {'Yes' if comp['in_pdf1'] else 'No'}")
            self.report.append(f"- **In PDF 2 (Daily):** {'Yes' if comp['in_pdf2'] else 'No'}\n")

            if comp['in_pdf1']:
                self.report.append(f"**PDF 1 Fields ({len(comp['fields_pdf1'])}):**")
                for field in comp['fields_pdf1'][:10]:
                    self.report.append(f"  - {field}")
                if len(comp['fields_pdf1']) > 10:
                    self.report.append(f"  - ... and {len(comp['fields_pdf1']) - 10} more")
                self.report.append('')

            if comp['in_pdf2']:
                self.report.append(f"**PDF 2 Fields ({len(comp['fields_pdf2'])}):**")
                for field in comp['fields_pdf2'][:10]:
                    self.report.append(f"  - {field}")
                if len(comp['fields_pdf2']) > 10:
                    self.report.append(f"  - ... and {len(comp['fields_pdf2']) - 10} more")
                self.report.append('')

            if comp['field_differences']['only_in_pdf1']:
                self.report.append('**Only in PDF 1:**')
                for field in comp['field_differences']['only_in_pdf1'][:5]:
                    self.report.append(f"  - {field}")
                self.report.append('')

            if comp['field_differences']['only_in_pdf2']:
                self.report.append('**Only in PDF 2:**')
                for field in comp['field_differences']['only_in_pdf2'][:5]:
                    self.report.append(f"  - {field}")
                self.report.append('')

    def _add_tables_comparison(self):
        """Add tables comparison"""
        self.report.append('## 📋 Tables Comparison\n')

        if not self.comparator.comparison['tables_comparison']:
            self.report.append('No tables found in PDFs or table counts differ.\n')
            return

        self.report.append('| Table # | PDF 1 Cols | PDF 2 Cols | Headers Match | Rows PDF 1 | Rows PDF 2 |')
        self.report.append('|---------|-----------|-----------|---------------|-----------|-----------|')

        for comp in self.comparator.comparison['tables_comparison']:
            idx = comp['table_index']
            cols_match = '✓' if comp['cols_match'] else '✗'
            headers_match = '✓' if comp['headers_match'] else '✗'

            self.report.append(
                f"| {idx} | {comp['pdf1']['cols']} | {comp['pdf2']['cols']} | {headers_match} | "
                f"{comp['pdf1']['rows']} | {comp['pdf2']['rows']} |"
            )

        self.report.append('')

        # Detailed table headers
        self.report.append('### Table Headers Detail\n')

        for comp in self.comparator.comparison['tables_comparison']:
            idx = comp['table_index']
            self.report.append(f"#### Table {idx}\n")

            if comp['pdf1']['headers']:
                self.report.append('**PDF 1 Headers:**')
                for header in comp['pdf1']['headers']:
                    self.report.append(f"  - {header}")
                self.report.append('')

            if comp['pdf2']['headers']:
                self.report.append('**PDF 2 Headers:**')
                for header in comp['pdf2']['headers']:
                    self.report.append(f"  - {header}")
                self.report.append('')

    def _add_field_analysis(self):
        """Add detailed field analysis"""
        self.report.append('## 🔍 Field-by-Field Analysis\n')

        all_fields_pdf1 = set()
        all_fields_pdf2 = set()

        for section in self.comparator.pdf1.sections:
            all_fields_pdf1.update([f[0] for f in section['fields']])

        for section in self.comparator.pdf2.sections:
            all_fields_pdf2.update([f[0] for f in section['fields']])

        common_fields = all_fields_pdf1 & all_fields_pdf2
        only_pdf1 = all_fields_pdf1 - all_fields_pdf2
        only_pdf2 = all_fields_pdf2 - all_fields_pdf1

        self.report.append(f"**Total Unique Fields - PDF 1:** {len(all_fields_pdf1)}")
        self.report.append(f"**Total Unique Fields - PDF 2:** {len(all_fields_pdf2)}")
        self.report.append(f"**Common Fields:** {len(common_fields)}")
        self.report.append(f"**Only in PDF 1:** {len(only_pdf1)}")
        self.report.append(f"**Only in PDF 2:** {len(only_pdf2)}\n")

        if only_pdf1:
            self.report.append('### Fields Only in PDF 1 (Monthly)\n')
            for field in sorted(only_pdf1)[:20]:
                self.report.append(f"- {field}")
            if len(only_pdf1) > 20:
                self.report.append(f"- ... and {len(only_pdf1) - 20} more\n")
            else:
                self.report.append('')

        if only_pdf2:
            self.report.append('### Fields Only in PDF 2 (Daily)\n')
            for field in sorted(only_pdf2)[:20]:
                self.report.append(f"- {field}")
            if len(only_pdf2) > 20:
                self.report.append(f"- ... and {len(only_pdf2) - 20} more\n")
            else:
                self.report.append('')

    def _add_parser_recommendations(self):
        """Add parser recommendations"""
        self.report.append('## 🛠️ Parser Recommendations\n')

        self.report.append('### Architecture\n')
        self.report.append('```python')
        self.report.append('class Trading212ActivityParser:')
        self.report.append('    def __init__(self, pdf_path):')
        self.report.append('        self.pdf = pdfplumber.open(pdf_path)')
        self.report.append('        self.is_monthly = self._detect_period()')
        self.report.append('        ')
        self.report.append('    def parse(self):')
        self.report.append('        sections = self._extract_sections()')
        self.report.append('        tables = self._extract_tables()')
        self.report.append('        metadata = self._extract_metadata()')
        self.report.append('        return {sections, tables, metadata}')
        self.report.append('```\n')

        self.report.append('### Key Parsing Steps\n')
        self.report.append('1. **Detect Report Type** - Check for "Monthly" or "Daily" keywords')
        self.report.append('2. **Extract Metadata** - Account info, period, statement date')
        self.report.append('3. **Parse Sections** - Use header detection to identify major sections')
        self.report.append('4. **Extract Tables** - Use pdfplumber table extraction')
        self.report.append('5. **Normalize Data** - Standardize field names across monthly/daily\n')

        self.report.append('### Handling Differences\n')
        self.report.append('- **Daily vs. Monthly:** Create format-agnostic parser or two specific parsers')
        self.report.append('- **Optional Fields:** Many fields only appear in monthly reports')
        self.report.append('- **Table Variations:** Column counts may differ; use column name matching')
        self.report.append('- **Data Types:** Parse numbers, dates, and currency consistently\n')

        self.report.append('### Recommended Libraries\n')
        self.report.append('- **pdfplumber** - Text and table extraction')
        self.report.append('- **pandas** - Table data normalization')
        self.report.append('- **dateutil** - Date parsing')
        self.report.append('- **re** - Pattern matching for field extraction\n')

    def _add_raw_structure_data(self):
        """Add raw structure data as JSON"""
        self.report.append('## 📊 Raw Structure Data (JSON)\n')
        self.report.append('```json')
        self.report.append(json.dumps(self.comparator.comparison, indent=2, default=str))
        self.report.append('```')


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("  Trading 212 Activity Statement - PDF Structure Analyzer")
    print("="*70 + "\n")

    pdf_path_1 = r"C:\claude\401. Trading 212 Hub\reports\Activity-Statement-2026-06-01-2026-06-30.pdf"
    pdf_path_2 = r"C:\claude\401. Trading 212 Hub\reports\Activity-Statement-2026-09-01-2026-09-01.pdf"
    output_path = r"C:\claude\401. Trading 212 Hub\reports\STRUCTURE_ANALYSIS.md"

    # Verify files exist
    for path in [pdf_path_1, pdf_path_2]:
        if not os.path.exists(path):
            print(f"✗ File not found: {path}")
            return False

    # Analyze first PDF
    print("📄 ANALYZING PDF 1 (Monthly)\n")
    analyzer1 = PDFStructureAnalyzer(pdf_path_1)
    if not analyzer1.load():
        return False
    analyzer1.identify_sections()
    analyzer1.extract_tables()

    # Analyze second PDF
    print("\n📄 ANALYZING PDF 2 (Daily)\n")
    analyzer2 = PDFStructureAnalyzer(pdf_path_2)
    if not analyzer2.load():
        return False
    analyzer2.identify_sections()
    analyzer2.extract_tables()

    # Compare
    print("\n" + "="*70)
    comparator = PDFComparator(analyzer1, analyzer2)
    comparator.compare()

    # Generate report
    print("📝 Generating report...")
    generator = MarkdownReportGenerator(comparator)
    report = generator.generate()

    # Save report
    print(f"💾 Saving to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✓ Report saved successfully!")
    print(f"   {len(report):,} characters written")

    # Close PDFs
    analyzer1.close()
    analyzer2.close()

    print("\n" + "="*70)
    print("  ✓ Analysis Complete!")
    print("="*70 + "\n")

    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
