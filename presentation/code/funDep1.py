# Creates part of select statement to get keys
select_alpha = ["t1." + str(a) for a in self.alpha]
select_beta = ["t2." + str(b) for b in self.beta]
select_sql = select_alpha + select_beta

# SQL setup for the left side of the dependency in WHERE-clause
alpha_sql_generator = (" t1.{} = t2.{} ".format(a, a)
                       for a in self.alpha)
and_alpha = ' AND '.join(alpha_sql_generator)

# SQL setup for the right side of the dependency in WHERE-clause
beta_sql_generator = (" (t1.{} <> t2.{}) ".format(b, b)
                      for b in self.beta)
or_beta = ' OR '.join(beta_sql_generator)