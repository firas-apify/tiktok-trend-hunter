"""TikTok Shop scraper module.

This module handles scraping product data from TikTok Shop.
It can either scrape directly or use Actor-to-Actor orchestration
to leverage existing TikTok scrapers on the Apify platform.
"""

import logging
from typing import Any

from apify import Actor
from apify_client import ApifyClient

from .models import ProductData

logger = logging.getLogger(__name__)


class TikTokShopScraper:
    """Scrapes trending products from TikTok Shop."""

    def __init__(self, category: str, max_products: int = 50, min_sales: int = 100):
        self.category = category
        self.max_products = max_products
        self.min_sales = min_sales

    async def scrape_with_actor(
        self, actor_id: str = "clockworks/tiktok-scraper"
    ) -> list[ProductData]:
        """Use Actor-to-Actor orchestration to scrape TikTok data.

        This method calls an existing TikTok scraper Actor and processes its output.
        """
        logger.info(f"Starting Actor-to-Actor scrape using {actor_id}")

        try:
            # Get the Apify token from environment
            token = Actor.config.token
            if not token:
                logger.warning("No Apify token found, using mock data")
                return await self._get_mock_data()

            client = ApifyClient(token)

            # Prepare input for the TikTok scraper
            run_input = {
                "searchQueries": [self.category],
                "resultsPerPage": self.max_products,
                "shouldDownloadVideos": False,
                "shouldDownloadCovers": False,
            }

            # Run the Actor and wait for it to finish
            logger.info(f"Calling Actor {actor_id} with category: {self.category}")
            run = client.actor(actor_id).call(run_input=run_input)

            if not run:
                logger.error("Actor run failed")
                return await self._get_mock_data()

            # Fetch results from the dataset
            dataset_items = list(
                client.dataset(run["defaultDatasetId"]).iterate_items()
            )

            products = self._transform_actor_output(dataset_items)
            logger.info(f"Scraped {len(products)} products from TikTok")

            return products

        except Exception as e:
            logger.error(f"Actor-to-Actor scrape failed: {e}")
            return await self._get_mock_data()

    def _transform_actor_output(self, items: list[dict[str, Any]]) -> list[ProductData]:
        """Transform raw Actor output into ProductData objects."""
        products = []

        for item in items:
            try:
                # Adapt this transformation based on the actual Actor output format
                product = ProductData(
                    product_id=str(item.get("id", "")),
                    product_title=item.get("title", item.get("desc", "Unknown")),
                    product_url=item.get("webVideoUrl", item.get("url", "")),
                    price=float(item.get("price", 0)),
                    original_price=item.get("originalPrice"),
                    sales_count=int(item.get("playCount", item.get("salesCount", 0))),
                    rating=item.get("rating"),
                    review_count=int(item.get("commentCount", 0)),
                    shop_name=item.get("authorMeta", {}).get("name"),
                    category=self.category,
                    reviews=item.get("comments", [])[:10],
                    image_url=item.get("covers", [None])[0]
                    if item.get("covers")
                    else None,
                )

                if product.sales_count >= self.min_sales:
                    products.append(product)

            except Exception as e:
                logger.warning(f"Failed to parse item: {e}")
                continue

        return products[: self.max_products]

    async def _get_mock_data(self) -> list[ProductData]:
        """Return mock data for testing and development."""
        logger.info("Using mock product data for development")

        mock_products = [
            ProductData(
                product_id="mock_001",
                product_title="Portable Blender USB Rechargeable",
                product_url="https://tiktokshop.com/product/mock_001",
                price=24.99,
                original_price=39.99,
                sales_count=15420,
                rating=4.7,
                review_count=2341,
                shop_name="KitchenGadgetsPro",
                category=self.category,
                reviews=[
                    "Perfect for my morning smoothies! So convenient for the office.",
                    "Battery lasts all week, amazing quality for the price!",
                    "Bought this for my gym bag, absolute game changer!",
                    "My kids love making their own fruit drinks now.",
                    "Wish I bought this sooner, makes healthy eating so easy!",
                ],
                image_url="https://example.com/blender.jpg",
            ),
            ProductData(
                product_id="mock_002",
                product_title="Electric Vegetable Chopper 3-in-1",
                product_url="https://tiktokshop.com/product/mock_002",
                price=34.99,
                original_price=49.99,
                sales_count=8932,
                rating=4.5,
                review_count=1256,
                shop_name="HomeChefTools",
                category=self.category,
                reviews=[
                    "Saves me so much time meal prepping!",
                    "Finally, no more crying while cutting onions!",
                    "The cleanup is super easy, dishwasher safe.",
                    "Bought for my mom and she absolutely loves it.",
                    "Great for making salsa and guacamole quickly.",
                ],
                image_url="https://example.com/chopper.jpg",
            ),
            ProductData(
                product_id="mock_003",
                product_title="Silicone Stretch Lids Set of 12",
                product_url="https://tiktokshop.com/product/mock_003",
                price=12.99,
                original_price=19.99,
                sales_count=25678,
                rating=4.8,
                review_count=4521,
                shop_name="EcoKitchenStore",
                category=self.category,
                reviews=[
                    "No more plastic wrap! These are incredible.",
                    "Fit perfectly on all my bowls and containers.",
                    "Such a simple solution, why didn't I buy these sooner?",
                    "Great for keeping food fresh, very stretchy.",
                    "Eco-friendly and actually works great!",
                ],
                image_url="https://example.com/lids.jpg",
            ),
            ProductData(
                product_id="mock_004",
                product_title="Magnetic Spice Rack Organizer",
                product_url="https://tiktokshop.com/product/mock_004",
                price=28.99,
                original_price=44.99,
                sales_count=6234,
                rating=4.6,
                review_count=892,
                shop_name="OrganizeMyHome",
                category=self.category,
                reviews=[
                    "Finally organized my tiny kitchen!",
                    "The magnets are super strong, no falling jars.",
                    "Looks so aesthetic on my fridge.",
                    "Space saver for small apartments!",
                    "Great gift idea for home cooks.",
                ],
                image_url="https://example.com/spicerack.jpg",
            ),
            ProductData(
                product_id="mock_005",
                product_title="Air Fryer Liners Disposable 100pcs",
                product_url="https://tiktokshop.com/product/mock_005",
                price=9.99,
                original_price=14.99,
                sales_count=42156,
                rating=4.9,
                review_count=7823,
                shop_name="AirFryerEssentials",
                category=self.category,
                reviews=[
                    "Makes cleanup a breeze, love these!",
                    "No more scrubbing my air fryer basket.",
                    "Great quality and perfect fit for my Ninja.",
                    "Reordering for the third time, can't live without them.",
                    "Food doesn't stick anymore, highly recommend!",
                ],
                image_url="https://example.com/liners.jpg",
            ),
        ]

        # Filter by min_sales and limit
        filtered = [p for p in mock_products if p.sales_count >= self.min_sales]
        return filtered[: self.max_products]

    async def scrape(self) -> list[ProductData]:
        """Main scraping method - uses Actor orchestration or falls back to mock data."""
        # In production, this would use the actual TikTok Shop scraper
        # For now, we'll use mock data or Actor orchestration
        return await self.scrape_with_actor()
