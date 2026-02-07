from impact_factor.core import Factor

fa = Factor()

print(fa.dbfile)

fa.search('0028-0836') 
fa.search('nature c%')

fa.filter(min_value=100, max_value=200)
fa.filter(min_value=100, max_value=200, pubmed_filter=True)