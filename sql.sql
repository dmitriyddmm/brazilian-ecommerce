-- 3 продавца с наибольшей и наименьшей средними оценками в каждом штате каждый год
WITH joined AS (
    SELECT
        DATE_TRUNC('year', orders.purchase_timestamp) period,
        sellers.state,
        order_products.seller_id,
        reviews.score,
        orders.id order_id
    FROM
        reviews
            JOIN
        orders
        ON
            orders.id = reviews.order_id
            JOIN
        order_products
        ON
            order_products.order_id = orders.id
            JOIN
        sellers
        ON
            sellers.id = order_products.seller_id

),
pre_grouped AS (
    SELECT
        period,
        state,
        seller_id,
        order_id,
        AVG(score) score
    FROM
        joined
    GROUP BY
        period,
        state,
        seller_id,
        order_id
),
grouped AS (
    SELECT
        period,
        state,
        seller_id,
        AVG(score) score
    FROM
        pre_grouped
    GROUP BY
        period,
        state,
        seller_id
),
ranged_min AS (
    SELECT
        *
    FROM
        (
            SELECT
                period,
                state,
                seller_id,
                score,
                ROW_NUMBER() OVER (PARTITION BY state, period ORDER BY score) range,
                'min' type
            FROM grouped
        ) pre_ranged
    WHERE
        range <= 3
),
ranged_max AS (
    SELECT
        *
    FROM
        (
            SELECT
                period,
                state,
                seller_id,
                score,
                ROW_NUMBER() OVER (PARTITION BY state, period ORDER BY score DESC) range,
                'max' type
            FROM grouped
        ) pre_ranged
    WHERE
        range <= 3
)
SELECT
    *
FROM
    ranged_min
UNION ALL
SELECT
    *
FROM
    ranged_max

-- Ежемесячное количество заказов в каждом штате
WITH joined AS (
    SELECT
        customers.state,
        DATE_TRUNC('month', orders.purchase_timestamp) period
    FROM
        customers
            JOIN
        orders
        ON
            orders.customer_id = customers.id
),
grouped AS (
    SELECT
        *,
        COUNT(*)
    FROM
        joined
    GROUP BY
        state,
        period
    ORDER BY
        period,
        state
)
SELECT
    *
FROM
    grouped

-- Ежемесячное прибавление суммарного веса каждой категории за 2017 год
WITH joined AS (
    SELECT
        order_products.price,
        DATE_TRUNC('month', orders.purchase_timestamp) period,
        products.category_name
    FROM
        order_products
            JOIN
        orders
        ON
            orders.id = order_products.order_id
            JOIN
        products
        ON
            products.id = order_products.product_id
),
grouped AS (
    SELECT
        period,
        category_name,
        SUM(price) price
    FROM
        joined
    GROUP BY
        category_name,
        period
)
SELECT
    period,
    category_name,
    SUM(price) OVER (PARTITION BY category_name ORDER BY category_name, period ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) sum
FROM
    grouped
WHERE
    DATE_PART('year', period) = 2017

-- Ежегодная суммарная стоимость заказов в каждом штате
WITH joined AS (
    SELECT
        customers.state,
        DATE_TRUNC('year', orders.purchase_timestamp) period,
        order_products.price
    FROM
        customers
            JOIN
        orders
        ON
            orders.customer_id = customers.id
            JOIN
        order_products
        ON
            order_products.order_id = orders.id
),
grouped AS (
    SELECT
        state,
        period,
        SUM(price)
    FROM
        joined
    GROUP BY
        state,
        period
    ORDER BY
        state,
        period
)
SELECT
    *
FROM
    grouped

