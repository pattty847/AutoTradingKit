# -*- coding: utf-8 -*-
from numpy import (
    append,
    arange,
    array,
    convolve,
    copy,
    cos,
    empty_like,
    exp,
    finfo,
    float64,
    greater,
    int64,
    isnan,
    nan,
    ones,
    roll,
    sqrt,
    zeros,
    zeros_like,
    arctan
)
from numba import njit


@njit(cache=True)
def nb_roc(x, n, k):
    return k * nb_idiff(x, n) / nb_shift(x, n)


@njit(cache=True)
def nb_mom(x, n):
    return nb_idiff(x, n)


@njit(cache=True)
def fibonacci(n, weighted):
    n = n if n > 1 else 2
    sqrt5 = sqrt(5.0)
    phi, psi = 0.5 * (1.0 + sqrt5), 0.5 * (1.0 - sqrt5)

    result = zeros(n)
    for i in range(0, n):
        result[i] = float(phi ** (i + 1) - psi ** (i + 1)) / sqrt5

    if weighted:
        return result / result.sum()
    return result


@njit(cache=True)
def nb_non_zero_range(x, y):
    diff = x - y
    if diff.any() == 0:
        diff += finfo(float64).eps
    return diff

@njit(cache=True)
def nb_wma(x, n, asc, prenan):
    m = x.size
    w = arange(1, n + 1, dtype=float64)
    result = zeros_like(x, dtype=float64)

    if not asc:
        w = w[::-1]

    for i in range(n - 1, m):
        result[i] = (w * x[i - n + 1:i + 1]).sum()
    result *= 2 / (n * n + n)

    if prenan:
        result[:n - 1] = nan

    return result


# John F. Ehler's Super Smoother Filter by Everget (3 poles), Tradingview
# https://www.tradingview.com/script/VdJy0yBJ-Ehlers-Super-Smoother-Filter/
@njit(cache=True)
def nb_ssf3(x, n, pi, sqrt3):
    m, result = x.size, copy(x)
    a = exp(-pi / n)
    b = 2 * a * cos(-pi * sqrt3 / n)
    c = a * a

    d4 = c * c
    d3 = -c * (1 + b)
    d2 = b + c
    d1 = 1 - d2 - d3 - d4

    # result[:3] = x[:3]
    for i in range(3, m):
        result[i] = d1 * x[i] + d2 * result[i - 1] \
            + d3 * result[i - 2] + d4 * result[i - 3]

    return result


# Ehler's Super Smoother Filter
# http://traders.com/documentation/feedbk_docs/2014/01/traderstips.html
@njit(cache=True)
def nb_ssf(x, n, pi, sqrt2):
    m, ratio, result = x.size, sqrt2 / n, copy(x)
    a = exp(-pi * ratio)
    b = 2 * a * cos(180 * ratio)
    c = a * a - b + 1

    # result[:2] = x[:2]
    for i in range(2, m):
        result[i] = 0.5 * c * (x[i] + x[i - 1]) + b * result[i - 1] \
            - a * a * result[i - 2]

    return result


# John F. Ehler's Super Smoother Filter by Everget (2 poles), Tradingview
# https://www.tradingview.com/script/VdJy0yBJ-Ehlers-Super-Smoother-Filter/
@njit(cache=True)
def nb_ssf_everget(x, n, pi, sqrt2):
    m, arg, result = x.size, pi * sqrt2 / n, copy(x)
    a = exp(-arg)
    b = 2 * a * cos(arg)

    # result[:2] = x[:2]
    for i in range(2, m):
        result[i] = 0.5 * (a * a - b + 1) * (x[i] + x[i - 1]) \
            + b * result[i - 1] - a * a * result[i - 2]

    return result




# Fast SMA Options: https://github.com/numba/numba/issues/4119
@njit(cache=True)
def nb_sma(x, n):
    result = convolve(ones(n) / n, x)[n - 1:1 - n]
    return nb_prepend(result, n - 1)



@njit(cache=True)
def pivot_camarilla(high, low, close):
    tp = (high + low + close) / 3
    hl_range = nb_non_zero_range(high, low)

    s1 = close - 11 / 120 * hl_range
    s2 = close - 11 / 60 * hl_range
    s3 = close - 0.275 * hl_range
    s4 = close - 0.55 * hl_range

    r1 = close + 11 / 120 * hl_range
    r2 = close + 11 / 60 * hl_range
    r3 = close + 0.275 * hl_range
    r4 = close + 0.55 * hl_range

    return tp, s1, s2, s3, s4, r1, r2, r3, r4


