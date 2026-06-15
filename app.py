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
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
            .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
            h1 { color: #333; margin: 20px 0; font-size: 32px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
            .metric-card { text-align: center; }
            .metric-value { font-size: 32px; font-weight: bold; color: #0066cc; }
            .metric-label { color: #666; font-size: 14px; margin-top: 5px; }
            .chart-card { grid-column: span 2; }
            .insights-list { list-style: none; }
            .insights-list li { padding: 10px 0; border-bottom: 1px solid #eee; }
            .insights-list li:before { content: '✓ '; color: #0066cc; font-weight: bold; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th { background: #f0f0f0; padding: 10px; text-align: left; font-weight: 600; }
            td { padding: 10px; border-bottom: 1px solid #eee; }
            tr:hover { background: #f9f9f9; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Product Analytics Dashboard</h1>

            <div class="grid">
                <div class="card metric-card">
                    <div class="metric-label">Fact Orders</div>
                    <div class="metric-value" id="fact-rows">-</div>
                </div>
                <div class="card metric-card">
                    <div class="metric-label">Users</div>
                    <div class="metric-value" id="user-count">-</div>
                </div>
                <div class="card metric-card">
                    <div class="metric-label">Products</div>
                    <div class="metric-value" id="product-count">-</div>
                </div>
                <div class="card metric-card">
                    <div class="metric-label">Reorder Rate</div>
                    <div class="metric-value" id="reorder-rate">-</div>
                </div>
            </div>

            <div class="grid">
                <div class="card chart-card">
                    <h2>Daily Users by Day of Week</h2>
                    <canvas id="usersChart"></canvas>
                </div>
                <div class="card chart-card">
                    <h2>Reorder Rate by Day</h2>
                    <canvas id="reorderChart"></canvas>
                </div>
            </div>

            <div class="card">
                <h2>Top 10 Most Reordered Products</h2>
                <table>
                    <thead>
                        <tr><th>Product ID</th><th>Times Ordered</th><th>Reorder Rate</th></tr>
                    </thead>
                    <tbody id="products-table"></tbody>
                </table>
            </div>

            <div class="card">
                <h2>Key Insights</h2>
                <ul class="insights-list" id="insights"></ul>
            </div>
        </div>

        <script>
            let usersChart, reorderChart;

            async function loadData() {
                try {
                    // Load status
                    const status = await fetch('/api/status').then(r => r.json());
                    document.getElementById('fact-rows').textContent = status.fact_rows.toLocaleString();
                    document.getElementById('user-count').textContent = status.user_count.toLocaleString();
                    document.getElementById('product-count').textContent = status.product_count.toLocaleString();
                    document.getElementById('reorder-rate').textContent = status.reorder_rate + '%';

                    // Load metrics and create charts
                    const metrics = await fetch('/api/metrics').then(r => r.json());
                    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
                    const userCounts = metrics.map(m => m.daily_users);
                    const reorderRates = metrics.map(m => (m.reorder_rate * 100).toFixed(1));

                    // Users chart
                    const usersCtx = document.getElementById('usersChart').getContext('2d');
                    usersChart = new Chart(usersCtx, {
                        type: 'bar',
                        data: {
                            labels: days,
                            datasets: [{
                                label: 'Daily Users',
                                data: userCounts,
                                backgroundColor: '#0066cc',
                                borderColor: '#0052a3',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: { legend: { display: false } },
                            scales: { y: { beginAtZero: true } }
                        }
                    });

                    // Reorder rate chart
                    const reorderCtx = document.getElementById('reorderChart').getContext('2d');
                    reorderChart = new Chart(reorderCtx, {
                        type: 'line',
                        data: {
                            labels: days,
                            datasets: [{
                                label: 'Reorder Rate (%)',
                                data: reorderRates,
                                borderColor: '#0066cc',
                                backgroundColor: 'rgba(0, 102, 204, 0.1)',
                                borderWidth: 2,
                                fill: true,
                                tension: 0.4
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: { legend: { display: false } },
                            scales: { y: { min: 50, max: 65 } }
                        }
                    });

                    // Top products
                    const products = await fetch('/api/top-products').then(r => r.json());
                    let productsHtml = '';
                    products.forEach(p => {
                        productsHtml += `<tr><td>${p.product_id}</td><td>${p.times_ordered}</td><td>${(p.reorder_rate * 100).toFixed(0)}%</td></tr>`;
                    });
                    document.getElementById('products-table').innerHTML = productsHtml;

                    // Insights
                    const insights = await fetch('/api/insights').then(r => r.json());
                    document.getElementById('insights').innerHTML = insights.map(i => `<li>${i}</li>`).join('');

                } catch (error) {
                    console.error('Error:', error);
                    document.body.innerHTML = '<p>Error loading dashboard</p>';
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
