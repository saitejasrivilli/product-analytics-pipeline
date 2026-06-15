-- Generic test: ensure table has rows
{% test row_count_greater_than_zero(model) %}

select count(*) as row_count
from {{ model }}
having count(*) = 0

{% endtest %}
