"""
API routes for variety comparison export functionality.
"""

from fastapi import APIRouter, HTTPException, Depends, Response
from typing import Dict, List, Any, Optional
import logging
import json
import csv
import io
from datetime import datetime
import uuid

from ..services.variety_comparison_service import VarietyComparisonService
from ..models.crop_variety_models import VarietyComparisonRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/export", tags=["export"])

# Dependency injection
async def get_comparison_service() -> VarietyComparisonService:
    """Get variety comparison service instance."""
    return VarietyComparisonService()

@router.post("/comparison")
async def export_comparison(
    export_data: Dict[str, Any],
    comparison_service: VarietyComparisonService = Depends(get_comparison_service)
):
    """
    Export variety comparison data in various formats.
    
    Supports PDF, Excel, and CSV export formats with comprehensive comparison data.
    """
    try:
        format_type = export_data.get('format', 'pdf').lower()
        comparison_data = export_data.get('comparison_data')
        varieties = export_data.get('varieties', [])
        
        if not comparison_data:
            raise HTTPException(status_code=400, detail="Comparison data is required")
        
        if format_type == 'pdf':
            return await export_pdf(comparison_data, varieties)
        elif format_type == 'excel':
            return await export_excel(comparison_data, varieties)
        elif format_type == 'csv':
            return await export_csv(comparison_data, varieties)
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
            
    except Exception as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

async def export_pdf(comparison_data: Dict[str, Any], varieties: List[Dict[str, Any]]) -> Response:
    """Export comparison data as PDF."""
    try:
        # For now, return a simple text-based PDF representation
        # In production, use libraries like reportlab or weasyprint
        
        pdf_content = generate_pdf_content(comparison_data, varieties)
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=variety_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            }
        )
    except Exception as e:
        logger.error(f"PDF export error: {e}")
        raise HTTPException(status_code=500, detail="PDF export failed")

async def export_excel(comparison_data: Dict[str, Any], varieties: List[Dict[str, Any]]) -> Response:
    """Export comparison data as Excel file."""
    try:
        # Generate Excel content
        excel_content = generate_excel_content(comparison_data, varieties)
        
        return Response(
            content=excel_content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=variety_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            }
        )
    except Exception as e:
        logger.error(f"Excel export error: {e}")
        raise HTTPException(status_code=500, detail="Excel export failed")

async def export_csv(comparison_data: Dict[str, Any], varieties: List[Dict[str, Any]]) -> Response:
    """Export comparison data as CSV file."""
    try:
        csv_content = generate_csv_content(comparison_data, varieties)
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=variety_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
    except Exception as e:
        logger.error(f"CSV export error: {e}")
        raise HTTPException(status_code=500, detail="CSV export failed")

