SELECT *
FROM (SELECT title,version,COUNT(*)
	  FROM Expected
	  GROUP BY title,version
WHERE NOT EXISTS (
SELECT NULL
FROM (SELECT title,version,COUNT(*)
	  FROM BookDim
	  GROUP BY title,version
WHERE expected.title = BookDim.title AND
expected.version <= BookDim.version
) 