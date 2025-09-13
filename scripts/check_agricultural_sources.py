#!/usr/bin/env python3
"""
Agricultural Sources Validation Script

This script checks that all agricultural recommendations are properly
sourced and reference credible agricultural institutions.
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Set

class AgriculturalSourcesChecker:
    """Validates agricultural sources and references."""
    
    def __init__(self):
        self.results = {
            'valid_sources': [],
            'missing_sources': [],
            'invalid_sources': [],
            'warnings': [],
            'total_files_checked': 0
        }
        
        # Approved agricultural sources
        self.approved_sources = {
            # University Extension Services
            'Iowa State University Extension',
            'University of Illinois Extension',
            'Ohio State University Extension',
            'Purdue University Extension',
            'University of Wisconsin Extension',
            'University of Minnesota Extension',
            'University of Nebraska Extension',
            'Kansas State University Extension',
            'University of Missouri Extension',
            'Michigan State University Extension',
            'Penn State Extension',
            'Cornell Cooperative Extension',
            'University of California Extension',
            'Texas A&M AgriLife Extension',
            'University of Florida Extension',
            
            # Government Agencies
            'USDA Natural Resources Conservation Service',
            'USDA Economic Research Service',
            'USDA National Agricultural Statistics Service',
            'NRCS',
            'USDA',
            'EPA',
            'NOAA',
            
            # Professional Organizations
            'American Society of Agronomy',
            'Soil Science Society of America',
            'Crop Science Society of America',
            'International Plant Nutrition Institute',
            'IPNI',
            'International Fertilizer Association',
            'Certified Crop Advisor',
            'CCA',
            
            # Research Institutions
            'CIMMYT',
            'CGIAR',
            'FAO',
            'Food and Agriculture Organization',
            
            # Industry Standards
            'Tri-State Fertilizer Recommendations',
            'North Central Regional Committee',
            'Southern Regional Committee'
        }
    
    def check_python_files(self) -> bool:
        """Check Python files for agricultural source references."""
        print("Checking Python files for agricultural sources...")
        
        python_files = []
        services_dir = Path("services")
        
        if services_dir.exists():
            python_files.extend(services_dir.rglob("*.py"))
        
        tests_dir = Path("tests")
        if tests_dir.exists():
            python_files.extend(tests_dir.rglob("*.py"))
        
        files_with_sources = 0
        files_needing_sources = []
        
        for py_file in python_files:
            self.results['total_files_checked'] += 1
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Skip test files and __init__.py files
                if py_file.name.startswith('test_') or py_file.name == '__init__.py':
                    continue
                
                # Check if file contains agricultural logic
                agricultural_keywords = [
                    'fertilizer', 'nitrogen', 'phosphorus', 'potassium',
                    'soil_ph', 'crop', 'yield', 'nutrient', 'lime',
                    'recommendation', 'agricultural'
                ]
                
                has_agricultural_content = any(
                    keyword in content.lower() for keyword in agricultural_keywords
                )
                
                if has_agricultural_content:
                    # Check for source references
                    sources_found = self._find_sources_in_content(content)
                    
                    if sources_found:
                        files_with_sources += 1
                        self.results['valid_sources'].extend(sources_found)
                        print(f"  ✓ {py_file}: {len(sources_found)} sources found")
                    else:
                        files_needing_sources.append(str(py_file))
                        print(f"  ⚠️  {py_file}: No agricultural sources found")
                
            except Exception as e:
                self.results['warnings'].append(f"Error reading {py_file}: {e}")
        
        if files_needing_sources:
            self.results['missing_sources'] = files_needing_sources
            
        return len(files_needing_sources) == 0
    
    def _find_sources_in_content(self, content: str) -> List[str]:
        """Find agricultural sources referenced in content."""
        found_sources = []
        
        # Look for source references in comments and docstrings
        source_patterns = [
            r'# Source: (.+)',
            r'# Reference: (.+)',
            r'# Based on: (.+)',
            r'""".*?References?:(.+?)"""',
            r'""".*?Sources?:(.+?)"""',
            r'Agricultural References?:(.+?)(?:\n|$)',
            r'Extension Guidelines?:(.+?)(?:\n|$)'
        ]
        
        for pattern in source_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Clean up the match
                source_text = match.strip()
                
                # Check if it matches approved sources
                for approved_source in self.approved_sources:
                    if approved_source.lower() in source_text.lower():
                        found_sources.append(approved_source)
        
        return list(set(found_sources))  # Remove duplicates
    
    def check_documentation_sources(self) -> bool:
        """Check documentation files for agricultural sources."""
        print("Checking documentation for agricultural sources...")
        
        doc_files = [
            '.kiro/specs/farm-advisory-system-requirements.md',
            '.kiro/specs/technical-architecture.md',
            '.kiro/specs/implementation-plan.md',
            'README.md'
        ]
        
        docs_with_sources = 0
        
        for doc_file in doc_files:
            doc_path = Path(doc_file)
            if not doc_path.exists():
                continue
                
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                sources_found = self._find_sources_in_content(content)
                
                if sources_found:
                    docs_with_sources += 1
                    self.results['valid_sources'].extend(sources_found)
                    print(f"  ✓ {doc_file}: {len(sources_found)} sources found")
                else:
                    print(f"  ⚠️  {doc_file}: No agricultural sources found")
                    
            except Exception as e:
                self.results['warnings'].append(f"Error reading {doc_file}: {e}")
        
        return True  # Documentation sources are not critical
    
    def validate_source_credibility(self) -> bool:
        """Validate that all found sources are credible."""
        print("Validating source credibility...")
        
        all_found_sources = set(self.results['valid_sources'])
        invalid_sources = []
        
        for source in all_found_sources:
            if not any(approved.lower() in source.lower() 
                      for approved in self.approved_sources):
                invalid_sources.append(source)
        
        if invalid_sources:
            self.results['invalid_sources'] = invalid_sources
            self.results['warnings'].append(
                f"Sources need validation: {invalid_sources}"
            )
        
        valid_source_count = len(all_found_sources) - len(invalid_sources)
        print(f"  ✓ {valid_source_count} valid sources found")
        
        return len(invalid_sources) == 0
    
    def check_source_diversity(self) -> bool:
        """Check that sources represent diverse agricultural expertise."""
        print("Checking source diversity...")
        
        all_sources = set(self.results['valid_sources'])
        
        source_categories = {
            'university_extension': 0,
            'government_agency': 0,
            'professional_organization': 0,
            'research_institution': 0
        }
        
        for source in all_sources:
            source_lower = source.lower()
            
            if 'extension' in source_lower or 'university' in source_lower:
                source_categories['university_extension'] += 1
            elif any(agency in source_lower for agency in ['usda', 'nrcs', 'epa', 'noaa']):
                source_categories['government_agency'] += 1
            elif any(org in source_lower for org in ['society', 'association', 'institute']):
                source_categories['professional_organization'] += 1
            elif any(inst in source_lower for inst in ['cimmyt', 'cgiar', 'fao']):
                source_categories['research_institution'] += 1
        
        # Check for minimum diversity
        categories_with_sources = sum(1 for count in source_categories.values() if count > 0)
        
        if categories_with_sources < 2:
            self.results['warnings'].append(
                "Limited source diversity - consider adding sources from different categories"
            )
        
        print(f"  ✓ Source diversity: {categories_with_sources}/4 categories represented")
        return True
    
    def run_all_checks(self) -> bool:
        """Run all agricultural source checks."""
        print("Running agricultural source validation...")
        print("=" * 50)
        
        checks = [
            self.check_python_files,
            self.check_documentation_sources,
            self.validate_source_credibility,
            self.check_source_diversity
        ]
        
        all_passed = True
        for check in checks:
            if not check():
                all_passed = False
        
        self._print_results()
        return all_passed
    
    def _print_results(self):
        """Print source validation results."""
        print("\n" + "=" * 50)
        print("AGRICULTURAL SOURCES VALIDATION RESULTS")
        print("=" * 50)
        
        print(f"Files checked: {self.results['total_files_checked']}")
        print(f"Valid sources found: {len(set(self.results['valid_sources']))}")
        print(f"Missing sources: {len(self.results['missing_sources'])}")
        print(f"Invalid sources: {len(self.results['invalid_sources'])}")
        print(f"Warnings: {len(self.results['warnings'])}")
        
        if self.results['valid_sources']:
            unique_sources = set(self.results['valid_sources'])
            print(f"\n✅ VALID SOURCES ({len(unique_sources)}):")
            for source in sorted(unique_sources):
                print(f"  • {source}")
        
        if self.results['missing_sources']:
            print(f"\n⚠️  FILES MISSING SOURCES ({len(self.results['missing_sources'])}):")
            for file_path in self.results['missing_sources']:
                print(f"  • {file_path}")
        
        if self.results['invalid_sources']:
            print(f"\n❌ INVALID SOURCES ({len(self.results['invalid_sources'])}):")
            for source in self.results['invalid_sources']:
                print(f"  • {source}")
        
        if self.results['warnings']:
            print(f"\n⚠️  WARNINGS ({len(self.results['warnings'])}):")
            for warning in self.results['warnings']:
                print(f"  • {warning}")
        
        # Save results to file
        with open('agricultural-sources-report.json', 'w') as f:
            json.dump(self.results, f, indent=2)

def main():
    """Main source validation function."""
    checker = AgriculturalSourcesChecker()
    
    success = checker.run_all_checks()
    
    if not success:
        print("\n❌ Agricultural source validation failed!")
        print("Please ensure all agricultural logic references credible sources.")
        sys.exit(1)
    else:
        print("\n✅ Agricultural source validation passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()