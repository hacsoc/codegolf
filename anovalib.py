import math
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import warnings
import single_regression as sr

def pplot(path, x):
    x = sorted([float(item) for item in x])
    y = [100.0*((j - 0.5)/float(len(x))) for j in xrange(1, len(x)+1)]
    plt.clf()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        stats.probplot(x, dist='norm', plot=plt)
    plt.savefig(path, format='png')

    plt.clf()

def boxplot(path, labels, *args):
    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    ax.boxplot(args)
    ax.set_xticklabels(labels)
    plt.savefig(path, format='png')
    plt.clf()

def scatterplot(path, x, y, xtext, ytext):
    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    ax.xaxis.set_label_text(xtext)
    ax.yaxis.set_label_text(ytext)
    ax.scatter(x, y)
    plt.savefig(path, format='png')
    plt.clf()

def orderplot(path, x, y, xtext, ytext):
    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    ax.xaxis.set_label_text(xtext)
    ax.yaxis.set_label_text(ytext)
    ax.scatter(x, y)
    ax.plot([i for i in xrange(-2, len(x)+2)], [0 for i in xrange(-2, len(x)+2)])
    plt.savefig(path, format='png')
    plt.clf()


def histplot(path, x):
    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    #ax.xaxis.set_label_text(xtext)
    #ax.yaxis.set_label_text(ytext)
    ax.hist(x)
    plt.savefig(path, format='png')
    plt.clf()

def residualplots(prefix, labels, treatments):
    tot_mean = np.mean([ob for k, t in treatments for ob in t])
    residuals = [ob - tot_mean for k, t in treatments for ob in t]
    grouped_residuals = [[ob - tot_mean for ob in t] for k, t in treatments ]
    sr.pplot(prefix + 'Rpp.png', residuals, 'residuals')
    histplot(prefix + 'Rhist.png', residuals)
    orderplot(
      prefix + 'Rorder.png', [i for i in xrange(1, len(residuals)+1)], residuals,
      'Observation Order', 'Residuals')
    boxplot(
      prefix + 'Rbox.png', labels, *grouped_residuals)


def _chk_asarray(a, axis):
    if axis is None:
        a = np.ravel(a)
        outaxis = 0
    else:
        a = np.asarray(a)
        outaxis = axis
    return a, outaxis

## From scipy.stats
def SS(a, axis=0):
    """Squares each value in the passed array, adds these squares, and
    returns the result.

    Parameters
    ----------
    a : array
    axis : int or None

    Returns
    -------
    The sum along the given axis for (a*a).
    """
    a, axis = _chk_asarray(a, axis)
    return np.sum(a*a, axis)

## From scipy.stats
def square_of_sums(a, axis=0):
    """Adds the values in the passed array, squares that sum, and returns the
    result.

    Returns: the square of the sum over axis.
    """
    a, axis = _chk_asarray(a, axis)
    s = np.sum(a,axis)
    if not np.isscalar(s):
        return s.astype(float)*s
    else:
        return float(s)*s

def f_oneway(*treatments):
    alldata = np.concatenate(treatments)
    a = float(len(treatments))
    n = float(len(treatments[0]))
    assert all(n == len(t) for t in treatments)
    N = float(len(alldata))

    tot_mean = np.mean([ob for t in treatments for ob in t])

    SS_total = sum((ob - tot_mean)**2 for t in treatments for ob in t)
    SS_treatments = n*sum((np.mean(t) - tot_mean)**2 for t in treatments)
    SS_error = sum((ob - np.mean(t))**2 for t in treatments for ob in t)
    assert round(SS_total, 8) == round(SS_treatments + SS_error, 8)

    df_treatments = (a - 1)
    MS_treatments = SS_treatments/df_treatments
    df_error = (a*(n - 1))
    MS_error = SS_error/df_error
    df_total = df_treatments + df_error

    f0 = MS_treatments / MS_error
    fa = 1 - stats.f.cdf(f0, df_treatments, df_error)
    p_val = 1 - stats.f.cdf(f0, df_treatments, df_error)

    def r(v):
        return round(v, 3)

    table = (
        ('Source',     'DF', 'SS', 'MS', 'F', 'P'),
        ('Treatment', r(df_treatments), r(SS_treatments), r(MS_treatments),
            r(f0), r(p_val)),
        ('Error', r(df_error), r(SS_error), r(MS_error), '', ''),
        ('Total', r(df_total), r(SS_total), '', '', ''),
    )

    return table

def mean_comparison(treatments):

    N = sum(
      (len(t) - 1)*(np.var(t, ddof=1))
      for k, t in treatments)
    D = float(sum(len(t) for k, t in treatments) - len(treatments))
    pooled_stdev = math.sqrt(N/D)
    #print 'pooled stdev', pooled_stdev

    table = [['', 'Min', 'Mean', 'Stdev', 'CI (95%)']]
    for level, t in treatments:
        ci_low, ci_high = stats.norm(loc=np.mean(t), scale=pooled_stdev).interval(.05)
        table.append((level, round(min(t), 3), round(np.mean(t), 3), round(np.std(t, ddof=1), 3),
          '(%s, %s)' % (round(ci_low, 3), round(ci_high, 3))))
    return table, pooled_stdev

def textable(table, caption='A Table', label='table'):
  #'r' if str(c).isdigit() else 'l'
    #header  = ' '*0 + r'\begin{figure*}[h!]' + '\n'
    #header += ' '*2 + r'\begin{center}' + '\n'
    header = (' '*2 + r'\subfigure[%s] {' + '\n') % (caption,)
    header += ' '*4 + r'\begin{tabular}'
    header += (
        '{| l | ' +
        ' | '.join(
          'r' if str(c).replace('.', '').isdigit() else 'l'
          for c in table[1][1:]
        ) + ' |}'
    )
    header += '\n'
    header += ' '*6 + r'\hline'
    body = (
      ' '*6 +
      (r' \\ \hline ' + '\n' + ' '*6).join(
        ' & '.join(str(c) for c in row) for row in table
      ) + r' \\ \hline '
    )
    footer  = ' '*4 + r'\end{tabular}' + '\n'
    footer += (' '*4 + r'\label{%s}' + '\n') % label
    footer += ' '*2 + '}\n'
    #footer += ' '*2 + r'\end{center}' + '\n'
    #footer += (' '*2 + r'\caption{%s}' + '\n') % caption
    #footer += ' '*0 + r'\end{figure*}' + '\n'
    return '\n'.join((header, body, footer))
