"""Mobile Fertilizer Strategy Interface Tests"""

from pathlib import Path

from fastapi.testclient import TestClient

from services.frontend.src.main import app


class TestMobileFertilizerStrategyInterface:
    """Test suite for the mobile fertilizer strategy interface."""

    def setup_method(self):
        self.client = TestClient(app)

    def test_mobile_strategy_route_serves_template(self):
        """Ensure the mobile strategy page is served correctly."""
        response = self.client.get("/mobile-fertilizer-strategy")
        assert response.status_code == 200

        html = response.text
        assert "Strategy Summary" in html
        assert "mobile-fertilizer-strategy.js" in html
        assert "mobile-fertilizer-strategy.css" in html

    def test_template_contains_critical_sections(self):
        """Verify that critical sections exist in the rendered HTML."""
        response = self.client.get("/mobile-fertilizer-strategy")
        assert response.status_code == 200

        html = response.text
        required_snippets = [
            "quick-actions",
            "priceTrendList",
            "recommendationList",
            "analysisChart",
            "captureGpsButton"
        ]

        for snippet in required_snippets:
            assert snippet in html, f"Expected snippet '{snippet}' missing from template"

    def test_assets_include_camera_overlay_styles(self):
        """Ensure camera overlay styles are present for field photo capture."""
        css_path = Path("services/frontend/src/static/css/mobile-fertilizer-strategy.css")
        assert css_path.exists(), "Expected CSS file not found"

        content = css_path.read_text(encoding="utf-8")
        assert ".camera-overlay" in content
        assert "camera-modal" in content

    def test_sample_data_definitions_present(self):
        """Confirm that sample data builders exist for offline usage."""
        js_path = Path("services/frontend/src/static/js/mobile-fertilizer-strategy.js")
        assert js_path.exists(), "Expected JS file not found"

        script = js_path.read_text(encoding="utf-8")
        assert "buildSampleSummary" in script
        assert "buildSamplePrices" in script
