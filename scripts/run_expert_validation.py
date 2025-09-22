#!/usr/bin/env python3
"""
Expert Validation Test Runner

This script runs the complete expert validation suite for AFAS,
executing all validation scripts and generating comprehensive reports.
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

class ExpertValidationRunner:
    """Runs complete expert validation suite."""
    
    def __init__(self):
        self.validation_results = {
            'start_time': datetime.now().isoformat(),
            'validation_scripts': {},
            'overall_status': 'unknown',
            'summary': {
                'total_validations': 0,
                'passed_validations': 0,
                'failed_validations': 0,
                'warnings': 0
            }
        }
        
        # Define validation scripts to run
        self.validation_scripts = [
            {
                'name': 'Agricultural Logic Validation',
                'script': 'scripts/validate_agricultural_logic.py',
                'description': 'Validates core agricultural recommendation logic',
                'required': True
            },
            {
                'name': 'Extension Data Validation',
                'script': 'scripts/validate_against_extension_data.py',
                'description': 'Validates against university extension guidelines',
                'required': True
            },
            {
                'name': 'Agricultural Sources Check',
                'script': 'scripts/check_agricultural_sources.py',
                'description': 'Validates agricultural source citations',
                'required': True
            },
            {
                'name': 'Fertilizer Safety Limits',
                'script': 'scripts/validate_fertilizer_limits.py',
                'description': 'Validates fertilizer rate safety limits',
                'required': True
            },
            {
                'name': 'Dangerous Recommendations Check',
                'script': 'scripts/check_dangerous_recommendations.py',
                'description': 'Detects potentially dangerous recommendations',
                'required': True
            },
            {
                'name': 'Agricultural Tests',
                'script': 'pytest tests/agricultural/ -v --tb=short',
                'description': 'Runs comprehensive agricultural test suite',
                'required': True,
                'is_pytest': True
            }
        ]
    
    def run_validation_script(self, script_info: Dict[str, Any]) -> Tuple[bool, str, str]:
        """Run a single validation script."""
        script_name = script_info['name']
        script_path = script_info['script']
        
        print(f"\n{'='*60}")
        print(f"Running: {script_name}")
        print(f"Script: {script_path}")
        print(f"Description: {script_info['description']}")
        print('='*60)
        
        try:
            # Check if script exists (for non-pytest scripts)
            if not script_info.get('is_pytest', False):
                if not Path(script_path).exists():
                    return False, f"Script not found: {script_path}", ""
            
            # Run the script
            if script_info.get('is_pytest', False):
                # Handle pytest command
                cmd_parts = script_path.split()
                result = subprocess.run(
                    cmd_parts,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
            else:
                # Handle Python script
                result = subprocess.run(
                    [sys.executable, script_path],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
            
            # Check result
            success = result.returncode == 0
            stdout = result.stdout
            stderr = result.stderr
            
            # Print output
            if stdout:
                print("STDOUT:")
                print(stdout)
            
            if stderr:
                print("STDERR:")
                print(stderr)
            
            if success:
                print(f"✅ {script_name} completed successfully")
            else:
                print(f"❌ {script_name} failed with return code {result.returncode}")
            
            return success, stdout, stderr
            
        except subprocess.TimeoutExpired:
            error_msg = f"Script timeout after 5 minutes: {script_path}"
            print(f"⏰ {error_msg}")
            return False, "", error_msg
            
        except Exception as e:
            error_msg = f"Error running script {script_path}: {str(e)}"
            print(f"💥 {error_msg}")
            return False, "", error_msg
    
    def run_all_validations(self) -> bool:
        """Run all validation scripts."""
        print("🌾 AFAS Expert Validation Suite")
        print("=" * 80)
        print(f"Starting comprehensive validation at {self.validation_results['start_time']}")
        print(f"Total validations to run: {len(self.validation_scripts)}")
        
        overall_success = True
        
        for script_info in self.validation_scripts:
            script_name = script_info['name']
            
            # Run the validation
            success, stdout, stderr = self.run_validation_script(script_info)
            
            # Record results
            self.validation_results['validation_scripts'][script_name] = {
                'script_path': script_info['script'],
                'description': script_info['description'],
                'required': script_info['required'],
                'success': success,
                'stdout': stdout,
                'stderr': stderr,
                'timestamp': datetime.now().isoformat()
            }
            
            # Update counters
            self.validation_results['summary']['total_validations'] += 1
            
            if success:
                self.validation_results['summary']['passed_validations'] += 1
            else:
                if script_info['required']:
                    self.validation_results['summary']['failed_validations'] += 1
                    overall_success = False
                else:
                    self.validation_results['summary']['warnings'] += 1
        
        # Determine overall status
        if overall_success:
            if self.validation_results['summary']['warnings'] > 0:
                self.validation_results['overall_status'] = 'passed_with_warnings'
            else:
                self.validation_results['overall_status'] = 'passed'
        else:
            self.validation_results['overall_status'] = 'failed'
        
        return overall_success
    
    def generate_validation_summary(self):
        """Generate and display validation summary."""
        print("\n" + "=" * 80)
        print("🏆 EXPERT VALIDATION SUMMARY")
        print("=" * 80)
        
        summary = self.validation_results['summary']
        overall_status = self.validation_results['overall_status']
        
        # Overall status
        status_icons = {
            'passed': '✅',
            'passed_with_warnings': '⚠️',
            'failed': '❌'
        }
        
        status_icon = status_icons.get(overall_status, '❓')
        print(f"Overall Status: {status_icon} {overall_status.upper().replace('_', ' ')}")
        
        # Summary statistics
        print(f"\nValidation Statistics:")
        print(f"  Total Validations: {summary['total_validations']}")
        print(f"  ✅ Passed: {summary['passed_validations']}")
        print(f"  ❌ Failed: {summary['failed_validations']}")
        print(f"  ⚠️  Warnings: {summary['warnings']}")
        
        # Success rate
        if summary['total_validations'] > 0:
            success_rate = (summary['passed_validations'] / summary['total_validations']) * 100
            print(f"  📊 Success Rate: {success_rate:.1f}%")
        
        # Detailed results
        print(f"\nDetailed Results:")
        for script_name, result in self.validation_results['validation_scripts'].items():
            status_icon = '✅' if result['success'] else '❌'
            required_text = ' (REQUIRED)' if result['required'] else ' (OPTIONAL)'
            print(f"  {status_icon} {script_name}{required_text}")
            print(f"      {result['description']}")
        
        # Failed validations
        failed_validations = [
            name for name, result in self.validation_results['validation_scripts'].items()
            if not result['success'] and result['required']
        ]
        
        if failed_validations:
            print(f"\n❌ Failed Required Validations:")
            for validation in failed_validations:
                print(f"  • {validation}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if overall_status == 'passed':
            print("  ✅ System is ready for production deployment")
            print("  📋 Implement continuous monitoring and feedback collection")
            print("  📅 Schedule quarterly expert reviews")
        elif overall_status == 'passed_with_warnings':
            print("  ⚠️  System can be deployed with monitoring for warning areas")
            print("  🔍 Address warnings before full production rollout")
            print("  📊 Implement enhanced monitoring for warning areas")
        else:
            print("  ❌ System is NOT ready for production deployment")
            print("  🔧 Address all failed validations before deployment")
            print("  🔄 Re-run validation suite after fixes")
        
        # Next steps
        print(f"\n📋 Next Steps:")
        if overall_status == 'passed':
            print("  1. Deploy to production environment")
            print("  2. Implement user feedback collection")
            print("  3. Schedule first quarterly expert review")
            print("  4. Begin Phase 2 development (Questions 6-10)")
        else:
            print("  1. Review failed validation details")
            print("  2. Fix identified issues")
            print("  3. Re-run validation suite")
            print("  4. Obtain expert sign-off before deployment")
    
    def save_validation_results(self):
        """Save detailed validation results to file."""
        # Add completion time
        self.validation_results['end_time'] = datetime.now().isoformat()
        
        # Calculate duration
        start_time = datetime.fromisoformat(self.validation_results['start_time'])
        end_time = datetime.fromisoformat(self.validation_results['end_time'])
        duration = (end_time - start_time).total_seconds()
        self.validation_results['duration_seconds'] = duration
        
        # Save to JSON file
        output_file = 'expert-validation-results.json'
        with open(output_file, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {output_file}")
        
        # Generate HTML report if possible
        try:
            self.generate_html_report()
        except Exception as e:
            print(f"⚠️  Could not generate HTML report: {e}")
    
    def generate_html_report(self):
        """Generate HTML validation report."""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AFAS Expert Validation Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        .header {{ background: #2c5530; color: white; padding: 20px; border-radius: 5px; }}
        .summary {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .status-passed {{ color: #28a745; font-weight: bold; }}
        .status-failed {{ color: #dc3545; font-weight: bold; }}
        .status-warning {{ color: #ffc107; font-weight: bold; }}
        .validation-item {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ddd; }}
        .validation-passed {{ border-left-color: #28a745; }}
        .validation-failed {{ border-left-color: #dc3545; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌾 AFAS Expert Validation Results</h1>
        <p>Autonomous Farm Advisory System - Comprehensive Validation Report</p>
        <p>Generated: {self.validation_results['end_time']}</p>
    </div>

    <div class="summary">
        <h2>📊 Validation Summary</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
                <th>Status</th>
            </tr>
            <tr>
                <td>Overall Status</td>
                <td>{self.validation_results['overall_status'].replace('_', ' ').title()}</td>
                <td>
                    {'<span class="status-passed">✅ PASSED</span>' if self.validation_results['overall_status'] == 'passed' 
                     else '<span class="status-warning">⚠️ PASSED WITH WARNINGS</span>' if self.validation_results['overall_status'] == 'passed_with_warnings'
                     else '<span class="status-failed">❌ FAILED</span>'}
                </td>
            </tr>
            <tr>
                <td>Total Validations</td>
                <td>{self.validation_results['summary']['total_validations']}</td>
                <td>-</td>
            </tr>
            <tr>
                <td>Passed</td>
                <td>{self.validation_results['summary']['passed_validations']}</td>
                <td><span class="status-passed">✅</span></td>
            </tr>
            <tr>
                <td>Failed</td>
                <td>{self.validation_results['summary']['failed_validations']}</td>
                <td>{'<span class="status-failed">❌</span>' if self.validation_results['summary']['failed_validations'] > 0 else '<span class="status-passed">✅</span>'}</td>
            </tr>
            <tr>
                <td>Warnings</td>
                <td>{self.validation_results['summary']['warnings']}</td>
                <td>{'<span class="status-warning">⚠️</span>' if self.validation_results['summary']['warnings'] > 0 else '<span class="status-passed">✅</span>'}</td>
            </tr>
        </table>
    </div>

    <div class="section">
        <h2>🔍 Detailed Validation Results</h2>
        """
        
        for script_name, result in self.validation_results['validation_scripts'].items():
            status_class = 'validation-passed' if result['success'] else 'validation-failed'
            status_icon = '✅' if result['success'] else '❌'
            required_text = ' (REQUIRED)' if result['required'] else ' (OPTIONAL)'
            
            html_content += f"""
        <div class="validation-item {status_class}">
            <h4>{status_icon} {script_name}{required_text}</h4>
            <p><strong>Description:</strong> {result['description']}</p>
            <p><strong>Script:</strong> {result['script_path']}</p>
            <p><strong>Status:</strong> {'Passed' if result['success'] else 'Failed'}</p>
            <p><strong>Timestamp:</strong> {result['timestamp']}</p>
        </div>
            """
        
        html_content += """
    </div>

    <footer style="margin-top: 50px; padding: 20px; background: #f8f9fa; border-radius: 5px;">
        <p><strong>Note:</strong> This validation report is generated automatically. 
        All recommendations should be reviewed by certified agricultural professionals.</p>
        <p><strong>Report Generated:</strong> """ + self.validation_results['end_time'] + """</p>
    </footer>
</body>
</html>
        """
        
        with open('expert-validation-report.html', 'w') as f:
            f.write(html_content)
        
        print(f"📄 HTML report generated: expert-validation-report.html")
    
    def run_complete_validation(self) -> bool:
        """Run complete validation suite and generate reports."""
        try:
            # Run all validations
            success = self.run_all_validations()
            
            # Generate summary
            self.generate_validation_summary()
            
            # Save results
            self.save_validation_results()
            
            # Generate comprehensive report if all validations passed
            if success:
                print("\n🎉 All validations passed! Generating comprehensive report...")
                try:
                    # Run the comprehensive report generator
                    subprocess.run([
                        sys.executable, 
                        'scripts/generate_agricultural_report.py'
                    ], check=True)
                    print("✅ Comprehensive agricultural report generated")
                except Exception as e:
                    print(f"⚠️  Could not generate comprehensive report: {e}")
            
            return success
            
        except KeyboardInterrupt:
            print("\n⚠️  Validation interrupted by user")
            return False
        except Exception as e:
            print(f"\n💥 Validation suite error: {e}")
            return False

def main():
    """Main validation runner function."""
    print("🚀 Starting AFAS Expert Validation Suite...")
    
    runner = ExpertValidationRunner()
    success = runner.run_complete_validation()
    
    if success:
        print("\n🎉 Expert validation completed successfully!")
        print("✅ System is ready for production deployment")
        sys.exit(0)
    else:
        print("\n❌ Expert validation failed!")
        print("🔧 Please address failed validations before deployment")
        sys.exit(1)

if __name__ == "__main__":
    main()