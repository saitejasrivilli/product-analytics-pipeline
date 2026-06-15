-- Generic test: ensure null rate is below threshold
-- Usage: - null_rate_check: column_name: order_id, threshold: 0.01
{% test null_rate_check(model, column_name, threshold=0.05) %}

select
    cast(sum(case when {{ column_name }} is null then 1 else 0 end) as float) / count(*) as null_rate
from {{ model }}
having null_rate > {{ threshold }}

{% endtest %}
