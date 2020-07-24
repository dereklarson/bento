import pandas as pd
import numpy as np

# import datetime as dt

from scipy.optimize import curve_fit

from bento.common.logger import fancy_logger
from bento.common.util import id_func

logging = fancy_logger(__name__)


class FitFunc:
    @staticmethod
    def linear(x, a, b):
        return a + b * x

    @staticmethod
    def quadratic(x, a, b, c):
        return a + b * x + c * x ** 2


def fit_cases(
    idf,
    x_column,
    y_column,
    filters=[],
    y_scale="linear",
    fitfunc="linear",
    fitrange=[-7, 7],
    **kwargs,
):

    # TODO expand to fit more than just dates, but for now exit if not 'Date'
    if x_column.lower() != "date":
        logging.info("Currently not support fitting for non-Date columns")
        return idf

    fit_points, points_to_predict = fitrange
    fit_df = pd.DataFrame()
    for item in filters:
        logging.debug(f"Fitting with filter: {item}")
        column, value = item

        fdf = idf[idf[column] == value]
        newest = fdf[x_column].max()
        # Get the most common point-2-point interval to determinate a granularity
        scale = fdf[x_column].diff().mode()[0]
        logging.debug(f"Newest date: {newest}, scale: {scale})")
        fdf = fdf[fdf[x_column] > (newest + fit_points * scale)]

        transform = id_func
        inverse = id_func
        if y_scale == "log":

            def log10(x):
                return np.log10(1 + x)

            def pow10(x):
                return np.power(10, x) - 1

            transform = log10
            inverse = pow10

        xd = [(x - newest) / scale for x in fdf[x_column]]
        yd = [transform(y) for y in fdf[y_column]]

        curve = getattr(FitFunc, fitfunc)
        coeff, err = curve_fit(curve, xd, yd)

        xp = [xd[-1] + day + 1 for day in range(points_to_predict)]

        new_data = [
            {
                column: value,  # + "_fit",
                x_column: newest + x * scale,
                y_column: inverse(curve(x, *coeff)),
            }
            for x in xp
        ]

        fit_df = pd.concat([fit_df, pd.DataFrame(new_data)])

    return pd.concat([idf, fit_df], sort=True)

    # fit_x = idf[idf[column] == value][fit_points:]
    # fit_y = data["y"][fit_points:]
    # newest = fit_x.max()
    # fit_x = (fit_x - newest).apply(lambda x: x.days)

    # transform = id_func
    # if y_scale == "log":
    #     fit_y = np.log10(1 + fit_y)

    #     def pow10(x):
    #         return np.power(10, 1 + x)

    #     transform = pow10

    # curve = getattr(FitFunc, fitfunc)
    # coeff, err = curve_fit(curve, list(fit_x), list(fit_y))

    # xp = [list(fit_x)[-1] + day + 1 for day in range(points_to_predict)]

    # x_new = pd.Series([newest + dt.timedelta(days=x) for x in xp])
    # y_new = pd.Series([transform(curve(x, *coeff)) for x in xp])

    # data["x"] = data["x"].append(x_new)
    # data["y"] = data["y"].append(y_new)
    # data["text"] = data["text"].append(pd.Series(["Fit"] * len(x_new)))
