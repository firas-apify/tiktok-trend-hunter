"""Tests for data models."""

import pytest

from src.tiktok_trend_hunter.models import (
    ActorInput,
    AnalyzedProduct,
    ProductAnalysis,
    ProductData,
)


class TestProductData:
    def test_create_product_data(self):
        product = ProductData(
            product_id="test_001",
            product_title="Test Product",
            product_url="https://example.com/product",
            price=19.99,
            sales_count=1000,
        )
        assert product.product_id == "test_001"
        assert product.price == 19.99
        assert product.reviews == []

    def test_product_data_with_reviews(self):
        product = ProductData(
            product_id="test_002",
            product_title="Test Product",
            product_url="https://example.com/product",
            price=29.99,
            sales_count=500,
            reviews=["Great product!", "Highly recommend"],
        )
        assert len(product.reviews) == 2


class TestProductAnalysis:
    def test_create_analysis(self):
        analysis = ProductAnalysis(
            virality_score=85,
            why_winning="High demand product with great reviews",
            problem_solved="Saves time in the kitchen",
            target_audience="Home cooks aged 25-45",
        )
        assert analysis.virality_score == 85
        assert analysis.emotional_triggers == []

    def test_virality_score_bounds(self):
        with pytest.raises(ValueError):
            ProductAnalysis(
                virality_score=150,  # Invalid: above 100
                why_winning="Test",
                problem_solved="Test",
                target_audience="Test",
            )


class TestAnalyzedProduct:
    def test_from_product_and_analysis(self):
        product = ProductData(
            product_id="test_001",
            product_title="Test Product",
            product_url="https://example.com/product",
            price=19.99,
            original_price=29.99,
            sales_count=1000,
        )
        analysis = ProductAnalysis(
            virality_score=75,
            why_winning="Strong sales momentum",
            problem_solved="Convenience",
            target_audience="Busy professionals",
            marketing_angles=["Time-saver", "Must-have"],
        )

        analyzed = AnalyzedProduct.from_product_and_analysis(product, analysis)

        assert analyzed.virality_score == 75
        assert analyzed.discount_percentage == pytest.approx(33.4, rel=0.1)
        assert len(analyzed.marketing_angles) == 2


class TestActorInput:
    def test_default_values(self):
        input_data = ActorInput()
        assert input_data.category == "Kitchen Gadgets"
        assert input_data.max_products == 10
        assert input_data.ai_provider == "anthropic"

    def test_from_camel_case(self):
        input_data = ActorInput(
            maxProducts=25,
            aiProvider="openai",
            includeReviewAnalysis=False,
        )
        assert input_data.max_products == 25
        assert input_data.ai_provider == "openai"
        assert input_data.include_review_analysis is False
