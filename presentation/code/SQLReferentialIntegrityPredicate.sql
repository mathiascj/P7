SELECT *
FROM facttable
WHERE NOT EXISTS(
    SELECT NULL FROM author_dim
    WHERE facttable.aid = author_dim.aid
    )