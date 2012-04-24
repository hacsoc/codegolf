import math
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib.numerix import arange
import warnings

class F(object):

    def __init__(self, I):
        self.I = I
        self.first = True

    def __call__(self, i, x):
        if self.first:
            self.first = False
            l = list()
            if i[0] == self.I: l.append(i[1])
            if x[0] == self.I: l.append(x[1])
            return l
        else:
            if x[0] == self.I: i.append(x[1])
            return i

def select_col(T, col):
    return reduce(F(col), map(tuple, ((i,col) for j, row in enumerate(T) for i, col in enumerate(row))))

def pplot(path, x, text):
    #N = float(len(x))
    x = sorted([float(item) for item in x])
    # ------------------ liberated from scipy.stats.morestats ------------------
    N = len(x)
    Ui = np.zeros(N) * 1.0
    Ui[-1] = 0.5**(1.0 /N)
    Ui[0] = 1 - Ui[-1]
    i = arange(2, N)
    Ui[1:-1] = (i - 0.3175) / (N + 0.365)
    y = stats.norm.ppf(Ui)
    ## -------------------------------------------------------------------------
    regressionplot(path, x, y, text, 'Normal Score', pi=True)
    
    #plt.clf()
    #with warnings.catch_warnings():
        #warnings.simplefilter("ignore")
        #stats.probplot(x, dist='norm', plot=plt)
    #plt.savefig(path, format='png')

    #plt.clf()

def boxplot(path, *args):
    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    ax.boxplot(args)
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

def regressionplot(path, X, Y, xtext, ytext, pi=True):
    plt.clf()
    X, Y = tuple(X), tuple(Y)
    slope, intercept, _, _, _, CI, PI, _, bag = regression(X, Y)
    lowCI, highCI = CI(.99)
    lowPI, highPI = PI(.99)
    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    ax.xaxis.set_label_text(xtext)
    ax.yaxis.set_label_text(ytext)
    data = ax.scatter(X, Y)
    lineX = arange(min(X), max(X), 0.05)
    fit = ax.plot(lineX, [(slope*x + intercept) for x in lineX])
    ci = ax.plot(lineX, lowCI(lineX), 'r--')
    ax.plot(lineX, highCI(lineX), 'r--')
    if pi:
        pi = ax.plot(lineX, lowPI(lineX), 'g--')
        ax.plot(lineX, highPI(lineX), 'g--')
        plt.legend((data, fit, ci, pi), ('Data', 'Regression', '99% CI', '99% PI'), 'lower right')
    else:
        plt.legend((data, fit, ci), ('Data', 'Regression', '99% CI'), 'lower right')
    plt.savefig(path, format='png')
    plt.clf()
    return bag
    
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

def residualplots(prefix, X, Y, slope, intercept):
    X, Y = tuple(X), tuple(Y)
    assert len(X) == len(Y)
    #N = float(len(X))
    #X_ = np.mean(X) # X bar
    #Y_ = np.mean(Y) # Y bar
    #XrYr = sum(float(x-X_)*float(y-Y_) for x, y in zip(X, Y)) # X residuals
    #Xr2 = SS(float(x-X_) for x in X) # Sum of Squares of X residuals
    yhat = lambda x: slope*x + intercept
    
    residuals = [y-yhat(x) for x, y in zip(X, Y)]
    
    pplot(prefix + 'Rpplot.png', residuals, 'Residuals')
    histplot(prefix + 'Rhist.png', residuals)
    orderplot(
      prefix + 'Rorder.png', [i for i in xrange(1, len(residuals)+1)], residuals,
      'Observation Order', 'Residuals')
    #boxplot(
      #prefix + 'Rbox.png', *grouped_residuals)


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
    a = tuple(a)
    a, axis = _chk_asarray(a, axis)
    return np.sum(a*a, axis)

