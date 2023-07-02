from typing import Optional, Tuple
from scipy.stats import sigmaclip
from sklearn.preprocessing import MinMaxScaler
from rdp import rdp
import numpy as np
import pandas as pd

DAYS_TO_MONTHS = 30.4167


def days_to_months(days: int):
    return days / DAYS_TO_MONTHS


def calculate_days(data: pd.DataFrame, start_date, end_date,
                   censor_date=None, launch_column: str = 'launch_date',
                   failure_column: str = 'failure_date', failed_time_column: str = 'days_up',
                   running_time_column: str = 'running_days'):
    """
    Возвращает выборку из data, где start_date < data[launch_column] < end_date.
    Для строк с failure_column.notnull() вычисляет failed_time_column = failure_column - launch_column.
    Для строк с failure_column.isnull() вычисляет running_time_column = censor_date - launch_column.

    :param data:
    :param start_date:
    :param end_date:
    :param censor_date: Момент конца измерений (end_date if censor_date is None).
    :param launch_column:
    :param failure_column:
    :param failed_time_column:
    :param running_time_column:
    :return:
    """
    if not isinstance(start_date, pd.Timestamp):
        start_date = pd.to_datetime(start_date)
    if not isinstance(end_date, pd.Timestamp):
        end_date = pd.to_datetime(end_date)
    if start_date >= end_date:
        raise ValueError("Start date must be before end date.")

    if censor_date is None:
        censor_date = end_date
    elif not isinstance(censor_date, pd.Timestamp):
        censor_date = pd.to_datetime(censor_date)

    data = data[(data[launch_column] > start_date) & (data[launch_column] < end_date)].copy()

    data.loc[~data[failure_column].notnull(), failed_time_column] = (
            data[failure_column] - data[launch_column]).dt.days
    data = censor_dates(data, censor_date, launch_column, running_time_column, failure_column)

    return data


def censor_dates(data: pd.DataFrame, censor_date, launch_column: str = 'launch_date',
                 running_time_column: str = 'running_days', failure_column: str = 'failure_date'):
    if not isinstance(censor_date, pd.Timestamp):
        censor_date = pd.to_datetime(censor_date)

    data.loc[data[failure_column].isnull(), running_time_column] = (
            censor_date - pd.to_datetime(data[launch_column])).dt.days

    return data


def empirical_cdf(x: np.ndarray, length: int = None, sort: bool = True) -> np.ndarray:
    if length is None:
        length = len(x)

    if sort:
        x.sort()
    y = np.empty(length, dtype=float)
    for i in range(length):
        y[i] = (i + 1) / length

    return np.column_stack((x, y))


def quantile(p: float, shape: float, scale: float):
    return scale * np.power(-np.log(1 - p), 1 / shape)


def optimize_curve(points: np.ndarray, epsilon: float) -> np.ndarray:
    scaler = MinMaxScaler()
    points = scaler.fit_transform(points)
    points = rdp(points, epsilon)
    points = scaler.inverse_transform(points)
    return points


def weibull_cdf(shape: float, scale: float, num: int = 50, xmax: float = None,
                xmin: float = None) -> np.ndarray:
    if xmax is None:
        xmax = quantile(0.999, shape, scale)
    if xmin is None:
        xmin = quantile(0.001, shape, scale)
    x = np.linspace(xmin, xmax, num)
    y = 1 - np.exp(-np.power(x / scale, shape))
    return np.column_stack((x, y))


def drop_outliers(data: pd.DataFrame, column: str, sigma: float = 3):
    """
    @param data:
    @param column:
    @param sigma:
    @return:
    """
    _, low, upp = sigmaclip(data[column].dropna(), low=sigma, high=sigma)
    return data[data[column].isnull() | ((data[column] >= low) & (data[column] <= upp))].copy()
