# Rule Packs

JSON-based rule definitions for web scraping and data validation.

## Structure

Each rule pack is a JSON file that defines:
- Target URLs and patterns
- Data extraction rules
- Validation criteria
- Transformation logic
- Output format

## Example Rule Pack

```json
{
  "name": "product-scraper",
  "version": "1.0.0",
  "target": {
    "url": "https://example.com/products",
    "selector": ".product-item"
  },
  "extract": {
    "title": ".product-title",
    "price": ".product-price",
    "description": ".product-description"
  },
  "validate": {
    "price": {
      "type": "number",
      "min": 0
    }
  }
}
```

## Usage

1. Create a new rule pack JSON file
2. Define your scraping rules
3. Use the crawler service to execute the rules
4. Monitor results in the dashboard

## Best Practices

- Use semantic naming for rule packs
- Include version numbers
- Document complex rules
- Test rules before deployment
- Keep rules modular and reusable 