def regression(X, Y):
    '''Performs linear regression for X and Y (response)

    @returns : slope, intercept'''
    X, Y = tuple(X), tuple(Y)
    assert len(X) == len(Y)
    N = float(len(X))
    X_ = np.mean(X) # X bar
    Y_ = np.mean(Y) # Y bar
    XrYr = sum(float(x-X_)*float(y-Y_) for x, y in zip(X, Y)) # X residuals
    Xr2 = SS(float(x-X_) for x in X) # Sum of Squares of X residuals

    slope = (XrYr)/Xr2 # B1
    intercept = Y_ - slope*X_ # B0
    yhat = lambda x: slope*x + intercept
    SS_total = SS(y-Y_ for y in Y)
    SS_regression = SS(yhat(x)-Y_ for x,y in zip(X,Y))
    SS_error = SS(y-yhat(x) for x,y in zip(X,Y))
    var_est = SS_error/float(N-2)
    std_est = math.sqrt(var_est)
    R2 = 1. - (SS_error/SS_total)
    SE_slope = math.sqrt(var_est/Xr2)
    SE_intercept = math.sqrt(var_est*((1./N)+((X_**2.)/Xr2)))
    def r(v):
      return round(v, 3)

    def T_Test(alpha):
      Ta = -1*stats.t.ppf(alpha/2., N-2)
      #print 'Ta =', Ta
      slope_stat = lambda hypothesis: (slope - hypothesis)/SE_slope

      hypothesis = 0
      slope_statistic = abs(slope_stat(hypothesis))
      slope_p = 1 - stats.t.cdf(slope_statistic, N-2)
      intercept_statistic = abs((intercept - hypothesis)/SE_intercept)
      intercept_p = 1 - stats.t.cdf(intercept_statistic, N-2)
      print slope_p, alpha, slope_p < alpha
      table = (
          ('Var', 'Name', 'Value', 'SE', 'Test Statistic', 'Pval', 'T$_{\\alpha}$',
              'Reject?'),
          ('Slope', '$\\beta_{1}$', r(slope), r(SE_slope), r(slope_statistic),
              r(slope_p), r(Ta), str(slope_p < alpha)),
          ('Intercept', '$\\beta_{0}$', r(intercept), r(SE_intercept),
              r(intercept_statistic), r(intercept_p), r(Ta),
              str(intercept_p < alpha))
      )
      return table
      
    def ANOVA():
        df_regression = 1.0
        df_error = N-2.0
        df_total = df_regression + df_error
        MS_regression = SS_regression/df_regression
        MS_error = SS_error/df_error
        Fo = MS_regression/MS_error
        p_val = 1 - stats.f.cdf(Fo, 1, N-2.0)
        table = (
            ('Source',     'DF', 'SS', 'MS', 'F', 'P'),
            ('Regression', r(df_regression), r(SS_regression), r(MS_regression),
                r(Fo), r(p_val)),
            ('Error', r(df_error), r(SS_error), r(MS_error), '', ''),
            ('Total', r(df_total), r(SS_total), '', '', ''),
        )
        return table

    def CI(conf):
        Ta = stats.t.ppf((1. - float(conf))/2., N-2)
        slope_low = slope - Ta*SE_slope
        slope_high = slope + Ta*SE_slope
        intercept_low = intercept - Ta*SE_intercept
        intercept_high = intercept + Ta*SE_intercept
        return (slope_low, slope_high), (intercept_low, intercept_high) 
    
    def responseCI(conf):
        Ta = stats.t.ppf((1. - float(conf))/2., N-2)
        y = lambda x: slope*x + intercept
        SE_line = lambda x: math.sqrt(var_est*((1./N)+(((x-X_)**2.)/Xr2)))
        return (
          lambda line: [y(x) - Ta*SE_line(x) for x in line],
          lambda line: [y(x) + Ta*SE_line(x) for x in line]
        )
    
    def responsePI(conf):
        Ta = stats.t.ppf((1. - float(conf))/2., N-2)
        y = lambda x: slope*x + intercept
        # -------------------------------------+
        #                                      |       difference from CI
        #                                      v
        SE_line = lambda x: math.sqrt(var_est*(1+(1./N)+(((x-X_)**2.)/Xr2)))
        return (
          lambda line: [y(x) - Ta*SE_line(x) for x in line],
          lambda line: [y(x) + Ta*SE_line(x) for x in line]
        )

    def correlation(alpha):
        r = slope*math.sqrt(Xr2/SS_total)
        To = (r*math.sqrt(N-3))/math.sqrt(1. - r**2.)
        pval = 1 - stats.t.cdf(To, N-2)
        #print 'Correlation?'
        #print ' '*2, 'To', To
        #print ' '*2, 'P-Val', pval
        #print ' '*2, 'result', pval <= alpha
        return To, pval
    return slope, intercept, T_Test, ANOVA, CI, responseCI, responsePI, correlation, locals()

def mean_comparison(treatments):

    N = sum(
      (len(t) - 1)*(np.var(t, ddof=1))
      for k, t in treatments)
    D = float(sum(len(t) for k, t in treatments) - len(treatments))
    pooled_stdev = math.sqrt(N/D)
    #print 'pooled stdev', pooled_stdev

    table = [['Treatment Level', 'Mean', 'Stdev', 'CI (80\%)']]
    for level, t in treatments:
        ci_low, ci_high = stats.norm(loc=np.mean(t), scale=pooled_stdev).interval(.20)
        table.append((level, round(np.mean(t), 3), round(np.std(t, ddof=1), 3),
          '(%s, %s)' % (round(ci_low, 3), round(ci_high, 3))))
    return table, pooled_stdev

def textable(table, caption='A Table', label='table'):
  #'r' if str(c).isdigit() else 'l'
    #header  = ' '*0 + r'\begin{figure*}[h!]' + '\n'
    #header += ' '*2 + r'\begin{center}' + '\n'
    #header = (' '*2 + r'\subfigure[%s] {' + '\n') % (caption,)
    header = ' '*0 + r'\begin{tabular}'
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
    #footer += (' '*4 + r'\label{%s}' + '\n') % label
    #footer += ' '*2 + '}\n'
    #footer += ' '*2 + r'\end{center}' + '\n'
    #footer += (' '*2 + r'\caption{%s}' + '\n') % caption
    #footer += ' '*0 + r'\end{figure*}' + '\n'
    return '\n'.join((header, body, footer))