@njit(cache=True)
def pivot_classic(high, low, close):
    tp = (high + low + close) / 3
    hl_range = nb_non_zero_range(high, low)

    s1 = 2 * tp - high
    s2 = tp - hl_range
    s3 = tp - 2 * hl_range
    s4 = tp - 3 * hl_range

    r1 = 2 * tp - low
    r2 = tp + hl_range
    r3 = tp + 2 * hl_range
    r4 = tp + 3 * hl_range

    return tp, s1, s2, s3, s4, r1, r2, r3, r4


@njit(cache=True)
def pivot_demark(open_, high, low, close):
    if (open_ == close).all():
        tp = 0.25 * (high + low + 2 * close)
    elif greater(close, open_).all():
        tp = 0.25 * (2 * high + low + close)
    else:
        tp = 0.25 * (high + 2 * low + close)

    s1 = 2 * tp - high
    r1 = 2 * tp - low

    return tp, s1, r1


@njit(cache=True)
def pivot_fibonacci(high, low, close):
    tp = (high + low + close) / 3
    hl_range = nb_non_zero_range(high, low)

    s1 = tp - 0.382 * hl_range
    s2 = tp - 0.618 * hl_range
    s3 = tp - hl_range

    r1 = tp + 0.382 * hl_range
    r2 = tp + 0.618 * hl_range
    r3 = tp + hl_range

    return tp, s1, s2, s3, r1, r2, r3


@njit(cache=True)
def pivot_traditional(high, low, close):
    tp = (high + low + close) / 3
    hl_range = nb_non_zero_range(high, low)

    s1 = 2 * tp - high
    s2 = tp - hl_range
    s3 = tp - 2 * hl_range
    s4 = tp - 2 * hl_range

    r1 = 2 * tp - low
    r2 = tp +  hl_range
    r3 = tp + 2 * hl_range
    r4 = tp + 2 * hl_range

    return tp, s1, s2, s3, s4, r1, r2, r3, r4


@njit(cache=True)
def pivot_woodie(open_, high, low):
    tp = (2 * open_ + high + low) / 4
    hl_range = nb_non_zero_range(high, low)

    s1 = 2 * tp - high
    s2 = tp - hl_range
    s3 = low - 2 * (high - tp)
    s4 = s3 - hl_range

    r1 = 2 * tp - low
    r2 = tp + hl_range
    r3 = high + 2 * (tp - low)
    r4 = r3 + hl_range

    return tp, s1, s2, s3, s4, r1, r2, r3, r4



# Ehler's Mother of Adaptive Moving Averages
# http://traders.com/documentation/feedbk_docs/2014/01/traderstips.html
@njit(cache=True)
def nb_mama(x, fastlimit, slowlimit, prenan):
    a, b, m = 0.0962, 0.5769, x.size
    p_w, smp_w, smp_w_c = 0.2, 0.33, 0.67

    wma4 = zeros_like(x)
    dt, smp = zeros_like(x), zeros_like(x)
    i1, i2 = zeros_like(x), zeros_like(x)
    ji, jq = zeros_like(x), zeros_like(x)
    q1, q2 = zeros_like(x), zeros_like(x)
    re, im, alpha = zeros_like(x), zeros_like(x), zeros_like(x)
    period, phase = zeros_like(x), zeros_like(x)
    mama, fama = zeros_like(x), zeros_like(x)

    # Ehler's starts from 6, TV-LB from 3, TALib from 32
    for i in range(3, m):
        adj_prev_period = 0.075 * period[i - 1] + 0.54

        # WMA(x,4) & Detrended WMA(x,4)
        wma4[i] = 0.4 * x[i] + 0.3 * x[i - 1] + 0.2 * x[i - 2] + 0.1 * x[i - 3]
        dt[i] = adj_prev_period * (a * wma4[i] + b * wma4[i - 2] - b * wma4[i - 4] - a * wma4[i - 6])

        # Quadrature(Detrender) and In Phase Component
        q1[i] = adj_prev_period * (a * dt[i] + b * dt[i - 2] - b * dt[i - 4] - a * dt[i - 6])
        i1[i] = dt[i - 3]

        # Phase Q1 and I1 by 90 degrees
        ji[i] = adj_prev_period * (a * i1[i] + b * i1[i - 2] - b * i1[i - 4] - a * i1[i - 6])
        jq[i] = adj_prev_period * (a * q1[i] + b * q1[i - 2] - b * q1[i - 4] - a * q1[i - 6])

        # Phasor Addition for 3 Bar Averaging
        i2[i] = i1[i] - jq[i]
        q2[i] = q1[i] + ji[i]

        # Smooth I2 & Q2
        i2[i] = p_w * i2[i] + (1 - p_w) * i2[i - 1]
        q2[i] = p_w * q2[i] + (1 - p_w) * q2[i - 1]

        # Homodyne Discriminator
        re[i] = i2[i] * i2[i - 1] + q2[i] * q2[i - 1]
        im[i] = i2[i] * q2[i - 1] + q2[i] * i2[i - 1]

        # Smooth Re & Im
        re[i] = p_w * re[i] + (1 - p_w) * re[i - 1]
        im[i] = p_w * im[i] + (1 - p_w) * im[i - 1]

        if im[i] != 0.0 and re[i] != 0.0:
            period[i] = 360 / arctan(im[i] / re[i])
        else:
            period[i] = 0

        if period[i] > 1.5 * period[i - 1]:
            period[i] = 1.5 * period[i - 1]
        if period[i] < 0.67 * period[i - 1]:
            period[i] = 0.67 * period[i - 1]
        if period[i] < 6:
            period[i] = 6
        if period[i] > 50:
            period[i] = 50

        period[i] = p_w * period[i] + (1 - p_w) * period[i - 1]
        smp[i] = smp_w * period[i] + smp_w_c * smp[i - 1]

        if i1[i] != 0.0:
            phase[i] = arctan(q1[i] / i1[i])

        dphase = phase[i - 1] - phase[i]
        if dphase < 1:
            dphase = 1

        alpha[i] = fastlimit / dphase
        if alpha[i] > fastlimit:
            alpha[i] = fastlimit
        if alpha[i] < slowlimit:
            alpha[i] = slowlimit

        mama[i] = alpha[i] * x[i] + (1 - alpha[i]) * mama[i - 1]
        fama[i] = 0.5 * alpha[i] * mama[i] + (1 - 0.5 * alpha[i]) * fama[i - 1]

    mama[:prenan], fama[:prenan] = nan, nan
    return mama, fama