-- 5 покупателей с наибольшей средней стоимостью заказа каждый месяц
WITH joined AS (
    SELECT
        orders.customer_id,
        DATE_TRUNC('month', orders.purchase_timestamp) period,
        order_products.order_id,
        order_products.price
    FROM
        orders
            JOIN
        order_products
        ON
            order_products.order_id = orders.id
),
grouped_sum AS (
    SELECT
        customer_id,
        period,
        order_id,
        SUM(price) price
    FROM
        joined
    GROUP BY
        customer_id,
        period,
        order_id
),
grouped_AVG AS (
    SELECT
        customer_id,
        period,
        AVG(price) price
    FROM
        grouped_sum
    GROUP BY
        customer_id,
        period
),
ranged AS (
    SELECT
        period,
        customer_id,
        price,
        ROW_NUMBER() OVER (PARTITION BY period ORDER BY price DESC) range
    FROM
        grouped_AVG
)
SELECT
    *
FROM
    ranged
WHERE
    range <= 5

-- Ежемесячное прибавление суммарной стоимости заказов в каждом штате за 2017 год
WITH joined AS (
    SELECT
        order_products.price,
        DATE_TRUNC('month', orders.purchase_timestamp) period,
        customers.state
    FROM
        order_products
            JOIN
        orders
        ON
            orders.id = order_products.order_id
            JOIN
        customers
        ON
            customers.id = orders.customer_id
),
grouped AS (
    SELECT
        period,
        state,
        SUM(price) price
    FROM
        joined
    GROUP BY
        state,
        period
)
SELECT
    period,
    state,
    SUM(price) OVER (PARTITION BY state ORDER BY state, period ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) sum
FROM
    grouped
WHERE
    DATE_PART('year', period) = 2017

-- 5 самых больших доставленных объёмов в каждом штате каждый год
WITH joined AS (
    SELECT
        DATE_TRUNC('year', orders.purchase_timestamp) period,
        customers.state,
        products.length * products.height * products.width volume
    FROM
        customers
            JOIN
        orders
        ON
            orders.customer_id = customers.id
            JOIN
        order_products
        ON
            order_products.order_id = orders.id
            JOIN
        products
        ON
            products.id = order_products.product_id
),
ranged AS (
    SELECT
        period,
        state,
        volume,
        ROW_NUMBER() OVER (PARTITION BY state, period ORDER BY volume DESC) range
    FROM
        joined
)
SELECT
    *
FROM
    ranged
WHERE
    range <= 5

-- Ежемесячное изменение средней оценки каждого продавца
WITH joined AS (
    SELECT
        reviews.score,
        DATE_TRUNC('month', orders.purchase_timestamp) period,
        sellers.id
    FROM
        order_products
            JOIN
        orders
        ON
            orders.id = order_products.order_id
            JOIN
        sellers
        ON
            sellers.id = order_products.seller_id
            JOIN
        reviews
        ON
            reviews.order_id = orders.id
),
grouped AS (
    SELECT
        period,
        id,
        AVG(score) score
    FROM
        joined
    GROUP BY
        id,
        period
),
aggredated AS (
    SELECT
        id,
        period,
        AVG(score) OVER (PARTITION BY id ORDER BY id, period ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) score
    FROM
        grouped
)
SELECT
    id,
    period,
    score - LAG(score) OVER (PARTITION BY id ORDER BY id, period ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) score
FROM
    aggredated

-- Продавец с наибольшей средней оценкой в каждом штате каждый год
WITH joined AS (
    SELECT
        reviews.score,
        DATE_TRUNC('year', orders.purchase_timestamp) period,
        order_products.seller_id,
        sellers.state
    FROM
        order_products
            JOIN
        orders
        ON
            orders.id = order_products.order_id
            JOIN
        sellers
        ON
            sellers.id = order_products.seller_id
            JOIN
        reviews
        ON
            reviews.order_id = orders.id
),
grouped AS (
    SELECT
        period,
        seller_id,
        state,
        AVG(score) score
    FROM
        joined
    GROUP BY
        seller_id,
        state,
        period
),
aggregated AS (
    SELECT
        state,
        period,
        FIRST_VALUE(seller_id) OVER (PARTITION BY period, state) seller_id,
        FIRST_VALUE(score) OVER (PARTITION BY period, state) score
    FROM
        grouped
)
SELECT
    *
FROM
    aggregated
GROUP BY
    state,
    period,
    seller_id,
    score
ORDER BY
    state,
    period