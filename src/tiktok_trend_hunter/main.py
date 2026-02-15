"""Main entry point for the TikTok Trend Hunter Actor."""

import logging
import os

from apify import Actor

from .analyzer import ProductAnalyzer
from .models import ActorInput, AnalyzedProduct
from .scraper import TikTokShopScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Main Actor logic."""
    async with Actor:
        logger.info("Starting TikTok Trend Hunter Actor")

        # Get and validate input
        raw_input = await Actor.get_input() or {}
        actor_input = ActorInput(**raw_input)

        # Fall back to environment variables for API keys
        anthropic_key = actor_input.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        openai_key = actor_input.openai_api_key or os.getenv("OPENAI_API_KEY")
        openrouter_key = actor_input.openrouter_api_key or os.getenv("ANTHROPIC_AUTH_TOKEN")
        openrouter_model = actor_input.openrouter_model or os.getenv("ANTHROPIC_MODEL", "nvidia/nemotron-nano-9b-v2:free")

        logger.info(f"Configuration: category={actor_input.category}, "
                   f"max_products={actor_input.max_products}, "
                   f"ai_provider={actor_input.ai_provider}")

        # Validate API keys
        if actor_input.ai_provider == "anthropic" and not anthropic_key:
            raise ValueError("Anthropic API key is required when using Anthropic provider")
        if actor_input.ai_provider == "openai" and not openai_key:
            raise ValueError("OpenAI API key is required when using OpenAI provider")
        if actor_input.ai_provider == "openrouter" and not openrouter_key:
            raise ValueError("OpenRouter API key is required when using OpenRouter provider")

        # Phase 1: Scrape products
        logger.info(f"Scraping trending products in category: {actor_input.category}")
        scraper = TikTokShopScraper(
            category=actor_input.category,
            max_products=actor_input.max_products,
            min_sales=actor_input.min_sales_count,
        )
        products = await scraper.scrape()
        logger.info(f"Found {len(products)} products to analyze")

        if not products:
            logger.warning("No products found, exiting")
            return

        # Phase 2: Analyze with AI
        logger.info(f"Analyzing products with {actor_input.ai_provider}")
        analyzer = ProductAnalyzer(
            provider=actor_input.ai_provider,
            anthropic_api_key=anthropic_key,
            openai_api_key=openai_key,
            openrouter_api_key=openrouter_key,
            openrouter_model=openrouter_model,
        )

        analyzed_products: list[AnalyzedProduct] = []
        for i, product in enumerate(products):
            logger.info(f"Analyzing product {i + 1}/{len(products)}: {product.product_title}")

            analysis = await analyzer.analyze_product(product)
            analyzed = AnalyzedProduct.from_product_and_analysis(product, analysis)
            analyzed_products.append(analyzed)

            # Charge per insight using Pay-per-Event
            # This is where monetization happens
            await Actor.charge(
                event_name="product-analyzed",
                count=1,
            )

        # Phase 3: Sort by virality score and output results
        analyzed_products.sort(key=lambda x: x.virality_score, reverse=True)

        logger.info("Pushing results to dataset")
        for product in analyzed_products:
            await Actor.push_data(product.model_dump())

        # Log summary
        top_products = analyzed_products[:3]
        logger.info("=" * 50)
        logger.info("TOP 3 VIRAL PRODUCTS:")
        for i, p in enumerate(top_products, 1):
            logger.info(f"{i}. {p.product_title} (Score: {p.virality_score})")
            logger.info(f"   Why: {p.why_winning[:100]}...")
        logger.info("=" * 50)

        logger.info(f"Analysis complete! {len(analyzed_products)} products analyzed.")
