import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
import datetime as dt

from statsmodels.stats.multitest import fdrcorrection
from pylab import savefig


# FUNCTIONS YOU CAN USE:
#     analyses(filepath) spits out a nifty heatmap to let you check correlation between variables
#
#     regress(option, df) churns out a saucy graph of the linear regression for the variables you provided, where
#       option is 'snr_total' or 'tsnr', whichever you want to make the dependent variable of your model
#       df is the pandas DataFrame containing your data. To modify which variables you want in your model, you'll
#             have to directly modify the regress function



# NOTABLE FILENAMES
# ../data/extractions/p2_BOLD.csv                  - all dates for p2_BOLD
# ../data/extractions/p2Xs4X35mm_BOLD.csv          - all dates for p2Xs4X35mm_BOLD
# ../data/extractions/anat.csv                     - all possible dates for anatomical data



def filter(option, df):
    is_p2 = df['Filetype'] == "task-rest_acq-p2_bold.json"
    is_x = df['Filetype'] == "task-rest_acq-p2Xs4X35mm_bold.json"
    
    if option == 'x':
        return df[is_x]
    elif option == 'p2':
        return df[is_p2]


def analyses(filepath):
    files = pd.read_csv(filepath)
    
    # FIRST CHECK: CONVERSION SOFTWARE VERSIONS
    check = files.iloc[0, 7]
    valid = True
    
    for i in files.index:
        if check != files.iloc[i, 7]:
            valid = False
            
    print("All Conversion Softwares are the same: " + str(valid))
    
    # SECOND CHECK: HEATMAP
    figure = sns.heatmap(files.corr(), cmap=sns.diverging_palette(h_neg=240, h_pos=10, n=9, sep=1, center="dark"), center=0)
    figure
    
    save = figure.get_figure()    
    save.savefig('heatmap.svg', pad_inches = 0.1)



def add_seasonal_simple(df, col='Date', start='2017-01-01'):
    # Add a very simplistic seasonal regressors as cos and sin since some date in a year
    time_delta = df[col] - np.datetime64(start)
    time_delta_rad = time_delta.apply(lambda d: d.days) * 2 * np.pi / 365.25
    df['Seasonal (sin)'] = np.sin(time_delta_rad)
    df['Seasonal (cos)'] = np.cos(time_delta_rad)


def Ftest(model, var_prefix, queue, prints=False):
    var_columns = [c for c in model.params.index if c.startswith(var_prefix)]
    
    if var_columns:
        f_test = model.f_test(' = '.join(var_columns) + " = 0")
        
        if f_test.pvalue < 0.05:
            if var_prefix == "Shim":
                for i in range(8):
                    queue.append("Shim" + str(i+1))
            elif var_prefix == "IOPD":
                for i in range(6):
                    queue.append("IOPD" + str(i+1))
                    
        if prints:
            print("%s F-test: %s" % (var_prefix, f_test))
        return f_test
    
    else:
        if prints:
            print("No %s variables in the model" % var_prefix)
        return None


# copy pasted from nipy function, renamed from _orthogonalize
def orthogonalize(X):
    """ Orthogonalize every column of design `X` w.r.t preceding columns
    Parameters
    ----------
    X: array of shape(n, p), the data to be orthogonalized
    Returns
    -------
    X: after orthogonalization
    Notes
    -----
    X is changed in place. the columns are not normalized
    """
    if X.size == X.shape[0]:
        return X
    for i in range(1, X.shape[1]):
        X[:, i] -= np.dot(X[:, i], np.dot(X[:, :i], np.linalg.pinv(X[:, :i])))
    return X


