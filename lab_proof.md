# Lab Proof

## Step 1: Baseline Execution

Original code selected:

Lab M1.05 – OpenAI API Product Listing Generator.

Baseline file:

`product_listing_generator_refactored.py`

Baseline result:

The original script executed successfully, processed three products, and generated the file `output/generated_listings.json`.

---

## Step 2: Refactoring Checklist

### Issues Found

- [ ] The script executes code immediately instead of using a `main()` function.

- [ ] The main processing loop has multiple responsibilities (loading, API call, response parsing and result creation).

- [ ] Prompt creation is hardcoded inside the processing flow.

- [ ] Several values are hardcoded instead of using constants or parameters.

- [ ] Debug and testing code is mixed with production code.

- [ ] Error handling can be modularized into reusable helper functions.

### Priority

1. Modularize the main processing flow.

2. Extract helper functions for repeated or independent logic.

3. Improve error handling and code organization.