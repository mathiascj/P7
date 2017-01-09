SELECT  *
FROM Expected
WHERE NOT EXISTS (
SELECT NULL
FROM BookDim
WHERE expected.title = BookDim.title AND
expected.version = BookDim.version
) 