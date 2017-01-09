SELECT DISTINCT t1.country, t2.city
FROM countrydim NATURAL JOIN authordim AS t1, countrydim NATURAL JOIN authordim AS t2
WHERE t1.city = t2.city 
AND t1.country <> t2.country
