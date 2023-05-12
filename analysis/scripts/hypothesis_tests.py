import statsmodels.api as sm
from tqdm import tqdm
import numpy as np


# A/B Testing Code from HW1
def mean_calculation(dataset, binary_col, numerical_col):
    data = dataset[[binary_col, numerical_col]]
    means_table = data.groupby(binary_col).mean().reset_index()
    means = means_table.iloc[:, 1]
    observed_mean = abs(means[1] - means[0])
    return observed_mean


def avg_difference_in_means(dataset,
                            binary_col,
                            numerical_col,
                            weight_col=None,
                            reps=25000):
    observed_difference = mean_calculation(dataset, binary_col, numerical_col)

    differences = []
    for _ in tqdm(range(reps)):
        dataset["shuffled"] = dataset[binary_col].sample(
            len(dataset),
            weights=dataset[weight_col]).values
        shuffled_df = dataset[["shuffled", numerical_col]]
        new_mean = mean_calculation(shuffled_df, "shuffled", numerical_col)
        differences.append(new_mean)

    p_val = np.mean(differences >= observed_difference)
    return p_val


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