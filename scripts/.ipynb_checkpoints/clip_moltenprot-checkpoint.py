"""
Clip Moltenprot data.

Author: Serena G. Lotreck
"""
import argpase
from os.path import abspath
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def close_factors(number):
    ''' 
    find the closest pair of factors for a given number

    from: https://stackoverflow.com/questions/67051401/how-to-automatically-set-number-of-rows-columns-subplots
    '''
    factor1 = 0
    factor2 = number
    while factor1 +1 <= factor2:
        factor1 += 1
        if number % factor1 == 0:
            factor2 = number // factor1
        
    return factor1, factor2


def almost_factors(number):
    '''
    find a pair of factors that are close enough for a number that is close enough

    from: https://stackoverflow.com/questions/67051401/how-to-automatically-set-number-of-rows-columns-subplots
    '''
    while True:
        factor1, factor2 = close_factors(number)
        if 1/2 * factor1 <= factor2: # the fraction in this line can be adjusted to change the threshold aspect ratio
            break
        number += 1
    return factor1, factor2


def before_plot(moltenprot_dfs, outloc, outprefix):
    """
    Plot the ratio and its first derivative and save.
    """
    ratio_df = moltenprot_dfs['Ratio']
    ratio_1st_der = moltenprot_dfs['Ratio (1st deriv.)']
    
    num_species = ratio_df.shape[1] - 1
    rows, cols = almost_factors(num_species)
    
    fig, axs = plt.subplots(rows, cols, sharex=True, sharey=True, figsize=(5*rows, 10*cols))
    
    for col, colder, ax in zip(ratio_df.columns.tolist()[1:], ratio_1st_der.columns.tolist()[1:], axs.flat):
    
        ax.set_title(col[1])
        ax.scatter(ratio_1st_der.index, ratio_1st_der[colder], c=ratio_1st_der[colder] > 0, label='First derivative')
        ax1 = ax.twinx()
        ax1.scatter(ratio_df.index, ratio_df[col], color='blue', label='Ratio')

    plt.savefig(f'{outloc}/{outprefix}_raw_data_before.png', format='png', dpi=300, bbox_inches='tight')

    print(f'Saved before plot to: {outloc}/{outprefix}_raw_data_before.png')


def cut_curve_w_deviation(index, curve, first_der):
    """
    Remove the remainder of the curve after the second positive transition of the first derivative, plus
    any sections that go more than 0.025 above/below the last positive value.

    parameters:
        index, list: points on the x axis
        curve, list: points in the curve
        first_der, list: points in the first derivative

    returns:
        index_cut, list: index, cut at the second positive transition
        curve_cut, list: curve, cut at the second positive transition
        first_der_cut, list: first_der, cut at the second positive transition
    """
    start_is = '+'
    num_sign_trans_allow = 2
    num_sign_trans_done = 0
    for i, point in enumerate(first_der):
        # Allow curves to start with negative first derivatives
        if i == 0:
            if point < 0:
                start_is = '-'
                num_sign_trans_allow = 3
        # Start looking for sign transitions
        try:
            if point*first_der[i+1] < 0: # Means next point transitions
                num_sign_trans_done += 1
                if num_sign_trans_done == num_sign_trans_allow:
                    cut_point = i
                    break
            else: # Check for the deviations
                if num_sign_trans_allow - num_sign_trans_done == 1: 
                    if abs(0 - point) > 0.002:
                        cut_point = i
                        break
        except IndexError: # Means it doesn't need to be cut
            cut_point = i - 1
    return index[:cut_point + 1], curve[:cut_point + 1], first_der[:cut_point + 1]


def clip_and_plot():
    """
    Clip curves and plot results, 
    """
    ratio_df = moltenprot_dfs['Ratio']
    ratio_1st_der = moltenprot_dfs['Ratio (1st deriv.)']
    
    num_species = ratio_df.shape[1] - 1
    rows, cols = almost_factors(num_species)
    
    fig, axs = plt.subplots(rows, cols, sharex=True, sharey=True, figsize=(5*rows, 10*cols))
    
    for col, colder, ax in zip(ratio_df.columns.tolist()[1:], ratio_1st_der.columns.tolist()[1:], axs.flat):
    
        ax.set_title(col[1])
        index_cut, curve_cut, first_der_cut = cut_curve_w_deviation(ratio_1st_der.index.tolist(), ratio_df[col].tolist(), ratio_1st_der[colder].tolist())
        ## TODO add code to adjust the columns in the df (replace cut data with nan)
        ax.scatter(index_cut, first_der_cut, c=np.array(first_der_cut) > 0, label='First derivative')
        ax1 = ax.twinx()
        ax1.scatter(index_cut, curve_cut, color='blue', label='Ratio')

    
def main(prometheus_xlsx, outloc, outprefix):

    # Read in data
    print('\nReading in data...')
    moltenprot_dfs = pd.read_excel(prometheus_xlsx, sheet_name=None, header=[0, 1, 2], index_col=0)

    # Make and save before plot
    print('\nMaking a plot of the data before manipulation...')
    before_plot(moltenprot_dfs, outloc, outprefix)

    # Clip the data
    print('\nClipping data...')
    clip_and_plot()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Clip moltenprot data')

    parser.add_argument('prometheus_xlsx', type=str,
                       help='Path to the Excel file from the Prometheus. Must contain '
                       'two sheets at least; "Ratio" and "Ratio (1st deriv.)"')
    parser.add_argument('outloc', type=str,
                       help='Path to dir to save outputs')
    parser.add_argument('outprefix', type=str,
                       help='String to prepend to output filenames')

    args = parser.parse_args()

    args.prometheus_xlsx = abspath(args.prometheus_xlsx)
    args.outloc = abspath(args.outloc)

    main(args.prometheus_xlsx, args.outloc, args.outprefix)