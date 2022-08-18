import pandas as pd
from scipy import stats as sts
import numpy as np
import time
import math
import pickle
import random
from IPython.core.display import HTML
from sklearn.preprocessing import RobustScaler, MinMaxScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter(action = 'ignore', category = FutureWarning)
    
class Data_Science_Analysis():
    
    def __init__(self):
        self.notebook_settings()
        
    class Flexlist(list):
        
        def __getitem__(self, keys):
            if isinstance(keys, (int, slice)): return list.__getitem__(self, keys)
            return [self[k] for k in keys]
    
    class num_format():
        # because this changes the global state of pandas, we need to use a context manager
        # in order to isolate the changes only to the function that calls it
        # then changes are reverted back to the original state
        # https://stackoverflow.com/questions/41009079/how-to-change-the-global-state-of-pandas-to-format-numbers-in-a-specific-way
        def __init__(self, kind):
            self.kind = kind
            
        def __enter__(self):
            # set the format according to the kind
            if self.kind == "percent":
                pd.options.display.float_format = '{:.2%}'.format
            elif self.kind == "float":
                pd.options.display.float_format = '{:.2f}'.format
            elif self.kind == "int":
                pd.options.display.float_format = '{:.0f}'.format
                
        def __exit__():
            # return to default
            pd.options.display.float_format = '{:}'.format
            
    def notebook_settings():
        eval('%matplotlib inline')
        eval('%pylab inline')
        
        plt.style.use('bmh')
        plt.rcParams['figure.figsize'] = [30, 15]
        plt.rcParams['font.size'] = 24
        
        display(HTML('<style>.container { width:100% !important; }</style>'))
        #pd.options.display.max_columns = None
        #pd.options.display.max_rows = None
        #pd.set_option('display.expand_frame_repr', False)
        sns.set()
    

    def get_column_names(df):
        column_names = pd.Series(df.columns.values)
        columns = pd.DataFrame(column_names)
        columns.columns = ['Columns']
        return columns, column_names

    def get_dimensions(df):
        dimensions_1 = pd.Series(df1.shape[1])
        dimensions_2 = pd.Series(df1.shape[0])
        dimensions = pd.concat([dimensions_1, dimensions_2], axis=1)
        dimensions.columns = ['Columns', 'Rows']
        dimensions = dimensions.T
        dimensions.columns = ['Dimensions'] 
        return dimensions

    def get_dataset_types(df):
        df_types = pd.DataFrame(df.dtypes)
        df_types.reset_index(drop=True, inplace=True)
        df_types.columns = ["Data_Type"]
        df_types["Column"] = pd.Series(df.columns).values
        df_types.set_index("Column", inplace=True)
        #df_types.sort_values(by="Data_Type", ascending=False, inplace=True)
        df_types
        return df_types

    def get_missing_values(df):
        missing_values = pd.DataFrame(df.isna().sum()) #isna, not isnull
        missing_values.reset_index(drop=True, inplace=True)
        missing_values.columns = ["Missing_Values"]
        missing_values["Column"] = pd.Series(df.columns).values
        missing_values.set_index("Column", inplace=True)
        missing_values.sort_values(by="Missing_Values", ascending=False, inplace=True)
        
        return missing_values

    def get_broadview_miss_val(df):
        
        missing_values = pd.DataFrame(df.isna().sum()/df.shape[0])
        missing_values.reset_index(drop=True, inplace=True)
        
        missing_values.columns = ["Absolute Missing (%)"]
        missing_values["Column"] = pd.Series(df.columns).values
        # Make index be the column "Absolute Missing (%)"
        missing_values.reset_index(drop=True, inplace=True)
        missing_values.set_index("Column", inplace=True)
        
        # Calculating the percentage of missing values in relation to the total number of rows in the column
        column_missing = []
        column_total = []
        column_miss = []
        for column in df.columns:
            col_miss = df[column].isnull().sum()
            total_values = df[column].count()
            
            column_miss.append(col_miss)
            column_total.append(total_values) 
            column_missing.append((col_miss/total_values))
        #DataFrame building
        missing_values["Column Missing (%)"] = pd.Series(column_missing).values
        missing_values["Column Remaining (%)"] = -(pd.Series(column_missing).values-1)
        missing_values["Column Total"] = pd.Series(column_total).values
        missing_values["Column Missing"] = pd.Series(column_miss).values
        
        missing_values.sort_values(by="Absolute Missing (%)", ascending=False, inplace=True)
        missing_columns = list(missing_values.query("`Absolute Missing (%)` > 0").index)
        # In Query, Column names with spaces or special chars are required to be inside backticks, 
        # also known as grave accents (shift + <accent key>)
        # Alternative way: missing_columns = missing_values[missing_values["Absolute_Missing_%"] > 0].index.tolist()
        # pure method:
        #self.pandas_num_format(kind = "percent")
        # with context manager:
        
        with num_format(kind = "percent"):
            return missing_values, missing_columns
        
        #return missing_values, missing_columns
    
    # def pandas_num_format(kind):
    #     if kind == "percent":
    #         pd.options.display.float_format = '{:.2%}'.format
    #     elif kind == "float":
    #         pd.options.display.float_format = '{:.2f}'.format
    #     elif kind == "normal":
    #         pd.options.display.float_format = '{:}'.format
    

    def get_num_statistics_metrics(df):
        # Central Tendency - mean, meadina 
        ct1 = pd.DataFrame(df.apply(np.mean)).T
        ct2 = pd.DataFrame(df.apply(np.median)).T
        # Dispersion Metrics - std, min, max, range, skew, kurtosis
        d1 = pd.DataFrame(df.apply(np.std)).T
        d2 = pd.DataFrame(df.apply(min)).T
        d3 = pd.DataFrame(df.apply(max)).T
        d4 = pd.DataFrame(df.apply(lambda x: x.max() - x.min())).T
        d5 = pd.DataFrame(df.apply(lambda x: x.skew())).T
        d6 = pd.DataFrame(df.apply(lambda x: x.kurtosis())).T

        # concatenar
        metrics = pd.concat([d2, d3, d4, ct1, ct2, d1, d5, d6]).T.reset_index()
        metrics.columns = ['Attributes', 'Min', 'Max', 'Range', 'Mean', 'Median', 'Standart Deviation', 'Skew', 'Kurtosis']
        metrics.set_index('Attributes', inplace=True)
        return metrics

    def get_unique_cat_values(df):
        unique_values = pd.DataFrame(df.apply(lambda x: x.unique().shape[0]))
        unique_values.reset_index(drop = True, inplace = True)
        unique_values.columns = ["Unique Values Count"]
        unique_values["Unique Values"] = df.apply(lambda x: x.unique()).values
        unique_values["Attributes"] = pd.Series(df.columns).values
        unique_values.set_index("Attributes", inplace = True)
        
        return unique_values

    def get_analysis_conclusions(matrix, columns = None, columns_included = None):
        if columns:
            columns = columns
        else:
            columns = ['Hipóteses', 'Conclusão', 'Relevância', 'Insigth']
            
        def highlight_relevance(value):
            positive = ['Alta', 'Verdadeira', 'Sim']
            negative = ['Baixa', 'Falsa', 'Não']
            mid = ['Média', 'Possível']
            if value in positive:
                color = 'green'
                return f'color:{color}'
            elif value in negative:
                color = 'red'
                return f'color:{color}'
            elif value in mid:
                color = 'orange'
                return f'color:{color}'
            
        if columns_included:
            analysis = pd.DataFrame.from_records(matrix[1:],columns=matrix[0])
            
        else:
            analysis = pd.DataFrame(conclusions,columns=columns)
        
        analysis.reset_index(drop=True, inplace=True)
        analysis.set_index('Hipóteses', inplace = True)
        return analysis.style.applymap(highlight_relevance)

    def cramer_v(x, y):
        cm = pd.crosstab(x, y).values # Previously, as_matrix was used. but this is deprecated
        n = cm.sum()
        r, k = cm.shape
        
        chi2 = sts.chi2_contingency(cm)[0]
        chi2corr = max(0, chi2 - (k-1)*(r-1)/(n-1))
        
        kcorr = k - (k-1)**2/(n-1)
        rcorr = r - (r-1)**2/(n-1)
        
        return np.sqrt((chi2corr/n) / (min(kcorr-1, rcorr-1)))
    
    def temporal_variable_treatment(temporal_df, target_col, kind):
        if kind == "day":
            temporal_df[target_col + '_sin'] = temporal_df[target_col].apply(lambda x: np.sin(x * (2. * np.pi/30)))
            temporal_df[target_col + '_cos'] = temporal_df[target_col].apply(lambda x: np.cos(x * (2. * np.pi/30)))
            return temporal_df
        elif kind == "month":
            temporal_df[target_col + '_sin'] = temporal_df[target_col].apply(lambda x: np.sin(x * (2. * np.pi/12)))
            temporal_df[target_col + '_cos'] = temporal_df[target_col].apply(lambda x: np.cos(x * (2. * np.pi/12)))
            return temporal_df
        elif kind == "year":
            temporal_df[target_col + '_sin'] = temporal_df[target_col].apply(lambda x: np.sin(x * (2. * np.pi/7)))
            temporal_df[target_col + '_cos'] = temporal_df[target_col].apply(lambda x: np.cos(x * (2. * np.pi/7)))
            return temporal_df
        elif kind == "week":
            temporal_df[target_col + '_sin'] = temporal_df[target_col].apply(lambda x: np.sin(x * (2. * np.pi/52)))
            temporal_df[target_col + '_cos'] = temporal_df[target_col].apply(lambda x: np.cos(x * (2. * np.pi/52)))
            return temporal_df

    def get_feature_engineering_formats(df, index_list):
        rows = []
        columns = []
        if isinstance(df, list):
            for dformat in df:
                rows.append(dformat.shape[0])
                columns.append(dformat.shape[1])
        res = pd.DataFrame({'Linhas': rows, 'Colunas': columns})
        # Define the indexes names
        res.index = [x.capitalize().replace('_', ' ') for x in index_list]
        res.index.name = "Data Frame"
        check_size = "Incompatível"
        #check if all values are equal on the rows column, if so, changing the variable check_size to "Compatible"
        if len(set(res['Linhas'])) == 1:
            check_size = "Compatível"
        res.loc['Formato'] = [check_size, '---']

        return res

    def get_encoded_dataset(df):
        if isinstance(df, list):
            df = pd.concat(df, axis=1)
        return df

    def get_file_size(file_path):
        """
        This function will return the file size and its unit
        """
        if os.path.isfile(file_path):
            num = os.stat(file_path)
            size = num.st_size
            
            for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024.0:
                    return "%3.1f %s" % (size, x)
                size /= 1024.0
        
    def save_dataset(dataset, name = ""):
        directory = '..//..//..//Data//Dataset//'
        path = directory + name + '.csv'
        
        # if dataset already exists, delete it
        if os.path.exists(path):
            os.remove(path)
            print(f'Previous Dataset: {name} deleted!')
            
        #save the new file
        with open(path, "w") as file:
            dataset_final = pd.DataFrame.to_csv(dataset, header=True, index=True, encoding="utf-8")
            file.write(dataset_final)
        size = get_file_size(path)
        
        return(print(   f'Current Dataset: {name} saved successfully!'+'\n'
                        +f'With size: {size}!'))

    def load_dataset(name):
        directory = '..//..//..//Data//Dataset//'
        path = directory + name + '.csv'
        dataset = pd.read_csv(path, index_col = 0)
        print(f'Current Dataset: {name} loaded successfully!')
        return dataset

    def save_model(model, model_name):
        file_name = model_name
        if '.pkl' in model_name:
            model_name.replace('.pkl', '')
        model_name = '..//..//..//Data//Models//' + model_name + '.pkl'
        pickle.dump(model, open(model_name, 'wb'))
        print(f'{file_name} saved successfully!')
        return True

    def load_model(model_name):
        if '.pkl' in model_name:
            model_name.replace('.pkl', '')
        model_name = '..//..//..//Data//Models//' + model_name + '.pkl'
        model = pickle.load(open(model_name, 'rb'))
        return model

    def model_metrics(model_name, y_test, y_pred, y_rescale = None):
        """ 
        This function calculates the mean absolute error, mean absolute percentage error, root mean squared error, 
        and mean percentage error of the predicted values.
        
        Parameters
        ----------
        y_test : array-like of shape (n_samples)
            The real values.
        y_pred : array-like of shape (n_samples)
            The predicted values.
        y_rescale : array-like of shape (n_samples)
            If the passed values need to be rescaled.
        
        Returns
        -------
        mae : float
            The mean absolute error.
        mape : float
            The mean absolute percentage error.
        rmse : float
            The root mean squared error.
        mpe : float
            The mean percentage error.
        rmsee : float
            The root mean squared error of estimation.
        """
        if y_rescale == 'Exponential':
            y_test = np.exp(y_test)
            y_pred = np.exp(y_pred)
            
        def metric_round(metrics_list):
            metric = float(np.round(metrics_list, 4))
            return metric
        
        def mean_percentage_error(y_test, y_pred):
            #remove all rows with zero sales to prevent division by zero
            #real problem when it happens, luckily it doesn't affect the metrics
            y_test = y_test[y_test != 0]
            y_pred = y_pred[y_pred != 0]
            mpe = np.mean((y_test - y_pred)/y_test)
            return mpe
        
        # def root_mean_squared_error_of_estimation(y_test, y_pred):
        #The Root Mean Squared Error of Estimation (RMSEE) is calculated as the root squared distance between 
        # the real Y variable (y_test) - the estimated Y variable (y_pred)
        #This means that its value depends on the original Y variable scale.
        
        #The RMSEcv instead gives you an idea of the standard deviation of the RMSEE. 
        #If the RMSEcv is very different from the RMSEE, it means that every CV model is predicting worse your observation.
        #https://www.researchgate.net/post/What-is-the-acceptable-range-for-root-mean-square-error-of-estimation-
        # RMSEE-and-root-mean-square-error-of-cross-validation-RMSECV
        #    rmsee = np.sqrt(mean_squared_error(y_test - y_pred))
        #   return rmsee
        
        mae = mean_absolute_error(y_test, y_pred)
        mape = mean_absolute_percentage_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mpe = mean_percentage_error(y_test, y_pred)
        #rmsee = root_mean_squared_error_of_estimation(y_test, y_pred)
        
        model_metrics = {'Model Name': model_name, 
                    'MAE': metric_round(mae), 
                    'MAPE': metric_round(mape),
                    'RMSE': metric_round(rmse),
                    'MPE': metric_round(mpe)
                    #'RMSEE': metric_round(rmsee)
                    }
        
        metrics = pd.DataFrame(model_metrics, index=[0])
        
        return metrics

    def crossval_time_series(cross_dataset, kfold, weeks, model_name, target_model, target_cols_xy, verbose = False):
        mae_list = []
        mape_list = []
        rmse_list = []
        mpe_list = []
        #We start the counting from the end of the K fold, then we subtract the round at each loop
        #When the K fold number reachs 1, the looping will do it's last round and there will be no timedelta do run
        #on the validation_end_date, which means that the validation_end_date will be the last date of the dataset itself
        def metric_format(metric_list):
            metric_format = np.round(np.mean(metric_list), 2).astype(str) + ' +/- ' + np.round(np.std(metric_list), 2).astype(str)
            return metric_format
        
        for k in reversed(range(1, kfold+1)):
            if verbose:
                print('KFold Number: {}'.format(k))
            # start and end date for validation 
            validation_start_date = cross_dataset['date'].max() - timedelta(days = k*weeks*7)
            validation_end_date = cross_dataset['date'].max() - timedelta(days = (k-1)*weeks*7)
            # filtering dataset
            training = cross_dataset[cross_dataset['date'] < validation_start_date]
            validation = cross_dataset[(cross_dataset['date'] >= validation_start_date) & (cross_dataset['date'] <= validation_end_date)]
            # training and validation datasets
            # training
            x_train = training.drop(target_cols_xy[0], axis=1) 
            y_train = training[target_cols_xy[1]]
            # validation
            x_test = validation.drop(target_cols_xy[0], axis=1)
            y_test = validation[target_cols_xy[1][0]] 
            #to calc metrics we can use it as a Series
            #later: series -> np.array -> float
            # target_model
            model = target_model.fit(x_train, y_train)
            # prediction
            y_pred = model.predict(x_test)
            # performance
            model_result = model_metrics(model_name, y_test, y_pred, 'Exponential')
            # store performance of each kfold iteration
            mae_list.append(model_result['MAE'].values)
            mape_list.append(model_result['MAPE'].values)
            rmse_list.append(model_result['RMSE'].values)
            mpe_list.append(model_result['MPE'].values) #previously float(model_result['MPE'].values)
            
        cross_val_results = {'Model Name': model_name,
                            'MAE CV': metric_format(mae_list),
                            'MAPE CV': metric_format(mape_list),
                            'RMSE CV': metric_format(rmse_list),#
                            'MPE CV': metric_format(mpe_list)}#
        cross_val = pd.DataFrame(cross_val_results, index=[0])
        
        return cross_val

    def execution_time(start = False, end = False, start_time = None):
        if start:
            start_cycle = time.time()
            return start
        elif end:
            end_cycle = time.time()
            current_cycle = round(end_cycle - start_time, 2)
            estimated = timedelta(seconds = (current_cycle*(cycles-1)))
            current_cycle = timedelta(seconds = (current_cycle))
            estimated = str(estimated).split('.')[0]
            current_cycle = str(current_cycle).split('.')[0]
            
            print(f'Current Cycle: {current_cycle}' + '\n'
                + f'Estimated Time: {estimated} minutes'+ '\n')
            
    def random_search_tms(cycles, cross_dataset, kfold, weeks, model_name, target_cols_xy, param, verbose = False):
        final_result = pd.DataFrame()
        param_selected_df = pd.DataFrame()
        param_selected = {}
        
        for i in range(cycles):
            start = execution_time(start = True)
            #print(f'Cycle {reversed(range(1, cycles+1))}')
            # choose values for parameters randomly
            hyper_param = {k: np.random.choice(v, 1)[0] for k, v in param.items()}
            #manualy insert the key:value pair "objective":'reg:squarederror'
            hyper_param['objective'] = 'reg:squarederror'
            #unpack hyper_param inside xgbr_model_tuned
            xgbr_model_tuned = XGBRegressor(**hyper_param)
            # model
            # always drop the key:value pair "objective":'reg:squarederror' from hyper_param
            del hyper_param['objective']
            # performance
            result = crossval_time_series(cross_dataset, kfold, weeks, model_name, xgbr_model_tuned, target_cols_xy, verbose = verbose)
            param_selected.update(hyper_param)
            param_selected_df = pd.concat([param_selected_df, param_selected_df.from_dict([param_selected])])
            final_result = pd.concat([final_result, result])
            execution_time(end = True, start_time = start)
        final_result = pd.concat([final_result, param_selected_df], axis=1)
        final_result.index.name='Cycle'
            
        return final_result

    def list_indexer(list_data):
        list_indexer = pd.DataFrame()
        for item in enumerate(viz_cols):
            #put every item in the list into the dataframe as two columns
            list_indexer = list_indexer.append(pd.DataFrame({'Number': [item[0]], 'Column_name': [item[1]]}))
        list_indexer.set_index('Number', inplace=True)
        return list_indexer