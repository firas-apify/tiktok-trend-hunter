"""Data models for the TikTok Trend Hunter."""

from pydantic import BaseModel, ConfigDict, Field


class ProductData(BaseModel):
    """Raw product data scraped from TikTok Shop."""

    product_id: str
    product_title: str
    product_url: str
    price: float
    original_price: float | None = None
    sales_count: int
    rating: float | None = None
    review_count: int = 0
    shop_name: str | None = None
    category: str | None = None
    reviews: list[str] = Field(default_factory=list)
    image_url: str | None = None


class ProductAnalysis(BaseModel):
    """AI-generated analysis for a product."""

    virality_score: int = Field(ge=0, le=100, description="Virality score from 0-100")
    why_winning: str = Field(description="Explanation of why this product is trending")
    problem_solved: str = Field(description="The main problem this product solves")
    emotional_triggers: list[str] = Field(
        default_factory=list, description="Emotional triggers found in reviews"
    )
    marketing_angles: list[str] = Field(
        default_factory=list, description="Suggested marketing angles for ads"
    )
    quality_flags: list[str] = Field(
        default_factory=list, description="Potential quality issues to watch out for"
    )
    target_audience: str = Field(description="Ideal target audience for this product")
    ad_hooks: list[str] = Field(
        default_factory=list, description="Suggested hooks for video ads"
    )


class AnalyzedProduct(BaseModel):
    """Combined product data with AI analysis."""

    product_id: str
    product_title: str
    product_url: str
    price: float
    original_price: float | None = None
    discount_percentage: float | None = None
    sales_count: int
    rating: float | None = None
    review_count: int = 0
    shop_name: str | None = None
    category: str | None = None
    image_url: str | None = None
    virality_score: int
    why_winning: str
    problem_solved: str
    emotional_triggers: list[str]
    marketing_angles: list[str]
    quality_flags: list[str]
    target_audience: str
    ad_hooks: list[str]

    @classmethod
    def from_product_and_analysis(
        cls, product: ProductData, analysis: ProductAnalysis
    ) -> "AnalyzedProduct":
        """Create an AnalyzedProduct from product data and analysis."""
        discount = None
        if product.original_price and product.original_price > product.price:
            discount = round(
                (1 - product.price / product.original_price) * 100, 1
            )

        return cls(
            product_id=product.product_id,
            product_title=product.product_title,
            product_url=product.product_url,
            price=product.price,
            original_price=product.original_price,
            discount_percentage=discount,
            sales_count=product.sales_count,
            rating=product.rating,
            review_count=product.review_count,
            shop_name=product.shop_name,
            category=product.category,
            image_url=product.image_url,
            virality_score=analysis.virality_score,
            why_winning=analysis.why_winning,
            problem_solved=analysis.problem_solved,
            emotional_triggers=analysis.emotional_triggers,
            marketing_angles=analysis.marketing_angles,
            quality_flags=analysis.quality_flags,
            target_audience=analysis.target_audience,
            ad_hooks=analysis.ad_hooks,
        )


class ActorInput(BaseModel):
    """Input configuration for the Actor."""

    category: str = "Kitchen Gadgets"
    max_products: int = Field(default=10, ge=1, le=50, alias="maxProducts")
    ai_provider: str = Field(default="openrouter", alias="aiProvider")
    anthropic_api_key: str | None = Field(default=None, alias="anthropicApiKey")
    openai_api_key: str | None = Field(default=None, alias="openaiApiKey")
    openrouter_api_key: str | None = Field(default=None, alias="openrouterApiKey")
    openrouter_model: str | None = Field(default=None, alias="openrouterModel")
    include_review_analysis: bool = Field(default=True, alias="includeReviewAnalysis")
    min_sales_count: int = Field(default=100, ge=0, alias="minSalesCount")

    model_config = ConfigDict(populate_by_name=True)
