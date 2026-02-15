# TikTok Shop Viral Product Finder & AI Analyzer

Discover winning products **before** they go viral. This AI-powered Actor doesn't just scrape data—it analyzes, scores, and tells you exactly *why* a product is trending and how to market it.

## What it does

1. **Scrapes** trending products from TikTok Shop by category
2. **Analyzes** each product using AI (reviews, sales velocity, sentiment)
3. **Scores** virality potential (0-100) based on multiple factors
4. **Generates** actionable marketing insights

## Output for each product

| Field | Description |
|-------|-------------|
| `virality_score` | 0-100 score predicting viral potential |
| `why_winning` | AI explanation of why this product is trending |
| `problem_solved` | The pain point this product addresses |
| `emotional_triggers` | Emotions found in reviews (gift, convenience, etc.) |
| `marketing_angles` | Suggested angles for ads and content |
| `ad_hooks` | Ready-to-use hooks for TikTok/video ads |
| `quality_flags` | Potential issues to watch out for |
| `target_audience` | Ideal customer profile |

## Use cases

- **Dropshippers**: Find products with proven demand before saturation
- **E-commerce sellers**: Validate product ideas with data
- **Content creators**: Discover trending products for affiliate content
- **Brand owners**: Monitor competitor products and trends

## Example output

```json
{
  "product_title": "Portable Blender USB Rechargeable",
  "virality_score": 88,
  "price": 24.99,
  "sales_count": 15420,
  "why_winning": "High sales velocity combined with enthusiastic reviews highlighting convenience. The portable design solves modern lifestyle needs.",
  "marketing_angles": ["Promote as must-have for gym-goers", "Highlight battery life in demos"],
  "ad_hooks": ["POV: You finally found a blender that fits in your bag", "Stop buying $8 smoothies"]
}
```

## Configuration

| Input | Description | Default |
|-------|-------------|---------|
| `category` | Product category to analyze | Kitchen Gadgets |
| `maxProducts` | Number of products (1-50) | 10 |
| `aiProvider` | AI provider (openrouter, anthropic, openai) | openrouter |
| `openrouterApiKey` | Your OpenRouter API key | - |
| `minSalesCount` | Minimum sales threshold | 100 |

## Pricing

This Actor uses **Pay-per-Event** pricing. You pay per product analyzed, not a monthly fee. Try it with a few products first to see the value.

## Getting started

1. Get a free API key from [OpenRouter](https://openrouter.ai)
2. Set your `openrouterApiKey` in the input
3. Choose a category and run!

## Support

Questions? Issues? [Open an issue on GitHub](https://github.com/firas-apify/tiktok-trend-hunter/issues)
