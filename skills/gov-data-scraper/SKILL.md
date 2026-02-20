# Government Data Scraper

Scrape business and entity data from free public government sources only. No paid APIs, no commercial services — just open government data.

## Sources

### California (Primary)
- **CA Secretary of State** — Business entity search
- **CA Franchise Tax Board** — Public tax records (limited)
- **County Recorders** — Property/business filings
- **City Business License Databases** — Municipal level

### Federal (USA)
- **SAM.gov** — Federal contractors (free API)
- **USASpending.gov** — Federal spending data
- **SEC EDGAR** — Public company filings
- **IRS Exempt Orgs** — Non-profit data

### Other States (Expandable)
- Delaware Division of Corporations
- Texas Secretary of State
- New York Department of State

## Commands

### Scrape CA SOS
```bash
# Business entity search
skill gov-data-scraper scrape-ca-sos --search "TECH" --type corp

# Get entity details
skill gov-data-scraper entity-details --entity-number "C1234567"

# Bulk scrape (respect rate limits)
skill gov-data-scraper bulk-ca --start-page 1 --pages 10 --delay 5
```

### Scrape Federal Sources
```bash
# SAM.gov contractors
skill gov-data-scraper sam-contractors --naics "541511" --state CA

# USASpending grants
skill gov-data-scraper federal-spending --recipient "SAN FRANCISCO"

# SEC EDGAR filings
skill gov-data-scraper sec-filings --ticker "AAPL" --form "10-K"
```

### Data Processing
```bash
# Enrich with additional gov sources
skill gov-data-scraper enrich --input leads.json --sources "ca-sos,sec-edgar"

# Export to CSV
skill gov-data-scraper export --input leads.json --format csv --output leads.csv

# Validate entity status
skill gov-data-scraper validate --input leads.json --check "active,good-standing"
```

## Rate Limits & Ethics

### Respect These Limits
- **CA SOS:** 1 request per 3 seconds max
- **SEC EDGAR:** 10 requests per second max
- **SAM.gov:** 1000 requests per day (API key)
- **USASpending:** 1000 requests per hour

### Ethical Scraping
- Only scrape public data (no paywalled content)
- Respect robots.txt
- Don't overwhelm servers
- Cache results to avoid re-scraping
- Attribute data sources

## Output Format

```json
{
  "entity_name": "TECH SOLUTIONS INC",
  "entity_number": "C1234567",
  "entity_type": "CORPORATION",
  "status": "ACTIVE",
  "formation_date": "2015-03-15",
  "registered_agent": "JOHN DOE",
  "address": {
    "street": "123 MAIN ST",
    "city": "SAN FRANCISCO",
    "state": "CA",
    "zip": "94102"
  },
  "sources": ["ca-sos"],
  "scraped_at": "2026-02-20T20:00:00Z",
  "enrichment": {
    "federal_contracts": [],
    "sec_filings": null,
    "usaspending": []
  }
}
```

## Integration with Miles' Work

Miles already built the CA SOS scraper. This skill extends it with:
- Additional government sources
- Rate limiting
- Data enrichment
- Export capabilities
- Ethical scraping guidelines

**Next Steps:**
1. Review Miles' existing scraper
2. Add rate limiting
3. Integrate federal sources (SAM.gov, USASpending)
4. Build enrichment pipeline
5. Export to CRM-ready format

## References

- [CA SOS Business Search](https://businesssearch.sos.ca.gov/)
- [SAM.gov API](https://sam.gov/)
- [USASpending API](https://api.usaspending.gov/)
- [SEC EDGAR](https://www.sec.gov/edgar)
- [IRS Exempt Orgs](https://www.irs.gov/charities-non-profits)
