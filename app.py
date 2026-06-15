"""
Dashboard API for product-analytics-pipeline.
Deploy to Render: https://render.com
"""

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# Pre-computed dashboard data
dashboard_data = {
    "status": {
        "fact_rows": 1384617,
        "user_count": 206209,
        "product_count": 49688,
        "reorder_rate": 59.86
    },
    "metrics": [
        {"day": 0, "daily_users": 27465, "orders": 27465, "items_per_order": 0.9, "reorder_rate": 0.61},
        {"day": 1, "daily_users": 19672, "orders": 19672, "items_per_order": 1.1, "reorder_rate": 0.599},
        {"day": 2, "daily_users": 16119, "orders": 16119, "items_per_order": 1.3, "reorder_rate": 0.588},
        {"day": 3, "daily_users": 15687, "orders": 15687, "items_per_order": 1.3, "reorder_rate": 0.587},
        {"day": 4, "daily_users": 15959, "orders": 15959, "items_per_order": 1.3, "reorder_rate": 0.595},
        {"day": 5, "daily_users": 17406, "orders": 17406, "items_per_order": 1.3, "reorder_rate": 0.606},
        {"day": 6, "daily_users": 18901, "orders": 18901, "items_per_order": 1.2, "reorder_rate": 0.594}
    ],
    "top_products": [
        {"product_id": 39507, "times_ordered": 12, "reorder_rate": 1.0},
        {"product_id": 37414, "times_ordered": 10, "reorder_rate": 1.0},
        {"product_id": 32112, "times_ordered": 10, "reorder_rate": 1.0},
        {"product_id": 15952, "times_ordered": 12, "reorder_rate": 1.0},
        {"product_id": 25115, "times_ordered": 10, "reorder_rate": 1.0},
        {"product_id": 5793, "times_ordered": 10, "reorder_rate": 1.0},
        {"product_id": 8558, "times_ordered": 12, "reorder_rate": 1.0},
        {"product_id": 20320, "times_ordered": 10, "reorder_rate": 1.0},
        {"product_id": 34631, "times_ordered": 10, "reorder_rate": 1.0},
        {"product_id": 40183, "times_ordered": 10, "reorder_rate": 1.0}
    ],
    "insights": [
        "📈 Monday has highest users (27K) with 61% reorder rate",
        "⭐ 15 products have 100% reorder rate (highly sticky)",
        "🔄 Overall reorder rate: 59.86%",
        "📦 Average basket: 1.1 items per order",
        "🎯 High-frequency products drive retention"
    ]
}

@app.route('/')
def index():
    """Dashboard homepage"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Product Analytics Dashboard</title>
        <style>
            body { font-family: Arial; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            h1 { color: #333; }
            .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #f9f9f9; font-weight: bold; }
            .metric { font-size: 24px; color: #0066cc; font-weight: bold; }
            .label { color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Product Analytics Dashboard</h1>

            <div class="card">
                <h2>Warehouse Status</h2>
                <div id="status"></div>
            </div>

            <div class="card">
                <h2>Daily Metrics by Day of Week</h2>
                <div id="metrics"></div>
            </div>

            <div class="card">
                <h2>Top 10 Most Reordered Products</h2>
                <div id="products"></div>
            </div>

            <div class="card">
                <h2>Key Insights</h2>
                <div id="insights"></div>
            </div>
        </div>

        <script>
            async function loadData() {
                try {
                    // Load status
                    const status = await fetch('/api/status').then(r => r.json());
                    document.getElementById('status').innerHTML = `
                        <p><span class="label">Fact Orders:</span> <span class="metric">${status.fact_rows.toLocaleString()}</span> rows</p>
                        <p><span class="label">Users:</span> <span class="metric">${status.user_count.toLocaleString()}</span></p>
                        <p><span class="label">Products:</span> <span class="metric">${status.product_count.toLocaleString()}</span></p>
                        <p><span class="label">Reorder Rate:</span> <span class="metric">${status.reorder_rate}%</span></p>
                    `;

                    // Load metrics
                    const metrics = await fetch('/api/metrics').then(r => r.json());
                    let metricsHtml = '<table><tr><th>Day</th><th>Users</th><th>Orders</th><th>Items/Order</th><th>Reorder Rate</th></tr>';
                    metrics.forEach(row => {
                        metricsHtml += `<tr><td>${row.day}</td><td>${row.daily_users}</td><td>${row.orders}</td><td>${row.items_per_order}</td><td>${row.reorder_rate}</td></tr>`;
                    });
                    metricsHtml += '</table>';
                    document.getElementById('metrics').innerHTML = metricsHtml;

                    // Load top products
                    const products = await fetch('/api/top-products').then(r => r.json());
                    let productsHtml = '<table><tr><th>Product ID</th><th>Times Ordered</th><th>Reorder Rate</th></tr>';
                    products.forEach(row => {
                        productsHtml += `<tr><td>${row.product_id}</td><td>${row.times_ordered}</td><td>${row.reorder_rate}</td></tr>`;
                    });
                    productsHtml += '</table>';
                    document.getElementById('products').innerHTML = productsHtml;

                    // Load insights
                    const insights = await fetch('/api/insights').then(r => r.json());
                    document.getElementById('insights').innerHTML = `
                        <ul>
                            ${insights.map(i => `<li>${i}</li>`).join('')}
                        </ul>
                    `;
                } catch (error) {
                    console.error('Error loading data:', error);
                    document.body.innerHTML = '<p>Error loading dashboard. Make sure DuckDB database is available.</p>';
                }
            }

            loadData();
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/api/status')
def api_status():
    """Warehouse status metrics"""
    return jsonify(dashboard_data["status"])

@app.route('/api/metrics')
def api_metrics():
    """Daily metrics by day of week"""
    return jsonify(dashboard_data["metrics"])

@app.route('/api/top-products')
def api_top_products():
    """Top 10 most reordered products"""
    return jsonify(dashboard_data["top_products"])

@app.route('/api/insights')
def api_insights():
    """Key business insights"""
    return jsonify(dashboard_data["insights"])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
