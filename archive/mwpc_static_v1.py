import numpy as np
import pandas as pd
import matplotlib.pylab as plt
import matplotlib.dates as md
import time

from scipy.optimize import curve_fit
from scipy.optimize import leastsq
from scipy.stats import norm

from database_call_v0 import lgdb_tools
from datetime import datetime, timedelta
tf = '%Y-%m-%d %H:%M:%S'

xfmt = md.DateFormatter('%d-%b %H:%M:%S')
dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f')

directory = 'G:/Websites/t/thornton/images/mwpc/'

def main():

    while True:
        message1, message2 = running()
        print('{} - {}, {}'.format(datetime.now().strftime(tf), message1, message2))

        if message1=='OK!':
            time.sleep(120)
        elif message1=='SKIPPED!':
            time.sleep(600)

def running():

    variable_name_h = 'MWPC.ZT8.135:PROFILE_H'
    variable_name_v = 'MWPC.ZT8.135:PROFILE_V'

    filename_v = 'mwpc_v'
    filename_h = 'mwpc_h'

    t1 = (datetime.now()-timedelta(hours=1)).strftime(tf)
    #t1 = '2015-05-18 20:00:00'
    t_now = (datetime.now()).strftime(tf)
    #t2 = '2015-05-20 06:00:00'

    t_check = t_now
    #t_check = '2015-05-26 06:00:01'

    a = lgdb_tools()
    output1 = a.get_data(variable_name_h, t1, t_now, filename_h)
    output1 = a.get_data(variable_name_v, t1, t_now, filename_v)

    n_spills = 10

    message1 = mwpc(filename_h, t_check, n_spills)
    message2 = mwpc(filename_v, t_check, n_spills)

    return message1, message2

def mwpc(filename, t_target, n_spills):

    filename = './data/{}.csv'.format(filename)

    df = mwpc_read(filename, t_target, n_spills)

    if not df.empty and df.ix[-1].max()>0.2:
        df_s = mwpc_last_spills(df, filename)
        df_a = mwpc_last_spills_avg(df, filename, n_spills)
        return 'OK!'
    elif df.empty:
        return 'SKIPPED!'

def gauss(x, A, mu, sigma):
    p = -(x-mu)**2/(2.*sigma**2)
    p = list(p) # need to convert to list in order for np.exp to work
    return A*np.exp(p)

def gaussian_fit_test(x_data,y_data):
    y_offset = np.min(y_data)
    x = np.array(x_data)
    y = np.array(y_data)-y_offset

    x_fine = np.arange(-100, 100, 0.1)  # x array, with finer resolution
    p = [1.0, 1.0, 75.0]             # initial fit params
    coeff, pcov = curve_fit(gauss, x, y, p) # fit the params, get coeffs
    y_fit = gauss(x_fine, *coeff)+y_offset                      # make a nice gaussian with fine x array

    peak,     centre,     sigma     = coeff
    peak_err, centre_err, sigma_err = np.sqrt(np.diag(pcov))

    fwhm = 2.355*sigma
    err_sigma  = (sigma_err/sigma)*100                    # std/sigma, % error for the FWHM value
    return x_fine, y_fit, fwhm, err_sigma, centre, centre_err

def mwpc_read(filename, t_target, n_spills):
    headers = ['Time [local]']+range(32)
    df = pd.read_csv(filename, delimiter=',', names=headers, index_col=False, skiprows=8)
    df['Time [local]'] = pd.to_datetime(df['Time [local]'])
    #df = df[df.columns[0].notnull()]
    df = df.set_index('Time [local]')
    df = df[:t_target][-n_spills:]
    #check if no beam (i.e. no data in df)
    return df


def mwpc_last_spills(df, filename):
    spacing = 6.0 # mm
    L = spacing*len(df.T)
    y_max = df.max().max()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    x = ((np.array(df.sum().index))*spacing)-(L/2.0)+(spacing/2)
    for i, index in enumerate(df.index):
        y = df.ix[i]
        index = str(index)
        stime = index.split(' ')[1].split('.')[0]
        sdate = index.split(' ')[0]
        ax.plot(x,y, ls='steps-mid', label=stime, linewidth=2)

    ax.grid()
    ax.set_xlabel('x [mm]')
    ax.set_ylabel('y')
    ax.set_title('MWPC ({}) {}'.format(sdate, filename))
    ax.legend()
    ax.set_ylim(top=y_max*1.2)

    figname = filename.split('_')[1].split('.')[0]
    filename_figure = '{}{}_1.png'.format(directory, figname)
    fig.savefig(filename_figure)
    plt.close(fig)
    return df

def mwpc_last_spills_avg(df, filename, n_spills):
    df_s = df.sum()
    df_d = df.std(axis=0)

    t_start = str(df.index[0]).split('.')[0]
    t_end   = str(df.index[-1]).split('.')[0]

    spacing = 6.0 # mm
    L = spacing*len(df_s.T)
    y_max = df_s.max().max()

    x = ((np.array(df_s.index))*spacing)-(L/2.0)+(spacing/2)
    y = df_s.values/n_spills

    x_f, y_f, fwhm, err_sigma, centre, centre_err = gaussian_fit_test(x, y)
    #x_f, y_f = gaussian_fit_test2(x,y)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.errorbar(x,y, yerr=df_d, ls='steps-mid', label='{} spills'.format(n_spills), linewidth=2)
    ax.plot(x_f, y_f, label='Gaussian Fit', linewidth=2)

    ts1 = 'FWHM = {:1.2f}+-{:1.1f} mm\nCentre = {:1.1f} +- {:1.1f} mm'.format(fwhm, err_sigma, centre, centre_err)
    props1 = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.05, 0.95, ts1, transform=ax.transAxes, fontsize=14,
        verticalalignment='top', bbox=props1)

    ts2    = 'Interval =\n{}\n{}'.format(t_start,t_end)
    props2 = dict(boxstyle='round', facecolor='white', alpha=0.5)
    ax.text(0.05, 0.80, ts2, transform=ax.transAxes, fontsize=14,
        verticalalignment='top', bbox=props2)

    ax.grid()
    ax.set_xlabel('x [mm]')
    ax.set_ylabel('y')
    ax.set_title('MWPC Profile\n(file: {})'.format(filename))
    ax.set_ylim(top=y.max()*1.2)
    ax.legend(numpoints=1)

    figname = filename.split('_')[1].split('.')[0]
    filename_figure = '{}{}_2.png'.format(directory, figname)
    fig.savefig(filename_figure)
    plt.close(fig)
    return df

if __name__ == "__main__":
    main()