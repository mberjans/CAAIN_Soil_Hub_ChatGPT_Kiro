#!/usr/bin/env python3
"""
Historical Analyzer
Weather Impact Analysis Service
Version: 1.0
Date: October 2025
"""

from typing import Dict, Any, List, Optional
import psycopg2
from datetime import datetime, timedelta


class HistoricalAnalyzer:
    """Analyze historical weather patterns using TimescaleDB continuous aggregates."""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize the historical analyzer.
        
        Args:
            database_url: Database connection URL (optional)
        """
        self.database_url = database_url
        self.connection = None
    
    def connect(self, database_url: str) -> bool:
        """Connect to the database.
        
        Args:
            database_url: Database connection URL
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.database_url = database_url
            self.connection = psycopg2.connect(database_url)
            return True
        except Exception as e:
            print(f"Error connecting to database: {str(e)}")
            return False
    
    def analyze_patterns(self, station_id: str, days: int = 30) -> Dict[str, Any]:
        """Analyze historical weather patterns for a specific station.
        
        Args:
            station_id: Weather station identifier
            days: Number of days to analyze (default: 30)
            
        Returns:
            Dictionary with historical pattern analysis
        """
        if not self.connection:
            raise RuntimeError("Database connection not established. Call connect() first.")
        
        try:
            cursor = self.connection.cursor()
            
            # Query continuous aggregates for daily summaries
            query = """
                SELECT 
                    day,
                    avg_temp,
                    min_temp,
                    max_temp,
                    total_precipitation,
                    avg_humidity
                FROM weather_daily_summary 
                WHERE station_id = %s 
                AND day >= NOW() - INTERVAL '%s days'
                ORDER BY day DESC
            """
            
            cursor.execute(query, (station_id, days))
            results = cursor.fetchall()
            
            # Process results
            patterns = {
                "station_id": station_id,
                "analysis_period_days": days,
                "data_points": len(results),
                "temperature_trend": self._calculate_temperature_trend(results),
                "precipitation_trend": self._calculate_precipitation_trend(results),
                "recent_patterns": self._extract_recent_patterns(results[:7])  # Last 7 days
            }
            
            cursor.close()
            return patterns
            
        except Exception as e:
            raise RuntimeError(f"Error analyzing historical patterns: {str(e)}")
    
    def _calculate_temperature_trend(self, results: List[tuple]) -> Dict[str, Any]:
        """Calculate temperature trends from historical data.
        
        Args:
            results: List of (day, avg_temp, min_temp, max_temp, total_precipitation, avg_humidity) tuples
            
        Returns:
            Dictionary with temperature trend analysis
        """
        if not results:
            return {"trend": "insufficient_data", "average": None, "range": None}
        
        # Extract temperatures
        avg_temps = [row[1] for row in results if row[1] is not None]
        
        if not avg_temps:
            return {"trend": "insufficient_data", "average": None, "range": None}
        
        # Calculate basic statistics
        avg_temp = sum(avg_temps) / len(avg_temps)
        min_temp = min(avg_temps)
        max_temp = max(avg_temps)
        
        # Simple trend analysis (comparing first and last thirds)
        third = len(avg_temps) // 3
        if third > 0:
            first_third_avg = sum(avg_temps[:third]) / third
            last_third_avg = sum(avg_temps[-third:]) / third
            
            if last_third_avg > first_third_avg + 1:
                trend = "warming"
            elif last_third_avg < first_third_avg - 1:
                trend = "cooling"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "trend": trend,
            "average": round(avg_temp, 1),
            "range": {"min": min_temp, "max": max_temp},
            "data_points": len(avg_temps)
        }
    
    def _calculate_precipitation_trend(self, results: List[tuple]) -> Dict[str, Any]:
        """Calculate precipitation trends from historical data.
        
        Args:
            results: List of (day, avg_temp, min_temp, max_temp, total_precipitation, avg_humidity) tuples
            
        Returns:
            Dictionary with precipitation trend analysis
        """
        if not results:
            return {"trend": "insufficient_data", "total": 0, "average_daily": 0}
        
        # Extract precipitation data
        precipitations = [row[4] for row in results if row[4] is not None]
        
        if not precipitations:
            return {"trend": "insufficient_data", "total": 0, "average_daily": 0}
        
        # Calculate basic statistics
        total_precip = sum(precipitations)
        avg_daily_precip = total_precip / len(precipitations)
        
        # Simple trend analysis (comparing first and last thirds)
        third = len(precipitations) // 3
        if third > 0:
            first_third_avg = sum(precipitations[:third]) / third
            last_third_avg = sum(precipitations[-third:]) / third
            
            if last_third_avg > first_third_avg * 1.2:
                trend = "increasing"
            elif last_third_avg < first_third_avg * 0.8:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "trend": trend,
            "total": round(total_precip, 1),
            "average_daily": round(avg_daily_precip, 1),
            "data_points": len(precipitations)
        }
    
    def _extract_recent_patterns(self, recent_results: List[tuple]) -> List[Dict[str, Any]]:
        """Extract patterns from recent data.
        
        Args:
            recent_results: List of recent data points
            
        Returns:
            List of recent pattern dictionaries
        """
        patterns = []
        for row in recent_results:
            patterns.append({
                "date": row[0].strftime("%Y-%m-%d") if row[0] else None,
                "average_temperature": float(row[1]) if row[1] else None,
                "min_temperature": float(row[2]) if row[2] else None,
                "max_temperature": float(row[3]) if row[3] else None,
                "total_precipitation": float(row[4]) if row[4] else None,
                "average_humidity": int(row[5]) if row[5] else None
            })
        return patterns
    
    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None