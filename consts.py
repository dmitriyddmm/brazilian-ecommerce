sql_queries = {
    # 3 продавца с наибольшей и наименьшей средними оценками в каждом штате каждый год
    'max_min_score': """
        WITH joined AS (
            SELECT
                date_trunc('year', orders.purchase_timestamp) period,
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
                avg(score) score
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
            avg(score) score
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
                        row_number() OVER (PARTITION BY state, period ORDER BY score) range,
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
                        row_number() OVER (PARTITION BY state, period ORDER BY score DESC) range,
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
    """,
    # Ежемесячное количество заказов в каждом штате
    'count_orders': """
        WITH joined AS (
            SELECT
                customers.state,
                date_trunc('month', orders.purchase_timestamp) period
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
    """,
    # Ежемесячное прибавление суммарного веса каждой категории за 2017 год
    'changing_weight': """
        WITH joined AS (
            SELECT
                order_products.price,
                date_trunc('month', orders.purchase_timestamp) period,
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
        
        -- Оконная функция суммирует цену для каждой категории с первого до текущего месяца
        SELECT
            period,
            category_name,
            SUM(price) OVER (PARTITION BY category_name ORDER BY category_name, period ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) sum
        FROM
            grouped
        WHERE
            date_part('year', period) = 2017
    """,
    # Ежегодная суммарная стоимость заказов в каждом штате
    'sum_price': """
        WITH joined AS (
            SELECT
                customers.state,
                date_trunc('year', orders.purchase_timestamp) period,
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
    """,
    # 5 покупателей с наибольшей средней стоимостью заказа каждый месяц
    'avg_price': """
        WITH joined AS (
            SELECT
                orders.customer_id,
                date_trunc('month', orders.purchase_timestamp) period,
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
                sum(price) price
            FROM
                joined
            GROUP BY
                customer_id,
                period,
                order_id
        ),
        grouped_avg AS (
            SELECT
                customer_id,
                period,
                avg(price) price
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
                row_number() OVER (PARTITION BY period ORDER BY price DESC) range
            FROM
                grouped_avg
        )
        
        SELECT
            *
        FROM
            ranged
        WHERE
            range <= 5
    """,
    # Ежемесячное прибавление суммарной стоимости заказов в каждом штате за 2017 год
    'changing_price': """
        WITH joined AS (
            SELECT
                order_products.price,
                date_trunc('month', orders.purchase_timestamp) period,
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
        
        -- Оконная функция суммирует цену для каждого штата с первого до текущего месяца указанного года
        SELECT
            period,
            state,
            SUM(price) OVER (PARTITION BY state ORDER BY state, period ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) sum
        FROM
            grouped
        WHERE
            date_part('year', period) = 2017
    """,
    # 5 самых больших доставленных объёмов в каждом штате каждый год
    'max_volume': """
       WITH joined AS (
            SELECT
                date_trunc('year', orders.purchase_timestamp) period,
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
                row_number() OVER (PARTITION BY state, period ORDER BY volume DESC) range
            FROM
                joined
        )
        
        SELECT
            *
        FROM
            ranged
        WHERE
            range <= 5
    """,
    # Ежемесячное изменение средней оценки каждого продавца
    'changing_score': """
        WITH joined AS (
            SELECT
                reviews.score,
                date_trunc('month', orders.purchase_timestamp) period,
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
        -- Оконная функция вычисляет среднюю оценку для каждого продавца с первого до текущего месяца
        aggredated AS (
            SELECT
                id,
                period,
                AVG(score) OVER (PARTITION BY id ORDER BY id, period ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) score
            FROM
                grouped
        )
        
        -- Оконная функция показывает изменение средней оценки по сравнению с прошлым месяцем
        SELECT
            id,
            period,
            score - LAG(score) OVER (PARTITION BY id ORDER BY id, period ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) score
        FROM
            aggredated
    """,
    # Продавец с наибольшей средней оценкой в каждом штате каждый год
    'max_score': """
    WITH joined AS (
        SELECT
            reviews.score,
            date_trunc('year', orders.purchase_timestamp) period,
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
    -- После этой функции вычислены средние оценки каждого продавца за каждый год в каждом штате
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
    -- Оконная функция показывает продавца с наибольшей оценкой за год в штате и его оценку
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
    """
}