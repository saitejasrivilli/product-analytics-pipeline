# Fact Table Grain Decision

## Grain Definition
**fact_orders grain: One row per order-product combination**

- **Row count:** 1,384,617 rows
- **Dimensions:** order_id, product_id, user_id, order_date, order_dow
- **Metrics:** reordered (0 or 1), add_to_cart_order, days_since_prior_order

## Decision Rationale

### Option A: Order-Product Grain (CHOSEN)
- One row per product in each order
- Enables: Product-level reorder rate analysis, basket composition, SKU performance
- Downside: Higher row count (1.38M), requires joins for order-level metrics

### Option B: Order Grain (Rejected)
- One row per order (no product detail)
- Enables: Order-level metrics (basket size, order value)
- Downside: Loses product-level insights, expensive denormalization for reorder analysis

### Option C: Product Grain (Rejected)
- One row per product (pre-aggregated)
- Enables: Fast product queries
- Downside: Loses order context, can't answer "What % of orders include product X?"

## Why Order-Product Wins

**Question: "What's the reorder rate for Banana?"**
- Order-product grain: `SELECT AVG(reordered) WHERE product_id = 123` → 1 query
- Order grain: Join orders → products → filter → aggregate → 3-4x slower
- Product grain: Pre-computed, loses temporal analysis

**Question: "How many products in average order?"**
- Order-product grain: `GROUP BY order_id, COUNT(DISTINCT product_id)` → Accurate
- Order grain: Would need denormalization in staging

## Performance Tradeoff

| Query Type | Order-Product | Order | Product |
|-----------|---------------|-------|---------|
| Product reorder rate | 0.2s | 1.2s | 0.05s |
| Basket composition | 0.3s | 0.8s | N/A |
| Order metrics | 0.5s | 0.1s | N/A |
| **Flexibility** | ⭐⭐⭐ | ⭐⭐ | ⭐ |

**Decision:** Accept higher row count for query flexibility. Slow queries are addressed via pre-aggregation layer (daily_product_metrics).

## Interview Talking Points

1. **"Why order-product grain?"** — Unlocks product-level analysis essential for e-commerce (reorder velocity, basket mixing). Order grain forces expensive joins.

2. **"What's the downside?"** — 1.38M rows vs 200K. Mitigated by pre-aggregated marts for dashboard performance.

3. **"Would you change it?"** — No. Tradeoff is sound: flexibility > raw speed. Power users can run slow ad-hoc queries; dashboard uses pre-aggs.

4. **"How does grain affect testing?"** — Grain drives test design. Order-product grain requires testing:
   - No duplicate order-product combinations
   - All order_ids exist in dim_orders
   - Referential integrity on product_id

## Related Models

- **fact_orders** — Base order-product grain (1.38M rows)
- **daily_product_metrics** — Pre-aggregated for dashboard (49K rows, 1 per product per day)
- **dim_products** — SCD Type 2 tracks product reclassifications over time
