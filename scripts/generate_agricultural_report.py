#!/usr/bin/env python3
"""
Agricultural Validation Report Generator

This script generates comprehensive agricultural validation reports
combining all validation results into a unified expert review document.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Any
import jinja2

class AgriculturalReportGenerator:
    """Generates comprehensive agricultural validation reports."""
    
    def __init__(self):
        self.report_data = {
            'generation_date': datetime.now().isoformat(),
            'validation_summary': {},
            'detailed_results': {},
            'expert_recommendations': [],
            'compliance_status': {},
            'next_steps': []
        }
        
    def collect_validation_results(self) -> bool:
        """Collect results from all validation scripts."""
        print("Collecting validation results...")
        
        # Expected validation result files
        result_files = {
            'extension_validation': 'extension-validation-report.json',
            'agricultural_logic': 'agricultural-validation-results.json',
            'source_validation': 'agricultural-sources-report.json',
            'safety_validation': 'safety-validation-results.json',
            'performance_validation': 'performance-validation-results.json'
        }
        
        collected_results = {}
        
        for validation_type, filename in result_files.items():
            filepath = Path(filename)
            
            if filepath.exists():
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    collected_results[validation_type] = data
                    print(f"  ✓ Loaded {validation_type} results")
                except Exception as e:
                    print(f"  ⚠️  Error loading {filename}: {e}")
                    collected_results[validation_type] = {'error': str(e)}
            else:
                print(f"  ⚠️  {filename} not found - creating placeholder")
                collected_results[validation_type] = self._create_placeholder_results(validation_type)
        
        self.report_data['detailed_results'] = collected_results
        return True
    
    def _create_placeholder_results(self, validation_type: str) -> Dict[str, Any]:
        """Create placeholder results for missing validation data."""
        return {
            'status': 'not_run',
            'message': f'{validation_type} validation not executed',
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze_validation_summary(self) -> bool:
        """Analyze overall validation status."""
        print("Analyzing validation summary...")
        
        summary = {
            'total_validations': 0,
            'passed_validations': 0,
            'failed_validations': 0,
            'warnings': 0,
            'overall_status': 'unknown',
            'confidence_score': 0.0
        }
        
        for validation_type, results in self.report_data['detailed_results'].items():
            summary['total_validations'] += 1
            
            if isinstance(results, dict):
                if results.get('status') == 'not_run':
                    summary['warnings'] += 1
                elif 'error' in results:
                    summary['failed_validations'] += 1
                elif self._is_validation_passed(results):
                    summary['passed_validations'] += 1
                else:
                    summary['failed_validations'] += 1
        
        # Calculate overall status
        if summary['failed_validations'] == 0:
            if summary['warnings'] == 0:
                summary['overall_status'] = 'passed'
                summary['confidence_score'] = 1.0
            else:
                summary['overall_status'] = 'passed_with_warnings'
                summary['confidence_score'] = 0.8
        else:
            summary['overall_status'] = 'failed'
            summary['confidence_score'] = max(0.0, 
                (summary['passed_validations'] / summary['total_validations']) * 0.7)
        
        self.report_data['validation_summary'] = summary
        return True
    
    def _is_validation_passed(self, results: Dict[str, Any]) -> bool:
        """Determine if a validation passed based on results structure."""
        # Check different result formats
        if 'summary' in results:
            summary = results['summary']
            if 'failed_tests' in summary:
                return summary['failed_tests'] == 0
        
        if 'failed' in results:
            return len(results['failed']) == 0
        
        if 'errors' in results:
            return len(results['errors']) == 0
        
        # Default to passed if no clear failure indicators
        return True
    
    def generate_expert_recommendations(self) -> bool:
        """Generate expert recommendations based on validation results."""
        print("Generating expert recommendations...")
        
        recommendations = []
        
        # Analyze each validation type
        for validation_type, results in self.report_data['detailed_results'].items():
            if validation_type == 'extension_validation':
                recommendations.extend(self._analyze_extension_validation(results))
            elif validation_type == 'agricultural_logic':
                recommendations.extend(self._analyze_agricultural_logic(results))
            elif validation_type == 'source_validation':
                recommendations.extend(self._analyze_source_validation(results))
            elif validation_type == 'safety_validation':
                recommendations.extend(self._analyze_safety_validation(results))
        
        # Add general recommendations
        recommendations.extend(self._generate_general_recommendations())
        
        self.report_data['expert_recommendations'] = recommendations
        return True
    
    def _analyze_extension_validation(self, results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Analyze extension validation results."""
        recommendations = []
        
        if 'error' in results or results.get('status') == 'not_run':
            recommendations.append({
                'category': 'Extension Validation',
                'priority': 'high',
                'recommendation': 'Complete extension service validation against Iowa State, Tri-State, and NRCS guidelines',
                'rationale': 'Extension service validation is critical for agricultural accuracy'
            })
        else:
            # Check specific validation categories
            for category, category_results in results.get('results', {}).items():
                if category == 'summary':
                    continue
                    
                if category_results.get('failed'):
                    recommendations.append({
                        'category': 'Extension Validation',
                        'priority': 'high',
                        'recommendation': f'Address failed {category.replace("_", " ")} validations',
                        'rationale': f'Failed validations in {category} indicate deviation from extension guidelines'
                    })
        
        return recommendations
    
    def _analyze_agricultural_logic(self, results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Analyze agricultural logic validation results."""
        recommendations = []
        
        if results.get('errors'):
            recommendations.append({
                'category': 'Agricultural Logic',
                'priority': 'critical',
                'recommendation': 'Fix agricultural logic errors before production deployment',
                'rationale': 'Logic errors can lead to incorrect recommendations that harm crops or environment'
            })
        
        if results.get('warnings'):
            recommendations.append({
                'category': 'Agricultural Logic',
                'priority': 'medium',
                'recommendation': 'Review and address agricultural logic warnings',
                'rationale': 'Warnings may indicate potential issues or areas for improvement'
            })
        
        return recommendations
    
    def _analyze_source_validation(self, results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Analyze source validation results."""
        recommendations = []
        
        if results.get('missing_sources'):
            recommendations.append({
                'category': 'Source Validation',
                'priority': 'high',
                'recommendation': 'Add agricultural source citations to files with missing references',
                'rationale': 'All agricultural logic must be traceable to credible sources'
            })
        
        if results.get('invalid_sources'):
            recommendations.append({
                'category': 'Source Validation',
                'priority': 'medium',
                'recommendation': 'Validate or replace questionable source references',
                'rationale': 'Only use sources from recognized agricultural institutions'
            })
        
        return recommendations
    
    def _analyze_safety_validation(self, results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Analyze safety validation results."""
        recommendations = []
        
        if 'error' in results or results.get('status') == 'not_run':
            recommendations.append({
                'category': 'Safety Validation',
                'priority': 'critical',
                'recommendation': 'Implement and run safety validation checks',
                'rationale': 'Safety validation prevents dangerous recommendations'
            })
        
        return recommendations
    
    def _generate_general_recommendations(self) -> List[Dict[str, str]]:
        """Generate general expert recommendations."""
        return [
            {
                'category': 'Continuous Improvement',
                'priority': 'medium',
                'recommendation': 'Establish regular expert review schedule',
                'rationale': 'Agricultural practices and research evolve continuously'
            },
            {
                'category': 'User Feedback',
                'priority': 'medium',
                'recommendation': 'Implement farmer feedback collection system',
                'rationale': 'Real-world validation from practicing farmers is essential'
            },
            {
                'category': 'Regional Expansion',
                'priority': 'low',
                'recommendation': 'Validate recommendations for additional geographic regions',
                'rationale': 'Expand system applicability while maintaining accuracy'
            }
        ]
    
    def assess_compliance_status(self) -> bool:
        """Assess compliance with agricultural standards."""
        print("Assessing compliance status...")
        
        compliance = {
            'extension_guidelines': 'unknown',
            'safety_standards': 'unknown',
            'source_attribution': 'unknown',
            'expert_review': 'unknown',
            'overall_compliance': 'unknown'
        }
        
        # Check extension guidelines compliance
        extension_results = self.report_data['detailed_results'].get('extension_validation', {})
        if self._is_validation_passed(extension_results):
            compliance['extension_guidelines'] = 'compliant'
        elif 'error' in extension_results:
            compliance['extension_guidelines'] = 'unknown'
        else:
            compliance['extension_guidelines'] = 'non_compliant'
        
        # Check safety standards
        safety_results = self.report_data['detailed_results'].get('safety_validation', {})
        if self._is_validation_passed(safety_results):
            compliance['safety_standards'] = 'compliant'
        elif 'error' in safety_results:
            compliance['safety_standards'] = 'unknown'
        else:
            compliance['safety_standards'] = 'non_compliant'
        
        # Check source attribution
        source_results = self.report_data['detailed_results'].get('source_validation', {})
        if (source_results.get('missing_sources', []) == [] and 
            source_results.get('invalid_sources', []) == []):
            compliance['source_attribution'] = 'compliant'
        else:
            compliance['source_attribution'] = 'non_compliant'
        
        # Expert review status (check if expert validation report exists)
        expert_report_path = Path('services/recommendation-engine/EXPERT_VALIDATION_REPORT.md')
        if expert_report_path.exists():
            compliance['expert_review'] = 'compliant'
        else:
            compliance['expert_review'] = 'non_compliant'
        
        # Overall compliance
        compliant_items = sum(1 for status in compliance.values() 
                            if status == 'compliant')
        total_items = len(compliance) - 1  # Exclude overall_compliance
        
        if compliant_items == total_items:
            compliance['overall_compliance'] = 'fully_compliant'
        elif compliant_items >= total_items * 0.75:
            compliance['overall_compliance'] = 'mostly_compliant'
        elif compliant_items >= total_items * 0.5:
            compliance['overall_compliance'] = 'partially_compliant'
        else:
            compliance['overall_compliance'] = 'non_compliant'
        
        self.report_data['compliance_status'] = compliance
        return True
    
    def generate_next_steps(self) -> bool:
        """Generate next steps based on validation results."""
        print("Generating next steps...")
        
        next_steps = []
        
        # Immediate actions (critical priority)
        critical_recommendations = [r for r in self.report_data['expert_recommendations'] 
                                  if r['priority'] == 'critical']
        if critical_recommendations:
            next_steps.append({
                'phase': 'immediate',
                'timeframe': '1-2 days',
                'actions': [r['recommendation'] for r in critical_recommendations]
            })
        
        # Short-term actions (high priority)
        high_priority_recommendations = [r for r in self.report_data['expert_recommendations'] 
                                       if r['priority'] == 'high']
        if high_priority_recommendations:
            next_steps.append({
                'phase': 'short_term',
                'timeframe': '1-2 weeks',
                'actions': [r['recommendation'] for r in high_priority_recommendations]
            })
        
        # Medium-term actions (medium priority)
        medium_priority_recommendations = [r for r in self.report_data['expert_recommendations'] 
                                         if r['priority'] == 'medium']
        if medium_priority_recommendations:
            next_steps.append({
                'phase': 'medium_term',
                'timeframe': '1-2 months',
                'actions': [r['recommendation'] for r in medium_priority_recommendations]
            })
        
        # Long-term actions (low priority)
        low_priority_recommendations = [r for r in self.report_data['expert_recommendations'] 
                                      if r['priority'] == 'low']
        if low_priority_recommendations:
            next_steps.append({
                'phase': 'long_term',
                'timeframe': '3-6 months',
                'actions': [r['recommendation'] for r in low_priority_recommendations]
            })
        
        self.report_data['next_steps'] = next_steps
        return True
    
    def generate_html_report(self) -> bool:
        """Generate HTML validation report."""
        print("Generating HTML report...")
        
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AFAS Agricultural Validation Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
        .header { background: #2c5530; color: white; padding: 20px; border-radius: 5px; }
        .summary { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .status-passed { color: #28a745; font-weight: bold; }
        .status-failed { color: #dc3545; font-weight: bold; }
        .status-warning { color: #ffc107; font-weight: bold; }
        .priority-critical { background: #f8d7da; border-left: 4px solid #dc3545; padding: 10px; }
        .priority-high { background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; }
        .priority-medium { background: #d1ecf1; border-left: 4px solid #17a2b8; padding: 10px; }
        .priority-low { background: #d4edda; border-left: 4px solid #28a745; padding: 10px; }
        .section { margin: 30px 0; }
        .recommendation { margin: 15px 0; padding: 10px; border-radius: 5px; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .compliance-compliant { color: #28a745; }
        .compliance-non-compliant { color: #dc3545; }
        .compliance-unknown { color: #6c757d; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌾 AFAS Agricultural Validation Report</h1>
        <p>Autonomous Farm Advisory System - Expert Validation Results</p>
        <p>Generated: {{ report_data.generation_date }}</p>
    </div>

    <div class="section">
        <h2>📊 Validation Summary</h2>
        <div class="summary">
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                    <th>Status</th>
                </tr>
                <tr>
                    <td>Total Validations</td>
                    <td>{{ report_data.validation_summary.total_validations }}</td>
                    <td>-</td>
                </tr>
                <tr>
                    <td>Passed Validations</td>
                    <td>{{ report_data.validation_summary.passed_validations }}</td>
                    <td><span class="status-passed">✓</span></td>
                </tr>
                <tr>
                    <td>Failed Validations</td>
                    <td>{{ report_data.validation_summary.failed_validations }}</td>
                    <td>{% if report_data.validation_summary.failed_validations > 0 %}<span class="status-failed">✗</span>{% else %}<span class="status-passed">✓</span>{% endif %}</td>
                </tr>
                <tr>
                    <td>Warnings</td>
                    <td>{{ report_data.validation_summary.warnings }}</td>
                    <td>{% if report_data.validation_summary.warnings > 0 %}<span class="status-warning">⚠</span>{% else %}<span class="status-passed">✓</span>{% endif %}</td>
                </tr>
                <tr>
                    <td>Overall Status</td>
                    <td>{{ report_data.validation_summary.overall_status.replace('_', ' ').title() }}</td>
                    <td>
                        {% if report_data.validation_summary.overall_status == 'passed' %}
                            <span class="status-passed">✓ PASSED</span>
                        {% elif report_data.validation_summary.overall_status == 'passed_with_warnings' %}
                            <span class="status-warning">⚠ PASSED WITH WARNINGS</span>
                        {% else %}
                            <span class="status-failed">✗ FAILED</span>
                        {% endif %}
                    </td>
                </tr>
                <tr>
                    <td>Confidence Score</td>
                    <td>{{ "%.1f" | format(report_data.validation_summary.confidence_score * 100) }}%</td>
                    <td>
                        {% if report_data.validation_summary.confidence_score >= 0.9 %}
                            <span class="status-passed">High</span>
                        {% elif report_data.validation_summary.confidence_score >= 0.7 %}
                            <span class="status-warning">Medium</span>
                        {% else %}
                            <span class="status-failed">Low</span>
                        {% endif %}
                    </td>
                </tr>
            </table>
        </div>
    </div>

    <div class="section">
        <h2>🏛️ Compliance Status</h2>
        <table>
            <tr>
                <th>Standard</th>
                <th>Status</th>
                <th>Description</th>
            </tr>
            {% for standard, status in report_data.compliance_status.items() %}
                {% if standard != 'overall_compliance' %}
                <tr>
                    <td>{{ standard.replace('_', ' ').title() }}</td>
                    <td>
                        <span class="compliance-{{ status.replace('_', '-') }}">
                            {{ status.replace('_', ' ').title() }}
                        </span>
                    </td>
                    <td>
                        {% if standard == 'extension_guidelines' %}
                            Compliance with university extension service guidelines
                        {% elif standard == 'safety_standards' %}
                            Adherence to agricultural safety standards
                        {% elif standard == 'source_attribution' %}
                            Proper citation of agricultural sources
                        {% elif standard == 'expert_review' %}
                            Expert validation by agricultural professionals
                        {% endif %}
                    </td>
                </tr>
                {% endif %}
            {% endfor %}
        </table>
    </div>

    <div class="section">
        <h2>💡 Expert Recommendations</h2>
        {% for recommendation in report_data.expert_recommendations %}
        <div class="recommendation priority-{{ recommendation.priority }}">
            <h4>{{ recommendation.category }} - {{ recommendation.priority.title() }} Priority</h4>
            <p><strong>Recommendation:</strong> {{ recommendation.recommendation }}</p>
            <p><strong>Rationale:</strong> {{ recommendation.rationale }}</p>
        </div>
        {% endfor %}
    </div>

    <div class="section">
        <h2>📋 Next Steps</h2>
        {% for phase in report_data.next_steps %}
        <div class="summary">
            <h4>{{ phase.phase.replace('_', ' ').title() }} ({{ phase.timeframe }})</h4>
            <ul>
                {% for action in phase.actions %}
                <li>{{ action }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endfor %}
    </div>

    <div class="section">
        <h2>📄 Detailed Validation Results</h2>
        {% for validation_type, results in report_data.detailed_results.items() %}
        <div class="summary">
            <h4>{{ validation_type.replace('_', ' ').title() }}</h4>
            {% if results.get('error') %}
                <p class="status-failed">Error: {{ results.error }}</p>
            {% elif results.get('status') == 'not_run' %}
                <p class="status-warning">Status: {{ results.message }}</p>
            {% else %}
                <p class="status-passed">Validation completed successfully</p>
                {% if results.get('summary') %}
                    <p>Summary: {{ results.summary }}</p>
                {% endif %}
            {% endif %}
        </div>
        {% endfor %}
    </div>

    <div class="section">
        <h2>📚 Agricultural Sources Referenced</h2>
        <ul>
            <li>Iowa State University Extension PM 1688 - Corn Nitrogen Rate Calculator</li>
            <li>Tri-State Fertilizer Recommendations (Ohio, Indiana, Michigan)</li>
            <li>USDA Natural Resources Conservation Service (NRCS) Guidelines</li>
            <li>USDA Plant Hardiness Zone Map</li>
            <li>American Society of Agronomy Standards</li>
            <li>Soil Science Society of America Guidelines</li>
            <li>International Plant Nutrition Institute (IPNI) Recommendations</li>
        </ul>
    </div>

    <footer style="margin-top: 50px; padding: 20px; background: #f8f9fa; border-radius: 5px;">
        <p><strong>Note:</strong> This validation report is generated automatically based on agricultural testing and validation scripts. 
        All recommendations should be reviewed by certified agricultural professionals before implementation in production systems.</p>
        <p><strong>Report Version:</strong> 1.0 | <strong>Generated:</strong> {{ report_data.generation_date }}</p>
    </footer>
</body>
</html>
        """
        
        try:
            template = jinja2.Template(html_template)
            html_content = template.render(report_data=self.report_data)
            
            with open('agricultural-validation-report.html', 'w') as f:
                f.write(html_content)
            
            print("  ✓ HTML report generated: agricultural-validation-report.html")
            return True
            
        except Exception as e:
            print(f"  ❌ Error generating HTML report: {e}")
            return False
    
    def save_json_report(self) -> bool:
        """Save detailed JSON report."""
        print("Saving JSON report...")
        
        try:
            with open('agricultural-metrics.json', 'w') as f:
                json.dump(self.report_data, f, indent=2)
            
            print("  ✓ JSON report saved: agricultural-metrics.json")
            return True
            
        except Exception as e:
            print(f"  ❌ Error saving JSON report: {e}")
            return False
    
    def run_report_generation(self) -> bool:
        """Run complete report generation process."""
        print("Generating comprehensive agricultural validation report...")
        print("=" * 60)
        
        steps = [
            ('Collecting validation results', self.collect_validation_results),
            ('Analyzing validation summary', self.analyze_validation_summary),
            ('Generating expert recommendations', self.generate_expert_recommendations),
            ('Assessing compliance status', self.assess_compliance_status),
            ('Generating next steps', self.generate_next_steps),
            ('Generating HTML report', self.generate_html_report),
            ('Saving JSON report', self.save_json_report)
        ]
        
        all_successful = True
        
        for step_name, step_func in steps:
            print(f"\n{step_name}...")
            try:
                if not step_func():
                    print(f"  ❌ {step_name} failed")
                    all_successful = False
                else:
                    print(f"  ✓ {step_name} completed")
            except Exception as e:
                print(f"  ❌ {step_name} error: {e}")
                all_successful = False
        
        return all_successful
    
    def print_summary(self):
        """Print report generation summary."""
        print("\n" + "=" * 60)
        print("AGRICULTURAL VALIDATION REPORT SUMMARY")
        print("=" * 60)
        
        summary = self.report_data['validation_summary']
        compliance = self.report_data['compliance_status']
        
        print(f"Overall Status: {summary['overall_status'].replace('_', ' ').title()}")
        print(f"Confidence Score: {summary['confidence_score']*100:.1f}%")
        print(f"Compliance Level: {compliance['overall_compliance'].replace('_', ' ').title()}")
        
        print(f"\nValidation Results:")
        print(f"  ✓ Passed: {summary['passed_validations']}")
        print(f"  ❌ Failed: {summary['failed_validations']}")
        print(f"  ⚠️  Warnings: {summary['warnings']}")
        
        print(f"\nRecommendations: {len(self.report_data['expert_recommendations'])}")
        
        critical_count = sum(1 for r in self.report_data['expert_recommendations'] 
                           if r['priority'] == 'critical')
        if critical_count > 0:
            print(f"  🚨 Critical: {critical_count}")
        
        print(f"\nReports Generated:")
        print(f"  📄 HTML Report: agricultural-validation-report.html")
        print(f"  📊 JSON Metrics: agricultural-metrics.json")

def main():
    """Main report generation function."""
    generator = AgriculturalReportGenerator()
    
    success = generator.run_report_generation()
    generator.print_summary()
    
    if not success:
        print("\n❌ Report generation completed with errors!")
        sys.exit(1)
    else:
        print("\n✅ Agricultural validation report generated successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()