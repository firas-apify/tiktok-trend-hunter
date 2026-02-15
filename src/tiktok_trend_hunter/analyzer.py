"""AI-powered product analysis module."""

import json
import logging

from anthropic import Anthropic
from openai import OpenAI

from .models import ProductAnalysis, ProductData

logger = logging.getLogger(__name__)

ANALYSIS_PROMPT = """You are an expert e-commerce analyst specializing in viral product identification for TikTok Shop and social commerce.

Analyze the following product data and provide a detailed assessment:

Product Title: {title}
Price: ${price}
Sales Count: {sales_count}
Rating: {rating}
Review Count: {review_count}
Category: {category}

Recent Reviews:
{reviews}

Based on this data, provide your analysis in the following JSON format:
{{
    "virality_score": <0-100 score based on sales velocity, review sentiment, and viral potential>,
    "why_winning": "<2-3 sentence explanation of why this product is trending>",
    "problem_solved": "<The main pain point or problem this product addresses>",
    "emotional_triggers": ["<emotional trigger 1>", "<emotional trigger 2>", ...],
    "marketing_angles": ["<marketing angle 1>", "<marketing angle 2>", ...],
    "quality_flags": ["<potential quality issue 1>", ...],
    "target_audience": "<Description of the ideal customer>",
    "ad_hooks": ["<video ad hook idea 1>", "<video ad hook idea 2>", ...]
}}

Consider:
- Sales velocity (high sales = proven demand)
- Review sentiment and emotional language
- Problem-solution clarity
- Viral/shareable qualities
- Price point attractiveness
- Potential quality concerns from reviews

Respond ONLY with the JSON object, no additional text."""


class ProductAnalyzer:
    """Analyzes products using AI to generate insights."""

    def __init__(
        self,
        provider: str = "openrouter",
        anthropic_api_key: str | None = None,
        openai_api_key: str | None = None,
        openrouter_api_key: str | None = None,
        openrouter_model: str = "nvidia/nemotron-nano-9b-v2:free",
    ):
        self.provider = provider
        self._anthropic_client: Anthropic | None = None
        self._openai_client: OpenAI | None = None
        self._model: str | None = None

        if provider == "anthropic":
            if not anthropic_api_key:
                raise ValueError("Anthropic API key is required")
            self._anthropic_client = Anthropic(api_key=anthropic_api_key)
        elif provider == "openai":
            if not openai_api_key:
                raise ValueError("OpenAI API key is required")
            self._openai_client = OpenAI(api_key=openai_api_key)
        elif provider == "openrouter":
            if not openrouter_api_key:
                raise ValueError("OpenRouter API key is required")
            self._openai_client = OpenAI(
                api_key=openrouter_api_key,
                base_url="https://openrouter.ai/api/v1",
            )
            self._model = openrouter_model
        else:
            raise ValueError(f"Unknown AI provider: {provider}")

    def _format_prompt(self, product: ProductData) -> str:
        """Format the analysis prompt with product data."""
        reviews_text = "\n".join(
            [f"- {review}" for review in product.reviews[:10]]
        ) or "No reviews available"

        return ANALYSIS_PROMPT.format(
            title=product.product_title,
            price=product.price,
            sales_count=product.sales_count,
            rating=product.rating or "N/A",
            review_count=product.review_count,
            category=product.category or "Unknown",
            reviews=reviews_text,
        )

    def _parse_response(self, response_text: str) -> ProductAnalysis:
        """Parse the AI response into a ProductAnalysis object."""
        try:
            # Try to extract JSON from the response
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            data = json.loads(response_text.strip())
            return ProductAnalysis(**data)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse AI response: {e}")
            # Return a default analysis if parsing fails
            return ProductAnalysis(
                virality_score=50,
                why_winning="Unable to analyze - AI response parsing failed",
                problem_solved="Unknown",
                emotional_triggers=[],
                marketing_angles=[],
                quality_flags=["Analysis incomplete"],
                target_audience="General consumers",
                ad_hooks=[],
            )

    async def analyze_product(self, product: ProductData) -> ProductAnalysis:
        """Analyze a single product and return insights."""
        prompt = self._format_prompt(product)

        try:
            if self.provider == "anthropic" and self._anthropic_client:
                response = self._anthropic_client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}],
                )
                response_text = response.content[0].text

            elif self.provider == "openai" and self._openai_client:
                response = self._openai_client.chat.completions.create(
                    model="gpt-4o",
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}],
                )
                response_text = response.choices[0].message.content or ""

            elif self.provider == "openrouter" and self._openai_client:
                response = self._openai_client.chat.completions.create(
                    model=self._model or "meta-llama/llama-3.3-8b-instruct:free",
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}],
                )
                response_text = response.choices[0].message.content or ""

            else:
                raise ValueError("No AI client configured")

            return self._parse_response(response_text)

        except Exception as e:
            logger.error(f"AI analysis failed for {product.product_title}: {e}")
            return ProductAnalysis(
                virality_score=0,
                why_winning=f"Analysis failed: {str(e)}",
                problem_solved="Unknown",
                emotional_triggers=[],
                marketing_angles=[],
                quality_flags=["Analysis failed"],
                target_audience="Unknown",
                ad_hooks=[],
            )

    async def analyze_products(
        self, products: list[ProductData]
    ) -> list[ProductAnalysis]:
        """Analyze multiple products."""
        results = []
        for product in products:
            logger.info(f"Analyzing product: {product.product_title}")
            analysis = await self.analyze_product(product)
            results.append(analysis)
        return results