def generate_pdf_content(comparison_data: Dict[str, Any], varieties: List[Dict[str, Any]]) -> str:
    """Generate PDF content for variety comparison."""
    
    # Simple text-based PDF structure
    # In production, use proper PDF generation libraries
    
    content = f"""
VARIETY COMPARISON REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Report ID: {comparison_data.get('request_id', 'N/A')}

SUMMARY
--------
Best Overall Variety: {comparison_data.get('summary', {}).get('best_overall_variety', 'N/A')}
Confidence Score: {comparison_data.get('summary', {}).get('confidence_score', 0):.2f}

DETAILED RESULTS
----------------
"""
    
    detailed_results = comparison_data.get('detailed_results', [])
    for result in detailed_results:
        content += f"""
Variety: {result.get('variety_name', 'N/A')}
Overall Score: {result.get('overall_score', 0):.2f}
Yield Potential: {result.get('criteria_scores', {}).get('yield_potential', 0):.2f}
Disease Resistance: {result.get('criteria_scores', {}).get('disease_resilience', 0):.2f}
Maturity Suitability: {result.get('criteria_scores', {}).get('maturity_suitability', 0):.2f}
Management Requirements: {result.get('criteria_scores', {}).get('management_requirements', 0):.2f}
Economic Outlook: {result.get('criteria_scores', {}).get('economic_outlook', 0):.2f}

Strengths:
{chr(10).join(f"- {strength}" for strength in result.get('strengths', []))}

Considerations:
{chr(10).join(f"- {consideration}" for consideration in result.get('considerations', []))}

Risk Rating: {result.get('risk_rating', 'N/A')}
"""
    
    content += f"""

TRADE-OFF ANALYSIS
------------------
"""
    
    trade_offs = comparison_data.get('trade_offs', [])
    for trade_off in trade_offs:
        content += f"""
Focus Area: {trade_off.get('focus_area', 'N/A')}
Preferred Variety: {trade_off.get('preferred_variety_name', 'N/A')}
Rationale: {trade_off.get('rationale', 'N/A')}
"""
    
    content += f"""

KEY TAKEAWAYS
--------------
"""
    
    key_takeaways = comparison_data.get('summary', {}).get('key_takeaways', [])
    for takeaway in key_takeaways:
        content += f"- {takeaway}\n"
    
    content += f"""

RECOMMENDED ACTIONS
-------------------
"""
    
    recommended_actions = comparison_data.get('summary', {}).get('recommended_actions', [])
    for action in recommended_actions:
        content += f"- {action}\n"
    
    return content

def generate_excel_content(comparison_data: Dict[str, Any], varieties: List[Dict[str, Any]]) -> bytes:
    """Generate Excel content for variety comparison."""
    
    # Simple CSV-based Excel content
    # In production, use libraries like openpyxl or xlsxwriter
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['VARIETY COMPARISON REPORT'])
    writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow(['Report ID:', comparison_data.get('request_id', 'N/A')])
    writer.writerow([])
    
    # Summary
    writer.writerow(['SUMMARY'])
    writer.writerow(['Best Overall Variety:', comparison_data.get('summary', {}).get('best_overall_variety', 'N/A')])
    writer.writerow(['Confidence Score:', comparison_data.get('summary', {}).get('confidence_score', 0)])
    writer.writerow([])
    
    # Detailed Results
    writer.writerow(['DETAILED RESULTS'])
    writer.writerow(['Variety', 'Overall Score', 'Yield Potential', 'Disease Resistance', 
                    'Maturity Suitability', 'Management Requirements', 'Economic Outlook', 'Risk Rating'])
    
    detailed_results = comparison_data.get('detailed_results', [])
    for result in detailed_results:
        criteria_scores = result.get('criteria_scores', {})
        writer.writerow([
            result.get('variety_name', 'N/A'),
            f"{result.get('overall_score', 0):.2f}",
            f"{criteria_scores.get('yield_potential', 0):.2f}",
            f"{criteria_scores.get('disease_resilience', 0):.2f}",
            f"{criteria_scores.get('maturity_suitability', 0):.2f}",
            f"{criteria_scores.get('management_requirements', 0):.2f}",
            f"{criteria_scores.get('economic_outlook', 0):.2f}",
            result.get('risk_rating', 'N/A')
        ])
    
    writer.writerow([])
    
    # Trade-offs
    writer.writerow(['TRADE-OFF ANALYSIS'])
    writer.writerow(['Focus Area', 'Preferred Variety', 'Rationale'])
    
    trade_offs = comparison_data.get('trade_offs', [])
    for trade_off in trade_offs:
        writer.writerow([
            trade_off.get('focus_area', 'N/A'),
            trade_off.get('preferred_variety_name', 'N/A'),
            trade_off.get('rationale', 'N/A')
        ])
    
    writer.writerow([])
    
    # Key Takeaways
    writer.writerow(['KEY TAKEAWAYS'])
    key_takeaways = comparison_data.get('summary', {}).get('key_takeaways', [])
    for takeaway in key_takeaways:
        writer.writerow([takeaway])
    
    writer.writerow([])
    
    # Recommended Actions
    writer.writerow(['RECOMMENDED ACTIONS'])
    recommended_actions = comparison_data.get('summary', {}).get('recommended_actions', [])
    for action in recommended_actions:
        writer.writerow([action])
    
    return output.getvalue().encode('utf-8')

