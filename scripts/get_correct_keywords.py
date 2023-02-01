# -*- coding: utf-8 -*-
"""
=====================================
Created on Tue Jan 10 2023 09:39
@author: Martin Rerabek, martin.rerabek@zhaw.ch
Copyright © 2023, Predictive Analytics Group, ICLS, ZHAW. All rights reserved.
=====================================

"""
# import modules
import pandas as pd
import numpy as np


def process_dev_keywords(keywords_file_ID):
    input_file = '../../keywords/data/sdgs/old/SDG{ID}_dev.csv'.format(ID=keywords_file_ID)
    print(input_file)

    # read csv as dataframe
    temp = pd.read_csv(input_file, sep=';', header=None)
    temp = temp.replace('\xa0', ' ', regex=True)
    temp = temp.replace('\*', '', regex=True)
    # temp = temp.replace('\?', 'z', regex=True)
    temp = temp.replace('xx+', '', regex=True)
    temp = temp.fillna('')
    temp = temp.apply(lambda x: x.str.strip())
    temp = temp.replace("NA", '')


    # add header and create unified df with default shape (number of columns=13)
    COLUMNS = ['id', \
               'keyword_en', 'required_context_en', 'forbidden_context_en', \
               'keyword_de', 'required_context_de', 'forbidden_context_de', \
               'keyword_fr', 'required_context_fr', 'forbidden_context_fr', \
               'keyword_it', 'required_context_it', 'forbidden_context_it'
               ]
    sdg_df = pd.DataFrame(columns=COLUMNS)
    for col in temp:
        sdg_df.iloc[:, col] = temp[col]
    sdg_df = sdg_df.fillna('')

    # check for NOT, NICHT, PAS, NON and move those in next columns with header MUST-NOT include)
    for col in sdg_df:
        sdg_col_index = sdg_df.columns.get_loc(col)
        if sdg_col_index < sdg_df.shape[1]-1:
            # check each item in affected columns and move the item to MNI
            for boll_word in ['NOT ', 'NICHT', 'PAS ', 'NON ']:
                for ind, item in enumerate(sdg_df[col].str.contains(boll_word)):
                    if item:
                        # read actual MUST_NOT_include
                        MI = sdg_df.iloc[ind, sdg_col_index]
                        MNI = sdg_df.iloc[ind, sdg_col_index+1]

                        MNI_new = MI.replace(boll_word, '')
                        MI_new = ''

                        sdg_df.iloc[ind, sdg_col_index] = MI_new
                        sdg_df.iloc[ind, sdg_col_index+1] = MNI_new

    # sdg_df.drop(columns='construct', inplace=True)
    sdg_df = sdg_df.apply(lambda x: x.str.strip())
    sdg_df = sdg_df.apply(lambda x: x.str.replace(",",", "))
    sdg_df = sdg_df.fillna('')

    sdg_df['id'] = sdg_df.index.astype(int)+1
    sdg_df['id'] = 'c' + sdg_df['id'].astype(str)
    return sdg_df


def main():
    for ID in np.arange(1,17): # for all SGDs
        # print(ID)
        new_sgd_df = process_dev_keywords(ID)
        output_file = '../../keywords/data/sdgs/SDG{ID}.csv'.format(ID=ID)
        new_sgd_df.to_csv(output_file, sep=';', index=False)



if __name__ == "__main__":
    """
    getting SDG indexes for database entry and filling sdg records
    """
    main()