# Numba version of ffill()
@njit(cache=True)
def nb_ffill(x):
    mask = isnan(x)
    idx = zeros_like(mask, dtype=int64)
    last_valid_idx = -1

    m = mask.size
    for i in range(m):
        if not mask[i]:
            last_valid_idx = i
        idx[i] = last_valid_idx
    return x[idx]


# Indexwise element difference by k indices of array x.
# Similar to Pandas Series/DataFrame diff()
@njit(cache=True)
def nb_idiff(x, k):
    n, k = x.size, int(k)
    result = zeros_like(x, dtype=float64)

    for i in range(k, n):
        result[i] = x[i] - x[i - k]
    result[:k] = nan

    return result


# Prepend n values, typically np.nan, to array x.
@njit(cache=True)
def nb_prenan(x, n, value = nan):
    if n > 0:
        x[:n - 1] = value
        return x
    return x


# Prepend n values, typically np.nan, to array x.
@njit(cache=True)
def nb_prepend(x, n, value = nan):
    return append(array([value] * n), x)


# Like Pandas Rolling Window. x.rolling(n).fn()
@njit(cache=True)
def nb_rolling(x, n, fn = None):
    if fn is None:
        return x
    m = x.size
    result = zeros_like(x, dtype=float)
    if n <= 0:
        return result  # TODO: Handle negative rolling windows

    for i in range(0, m):
        result[i] = fn(x[i:n + i])
    result = roll(result, n - 1)
    result[:n - 1] = nan
    return result


# np shift
# shift5 - preallocate empty array and assign slice by chrisaycock
# https://stackoverflow.com/questions/30399534/shift-elements-in-a-numpy-array
@njit(cache=True)
def nb_shift(x, n, value = nan):
    result = empty_like(x)
    if n > 0:
        result[:n] = value
        result[n:] = x[:-n]
    elif n < 0:
        result[n:] = value
        result[:n] = x[-n:]
    else:
        result[:] = x
    return result


# Uncategorized
# @njit(cache=True)
# def nb_roofing_filter(x: Array, n: Int, k: Int, pi: Float, sqrt2: Float):
#     """Ehler's Roofing Filter (INCOMPLETE)
#     http://traders.com/documentation/feedbk_docs/2014/01/traderstips.html"""
#     m, hp = x.size, np.copy(x)
#     # a = exp(-pi * sqrt(2) / n)
#     # b = 2 * a * cos(180 * sqrt(2) / n)
#     rsqrt2 = 1 / np.sqrt2
#     a  = (np.cos(rsqrt2 * 360 / n) + np.sin(rsqrt2 * 360 / n) - 1)
#     a /= np.cos(rsqrt2 * 360 / n)
#     b, c = 1 - a, (1 - a / 2)

#     for i in range(2, m):
#         hp = c * c * (x[i] - 2 * x[i - 1] + x[i - 2]) \
#             + 2 * b * hp[i - 1] - b * b * hp[i - 2]

#     result = nb_ssf(hp, k, pi, rsqrt2)
#     return result
