# Database 1 - Manual Review Checklist

## Pre-Validation Setup
- [ ] Database file/connection available
- [ ] Database connection tested and working
- [ ] Validation notebook dependencies installed
- [ ] Database schema accessible

## 1. Database Source Verification

### Provenance Check
- [ ] Database source documented
- [ ] Source is NOT publicly available on GitHub
- [ ] Source is NOT easily webcrawled/scraped
- [ ] Source represents real-world use case
- [ ] No evidence of being LLM-generated or synthetic

### Source Type (check one)
- [ ] Government data (FAA, public records) - hidden from crawlers
- [ ] Reverse-engineered from real website/application
- [ ] Built database representing real-world use case
- [ ] Internal operational database
- [ ] Real-world research database

## 2. Schema Documentation Review

- [ ] Database description provided
- [ ] All tables documented with descriptions
- [ ] All columns documented (name, type, constraints)
- [ ] Relationships/foreign keys documented
- [ ] Data types appropriate for use case
- [ ] Schema complexity sufficient for meaningful analysis

## 3. Placeholder Data Review

### Email Addresses
- [ ] No @example.com addresses
- [ ] No @test.com addresses
- [ ] No user_001@, test1@ patterns
- [ ] Email addresses appear authentic

### URLs and Links
- [ ] No localhost URLs
- [ ] No 127.0.0.1 addresses
- [ ] No staging/test URLs
- [ ] No .run.app or development URLs
- [ ] URLs appear production-ready

### Names and Identifiers
- [ ] No excessive "John Smith" or "Test User" patterns
- [ ] Names appear diverse and realistic
- [ ] No generic placeholder names

### Other Placeholders
- [ ] No suspicious product slugs (/p/Spuh, /p/Hywd)
- [ ] No generic store names (Aqua Store, Yankee Goods) unless legitimate
- [ ] Data appears production-grade

## 4. Data Quality Assessment

### Realism Check
- [ ] Data patterns match real-world expectations
- [ ] Distributions are not "too clean" (synthetic indicator)
- [ ] Data shows expected variance and noise
- [ ] Relationships between tables are logical

### Timestamp Verification
- [ ] Timestamps show realistic patterns
- [ ] No identical time intervals (generation indicator)
- [ ] Date ranges are appropriate for use case
- [ ] No evidence of timestamp manipulation

### Data Volume
- [ ] Sufficient data volume for analysis
- [ ] Not too small (suspicious)
- [ ] Not suspiciously uniform

## 5. Complexity Assessment

### Database Structure
- [ ] Multiple tables (not overly simple)
- [ ] Relationships between tables
- [ ] Foreign keys present
- [ ] Sufficient columns per table

### Business Logic
- [ ] Tables represent meaningful business entities
- [ ] Relationships reflect real-world connections
- [ ] Data supports complex queries
- [ ] Can support 30+ meaningful queries

## 6. Technical Validation Results

### Automated Checks
- [ ] Validation notebook executed successfully
- [ ] No high-severity placeholder issues
- [ ] Complexity score ≥ 30/100
- [ ] Fewer than 5 suspicious distributions
- [ ] Timestamp analysis passed

### Data Science Checks
- [ ] F-score, precision, recall calculated (if applicable)
- [ ] Curve fitting analysis performed
- [ ] No "too clean" curve fits detected
- [ ] Data shows expected statistical properties

## 7. Query Readiness

- [ ] Database supports complex joins
- [ ] Sufficient data for aggregations
- [ ] Can generate 30+ meaningful queries
- [ ] At least 10-15 queries can involve joins/aggregations
- [ ] Queries would demonstrate real-world complexity

## 8. Documentation Completeness

- [ ] Database description clear and comprehensive
- [ ] Schema documentation complete
- [ ] All tables and columns documented
- [ ] Relationships explained
- [ ] Use case clearly described

## 9. Final Validation Decision

### Overall Assessment
- [ ] **PASS** - Database meets all requirements
- [ ] **WARNING** - Minor issues but acceptable
- [ ] **FAIL** - Does not meet requirements

### Issues Found (if any)
- List any issues discovered during validation:

### Recommendations
- Provide recommendations for improvement:

---

## Validation Sign-off

**Validated by:** _________________
**Date:** _________________
**Status:** _________________
**Notes:**

---

## Next Steps

If PASS:
- [ ] Proceed with query generation (30+ queries)
- [ ] Complete schema documentation
- [ ] Prepare for delivery

If FAIL:
- [ ] Document specific failure reasons
- [ ] Recommend alternative database or fixes
- [ ] Escalate if needed