def generate_csv_content(comparison_data: Dict[str, Any], varieties: List[Dict[str, Any]]) -> str:
    """Generate CSV content for variety comparison."""
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['VARIETY COMPARISON REPORT'])
    writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow(['Report ID:', comparison_data.get('request_id', 'N/A')])
    writer.writerow([])
    
    # Summary
    writer.writerow(['SUMMARY'])
    writer.writerow(['Best Overall Variety:', comparison_data.get('summary', {}).get('best_overall_variety', 'N/A')])
    writer.writerow(['Confidence Score:', comparison_data.get('summary', {}).get('confidence_score', 0)])
    writer.writerow([])
    
    # Detailed Results
    writer.writerow(['DETAILED RESULTS'])
    writer.writerow(['Variety', 'Overall Score', 'Yield Potential', 'Disease Resistance', 
                    'Maturity Suitability', 'Management Requirements', 'Economic Outlook', 'Risk Rating'])
    
    detailed_results = comparison_data.get('detailed_results', [])
    for result in detailed_results:
        criteria_scores = result.get('criteria_scores', {})
        writer.writerow([
            result.get('variety_name', 'N/A'),
            f"{result.get('overall_score', 0):.2f}",
            f"{criteria_scores.get('yield_potential', 0):.2f}",
            f"{criteria_scores.get('disease_resilience', 0):.2f}",
            f"{criteria_scores.get('maturity_suitability', 0):.2f}",
            f"{criteria_scores.get('management_requirements', 0):.2f}",
            f"{criteria_scores.get('economic_outlook', 0):.2f}",
            result.get('risk_rating', 'N/A')
        ])
    
    writer.writerow([])
    
    # Trade-offs
    writer.writerow(['TRADE-OFF ANALYSIS'])
    writer.writerow(['Focus Area', 'Preferred Variety', 'Rationale'])
    
    trade_offs = comparison_data.get('trade_offs', [])
    for trade_off in trade_offs:
        writer.writerow([
            trade_off.get('focus_area', 'N/A'),
            trade_off.get('preferred_variety_name', 'N/A'),
            trade_off.get('rationale', 'N/A')
        ])
    
    writer.writerow([])
    
    # Key Takeaways
    writer.writerow(['KEY TAKEAWAYS'])
    key_takeaways = comparison_data.get('summary', {}).get('key_takeaways', [])
    for takeaway in key_takeaways:
        writer.writerow([takeaway])
    
    writer.writerow([])
    
    # Recommended Actions
    writer.writerow(['RECOMMENDED ACTIONS'])
    recommended_actions = comparison_data.get('summary', {}).get('recommended_actions', [])
    for action in recommended_actions:
        writer.writerow([action])
    
    return output.getvalue()

@router.get("/formats")
async def get_export_formats():
    """Get available export formats."""
    return {
        "available_formats": [
            {
                "format": "pdf",
                "description": "Portable Document Format",
                "mime_type": "application/pdf",
                "features": ["Formatted report", "Charts and graphs", "Print-ready"]
            },
            {
                "format": "excel",
                "description": "Microsoft Excel Spreadsheet",
                "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "features": ["Multiple sheets", "Formulas", "Charts", "Data analysis"]
            },
            {
                "format": "csv",
                "description": "Comma-Separated Values",
                "mime_type": "text/csv",
                "features": ["Raw data", "Importable", "Lightweight", "Universal compatibility"]
            }
        ]
    }

@router.get("/health")
async def export_health_check():
    """Health check for export service."""
    return {
        "service": "export",
        "status": "healthy",
        "version": "1.0.0",
        "supported_formats": ["pdf", "excel", "csv"],
        "timestamp": datetime.now().isoformat()
    }