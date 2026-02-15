"""Tests for the scraper module."""

import pytest

from src.tiktok_trend_hunter.scraper import TikTokShopScraper


class TestTikTokShopScraper:
    @pytest.mark.asyncio
    async def test_mock_data_returns_products(self):
        scraper = TikTokShopScraper(
            category="Kitchen Gadgets",
            max_products=5,
            min_sales=100,
        )
        products = await scraper._get_mock_data()

        assert len(products) > 0
        assert len(products) <= 5

    @pytest.mark.asyncio
    async def test_mock_data_filters_by_min_sales(self):
        scraper = TikTokShopScraper(
            category="Kitchen Gadgets",
            max_products=50,
            min_sales=10000,  # High threshold
        )
        products = await scraper._get_mock_data()

        for product in products:
            assert product.sales_count >= 10000

    @pytest.mark.asyncio
    async def test_mock_data_respects_max_products(self):
        scraper = TikTokShopScraper(
            category="Kitchen Gadgets",
            max_products=2,
            min_sales=0,
        )
        products = await scraper._get_mock_data()

        assert len(products) <= 2

    @pytest.mark.asyncio
    async def test_scraper_uses_category(self):
        scraper = TikTokShopScraper(category="Beauty Products")
        products = await scraper._get_mock_data()

        # Mock data assigns category from scraper config
        for product in products:
            assert product.category == "Beauty Products"