def regress(target_variable, model_df, plot=True, print_summary=True, add_qa=True, add_seasonal=True, real_data=False):
    """
    creates a regression graph plotted against actual data from certain QA metrics

    Parameters
    ----------
       target_variable: takes str value of either snr_total or tsnr to model against
       model_df       : takes pandas DataFrame with data to be used for predictive modeling
       plot           : boolean to turn the plotted graph on/off
       print_summary  : boolean to turn the printed summary of OLS regression on/off
       add_qa         : boolean to add/not add snr_total_qa into list of variables to be modeled
       add_seasonal   : boolean to add/not add seasonal variables into list of variables to be modeled
       real_data      : boolean to indicate whether or not the pandas DataFrame being fed in is from real data or not
    """
    
    if type(model_df) is not pd.core.frame.DataFrame:
        return "DataFrame must be of type pandas.core.frame.DataFrame"
    
    
    ########## adding seasonal curves to the model
    add_seasonal_simple(model_df)
    
    
    ########## Converting date to a format that can be parsed by statsmodels API
    model_df = model_df.copy()
    date_df = model_df['Date']
    model_df['Date'] = pd.to_datetime(model_df['Date'], format="%Y%m%d")
    model_df['Date'] = model_df['Date'].map(lambda x: x.toordinal())
    
    f_tests_todo = ['IOPD']
    excluded_cols = ['Date', 'IOPD1', 'IOPD2', 'IOPD3', 'IOPD4', 'IOPD5', 'IOPD6', 'Seasonal (sin)', 'Seasonal (cos)']
    seasonal_cols = ['Seasonal (sin)', 'Seasonal (cos)',]

    cols = ['Date']
    if not real_data:
        # preparing model_df for orthogonalization
        cols += ['AcquisitionTime', 'SAR', 'TxRefAmp',
                'IOPD1', 'IOPD2', 'IOPD3', 'IOPD4', 'IOPD5', 'IOPD6']
        if add_seasonal:
            cols += seasonal_cols
    else:
        cols += ['age', 'sex_male', 'PatientWeight',]
        if add_seasonal:
            cols += seasonal_cols
        if add_qa:
            cols += ['snr_total_qa']
        cols += ['IOPD1_real', 'IOPD2_real', 'IOPD3_real', 'IOPD4_real', 'IOPD5_real', 'IOPD6_real']

    if add_seasonal:
        f_tests_todo += ['Seasonal']
               
    cols.append(target_variable)
    
    model_df = model_df[cols]
   
    # There is apparently a sample date (20170626) with SAR being unknown None/NaN
    # For now we will just filter out those samples
    if 'SAR' in model_df.columns:
        finite_SAR = np.isfinite(model_df['SAR'])
        if not np.all(finite_SAR):
            print("Following dates didn't have SAR, excluding them: %s" % str(model_df['Date'][~finite_SAR]))
            model_df = model_df[finite_SAR]
    

    orthogonalized_df = model_df.drop(target_variable, axis=1)  # avoid orthogonalizing target variable
    cols = cols[:-1] # remove target variable from column list
    
    # orthogonalize dataframe after its conversion to NumPy array, then convert back and replace in original model_df
    model_array = orthogonalize(orthogonalized_df.to_numpy())
    orthogonalized_df = pd.DataFrame(model_array)
    orthogonalized_df.columns = [cols]
    orthogonalized_df[target_variable] = pd.Series(model_df[target_variable])
    model_df = orthogonalized_df
    
    # add datetime64[ns] formatted date time
    model_df.columns=[x[0] for x in model_df.columns]
    model_df['Date'] = pd.to_datetime(model_df['Date'])
    model_df = model_df.drop('Date', axis=1) 
    model_df['Date'] = date_df
    
    
    ########## Assigning independent and dependent variables
    model_vars = []
    
    for item in model_df.std().iteritems():
        if item[0] != 'Date' and item[0] != target_variable:
            model_vars.append(item[0])

    X = model_df[model_vars]
    y = model_df[target_variable]
    X = X.sub(X.mean())
    X = sm.add_constant(X)
    
    model_df = sm.add_constant(model_df)
    
    
    ########## modeling predictions
    model = sm.OLS(y, X).fit()
    predictions = model.predict(X)
    
    ################ CODE FOR TESTING INDIVIDUAL VARIABLE EFFECTS ####################
    significant_variables = []
    F_tests_pvals = {
       v: float(Ftest(model, v, significant_variables).pvalue)
       for v in f_tests_todo
    }
    
    # get p-values
    for key, value in dict(model.pvalues).items():
        if key not in significant_variables and value < 0.05 or key.lower() == 'const':
            # identify statistically insignificant variables in df
            significant_variables.append(key)
    
    
    ######## set statistically insignificant variables to 0, then predict
        
    partial_fits = {}  # partial_fits = {}

    for variable in significant_variables:

        X2 = X.copy(True) # prepare for mods

        for col in X2:
            if col != variable:
                X2[col] = 0
        
        partial_fits[str(variable)] = model.predict(X2)
     
    if print_summary:
        print("Statistically significant variables: " + str(significant_variables))
    
    ################ END CODE FOR TESTING INDIVIDUAL VARIABLE EFFECTS ####################
    
    # Functionality for carrying out FDR correction
    outvars = {} # dict containing all predictive variables and their p values from the model
    
    for var in cols:
        is_f_test = False
        
        for f_test in f_tests_todo:
           if var.startswith(f_test):
              is_f_test = True
              break
            
        if is_f_test:
           continue
        
        if var not in excluded_cols:
            var_pvalue = getattr(model.pvalues, var)
            outvars[var] = var_pvalue
   
    outvars.update(F_tests_pvals) # add previously conducted F test p values to the outvars

    FDR_tuple = fdrcorrection(list(outvars.values())) # actual FDR test conduct
    t_f = list(FDR_tuple[0]) # split tuple into true/false array
    FDR_pvals = list(FDR_tuple[1]) # split tuple into p value array
    
    print("FDR-corrected p-values:")
    for (var, value), fdr_pval, is_sign in zip(outvars.items(), FDR_pvals, t_f):
        print("%15s | Original  p-value: %8.3g" % (var, value) +
              " | FDR-corrected p-value: %8.3g%s" % (fdr_pval, '**' if is_sign else ''))
    print("\n")

    # giving additional data
    if print_summary:
        print(model.summary())
        print("AIC: " + str(model.aic))
        print("BIC: " + str(model.bic))
    
    if not plot:
        return model
    
    
    ######### converting the above predictions to a format that can be plotted
    
    plot_df = predictions.to_frame()       # new DataFrame containing only data needed for the plot
    plot_df.columns = ['full fit']
    plot_df = plot_df.join(model_df['Date'])
    plot_df = plot_df.join(model_df[target_variable])
    
    summation_df = None
    
    for key, value in partial_fits.items():
        column = value.to_frame()
        column.columns = ['partial fit']

        if summation_df is None:
            summation_df = column          # used to add up the values
        else:
            summation_df = summation_df.add(column, axis=1)
    
    plot_df = pd.concat([plot_df, summation_df], axis=1)
    
    # plotting the graph
    plt.figure(figsize=(15, 6))

    ax = sns.lineplot(x="Date", y=target_variable, data=plot_df, color="#000000")
    
    # plotting partial fit
    ax_partial = plt.twinx()
    sns.lineplot(x="Date", y="full fit", data=plot_df, color="r", ax=ax)
    if partial_fits:
        sns.lineplot(x="Date", y="partial fit", data=plot_df, color="#ffcccc", ax=ax_partial)
        plt.ylim(145, 305)
        ax_partial.legend(['partial fit'])
    
    ax.legend(['actual', 'full fit'], loc='upper left')
    plt.savefig("test.svg")
    
    return model


