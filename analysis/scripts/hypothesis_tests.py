import statsmodels.api as sm

def correlation_test(x, y, weight=None):
  """
  Calculates p-value for either OLS or WLS for y = mx + const.
    (does WLS if weight is not None, otherwise OLS)

  X, Y, and WEIGHT should be pandas series (or 1-column DataFrames)
    with the state 2-letter abbreviations as indexes.
  """
  weighted = weight is not None
  X = sm.add_constant(x)

  if weighted:
    model = sm.WLS(y, X, weights=weight)
  else:
    model = sm.OLS(y, X)
  
  results = model.fit()
  pvals = results.pvalues

  return pvals[-1], results.params