def scrape_var_significance(targets, p_var, df):
    dummy = [] # dud list for Seasonal f test comparison
    columns = ['Variable', p_var + ' p value', 'R2 value']
    result = pd.DataFrame(columns = columns)
    raw_pvals = []
    
    for target in targets:
        input_df = pd.DataFrame(df,columns=['Date', 'sid', 'ses', target, 'age', 'tsnr',
                                             'snr_total_qa', 'IOPD1_real', 'IOPD2_real', 'IOPD3_real', 
                                             'IOPD4_real', 'IOPD5_real', 'IOPD6_real', 'sex_male', 'PatientWeight'])
        model = regress(target, input_df, plot=False, print_summary=False, real_data=True)
        
        if p_var == 'Seasonal':
            seasonal_ftest = Ftest(model, 'Seasonal', dummy).pvalue
            result.loc[len(result)] = [target, seasonal_ftest, model.rsquared]
            raw_pvals.append(seasonal_ftest)
            
        else:
            var_pval = model.pvalues[p_var]
            result.loc[len(result)] = [target, var_pval, model.rsquared]
            raw_pvals.append(var_pval)
            
    fdr_df = pd.DataFrame({'FDR-corrected': fdrcorrection(raw_pvals)[1].tolist()})
    result = result.join(fdr_df)
        
    return result
