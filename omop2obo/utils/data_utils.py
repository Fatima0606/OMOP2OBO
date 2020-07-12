#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Data PreProcessing Utility Functions.

Pandas DataFrame manipulations
* data_frame_subsetter
* data_frame_supersetter
* column_splitter
* aggregates_column_values

Dictionary manipulations
* merge_dictionaries

"""

# import needed libraries
import pandas as pd  # type: ignore

from functools import reduce
from more_itertools import unique_everseen
from typing import Callable, Dict, List  # type: ignore

# ENVIRONMENT WARNINGS
# WARNING 1 - Pandas: disable chained assignment warning rationale:
# https://stackoverflow.com/questions/20625582/how-to-deal-with-settingwithcopywarning-in-pandas
pd.options.mode.chained_assignment = None


def data_frame_subsetter(data: pd.DataFrame, primary_key: str, subset_columns: List) -> pd.DataFrame:
    """Takes a Pandas DataFrame and subsets it such that each subset represents an original column of codes, OMOP
    concept identifiers, and a string containing the code's column name in the original DataFrame. An example of
    the input and generated output is shown below.

        INPUT:
              CONCEPT_ID CONCEPT_SOURCE_CODE  UMLS_CUI   UMLS_CODE        UMLS_SEM_TYPE
            0    4331309            22653005  C0729608    22653005  Disease or Syndrome
            1    4331310            22653011  C4075981    22653005  Disease or Syndrome

        OUTPUT:
              CONCEPT_ID                CODE          CODE_COLUMN
            0    4331309            22653005  CONCEPT_SOURCE_CODE
            1    4331309            C0729608             UMLS_CUI
            2   37018594            22653005            UMLS_CODE

    Args:
        data: A Pandas DataFrame containing several columns of clinical codes (see INPUT for an example).
        primary_key: A string containing a column to be used as a primary key.
        subset_columns: A list of columns to subset Pandas DataFrame on.

    Returns:
        subset_data_frames: A Pandas DataFrame containing stacked subsets of the original DataFrame.
    """

    # subset data
    subset_data_frames = []

    for col in subset_columns:
        subset = data[[primary_key, col]]
        subset.loc[:, 'CODE_COLUMN'] = [col] * len(subset)
        subset.columns = [primary_key, 'CODE', 'CODE_COLUMN']
        subset_data_frames.append(subset)

    # convert list to single concatenated Pandas DataFrame
    subset_data = pd.concat(subset_data_frames)

    return subset_data.drop_duplicates()


def data_frame_supersetter(data: pd.DataFrame, index: str, columns: str, values: str) -> pd.DataFrame:
    """Takes a stacked Pandas DataFrame and unstacks it according to row values specified in the index column.
    This is equivalent to converting a DataFrame in long format to wide format. An example of the input and
    generated output is shown below.

        INPUT:
              CONCEPT_ID                CODE          CODE_COLUMN
            0    4331309            22653005  CONCEPT_SOURCE_CODE
            1    4331309            C0729608             UMLS_CUI
            2   37018594            22653005            UMLS_CODE

        OUTPUT:
                 CONCEPT_ID CONCEPT_SOURCE_CODE  UMLS_CUI   UMLS_CODE
            0    4331309            22653005  C0729608    22653005
            1    4331310            22653011  C4075981    22653005

    Args:
        data: A Pandas DataFrame containing several columns of clinical codes (see INPUT for an example).
        index: A string containing a column to be used as a primary key.
        columns: A list of columns to unstack from row values into columns.
        values: A list of columns whose values will be used to populate the unstacked DataFrame.

    Returns:
        superset_data_frame: An unstacked version of the input DataFrame (see OUTPUT above for an example).
    """

    # unstack the DataFrame
    superset_data_frame = data.drop_duplicates().pivot(index=index, columns=columns, values=values)

    # reset index
    superset_data_frame.reset_index(level=0, inplace=True)
    superset_data_frame.columns.name = None

    return superset_data_frame.drop_duplicates()


def column_splitter(data: pd.DataFrame, delimited_columns: List, delimiter: str) -> pd.DataFrame:
    """Takes a Pandas DataFrame and a list of strings specifying columns in the DataFrame that may contain a delimiter
    and expands the delimited strings within each column into separate rows. The expanded data are then merged with the
    original data.

    Args:
        data: A stacked Pandas DataFrame containing output from the umls_cui_annotator method.
        delimited_columns: A list of the column names which contain delimited data.
        delimiter: A string specifying the delimiter type.

    Returns:
        merged_split_data: A Pandas DataFrame containing the expanded data.
    """

    delimited_data = []
    key = [x for x in list(data.columns) if x not in delimited_columns][0]

    for col in delimited_columns:
        subset_data = data[[key, col]]

        # expand delimited column
        split_data = subset_data[col].str.split(delimiter).apply(pd.Series, 1).stack()
        split_data.index = split_data.index.droplevel(-1)
        split_data.name = col

        # drop original delimited column and merge expanded data
        subset_data.drop(columns=[col], inplace=True)
        merged_split_data = subset_data.join(split_data)

        # clean up leading and trailing white space
        merged_split_data[col] = merged_split_data[col].apply(lambda x: x.strip())
        delimited_data.append(merged_split_data.drop_duplicates())

    # merge delimited data
    merged_delimited_data = reduce(lambda x, y: pd.merge(x, y, on=key), delimited_data)

    return merged_delimited_data.drop_duplicates()


def aggregates_column_values(data: pd.DataFrame, primary_key: str, agg_cols: List, delimiter: str) -> pd.DataFrame:
    """Takes a Pandas DataFrame, a string containing a primary key, a list of columns to aggregate, and a string
    delimiter to use when aggregating the columns. The method then loops over each column in agg_cols and performs
    the aggregation. The method joins all aggregated columns and merges it into a single Pandas DataFrame.

    Args:
        data: A Pandas DataFrame.
        primary_key: A string containing a column name to be used as a primary key.
        agg_cols: A list of columns to aggregate.
        delimiter: A string containing a delimiter to aggregate results by.

    Returns:
        merged_combo: A Pandas DataFrame that includes the primary_key column and one
            delimiter-aggregated column for each column in the agg_cols list.
    """

    # create list of aggregated GroupBy DataFrames
    combo = [data.groupby([primary_key])[col].apply(lambda x: delimiter.join(list(unique_everseen(x))))
             for col in agg_cols]

    # merge data frames by primary key and reset index
    merged_combo = reduce(lambda x, y: pd.merge(x, y, on=primary_key, how='outer'), combo)
    merged_combo.reset_index(level=0, inplace=True)

    return merged_combo


def data_frame_grouper(data: pd.DataFrame, primary_key: str, type_column: str, col_agg: Callable) -> \
        pd.DataFrame:
    """Methods takes a Pandas DataFrame as input, a primary key, and a column to group the data by and
    creates a new DataFrame that merges the individual grouped DataFrames into a single DataFrame.
    Examples of the input and output data are shown below.

    INPUT_DATA:
                   CONCEPT_ID         CONCEPT_DBXREF_ONT_URI  CONCEPT_DBXREF_ONT_TYPE         CONCEPT_DBXREF_EVIDENCE
            0         442264        http://...MONDO_0100010                     MONDO   CONCEPT_DBXREF_sctid:68172002
            2        4029098        http://...MONDO_0045014                     MONDO  CONCEPT_DBXREF_sctid:237913008
            4        4141365           http://...HP_0000964                        HP  CONCEPT_DBXREF_sctid:426768001

    OUTPUT DATA:
    Columns: ['CONCEPT_ID', 'HP_CONCEPT_DBXREF_ONT_URI', 'HP_CONCEPT_DBXREF_ONT_LABEL', 'HP_CONCEPT_DBXREF_EVIDENCE',
              'MONDO_CONCEPT_DBXREF_ONT_URI', 'MONDO_CONCEPT_DBXREF_ONT_LABEL', 'MONDO_CONCEPT_DBXREF_EVIDENCE']

    Args:
        data: A Pandas DataFrame containing data with columns that can be grouped (see INPUT above for ex).
        primary_key: A string containing the name of the column in the input DataFrame to use as a
            primary key.
        type_column: A string containing the name of the column in the input DataFrame to use for
            grouping the data (see OUTPUT above for an example).
        col_agg: A func that aggregates data within a Pandas DataFrame column.

    Returns:
        grouped_data_full: A Pandas DataFrame containing a merged version of the grouped data.
    """

    # group data by ontology type
    grouped_data = data.groupby(type_column)
    grouped_data_frames = []

    for grp in grouped_data.groups:
        temp_df = grouped_data.get_group(grp)
        temp_df.drop(type_column, axis=1, inplace=True)
        # rename columns
        updated_names = [x.replace('ONT', grp) for x in list(temp_df.columns) if x != primary_key]
        temp_df.columns = [primary_key] + updated_names
        # aggregate data
        agg_cols = [col for col in temp_df.columns if col.split('_')[-1] in ['LABEL', 'EVIDENCE', 'URI']]
        temp_df_agg = col_agg(temp_df.copy(), primary_key, agg_cols, ' | ')

        grouped_data_frames.append(temp_df_agg.drop_duplicates())

    # merge DataFrames back together
    grouped_data_full = reduce(lambda x, y: pd.merge(x, y, how='outer', on=primary_key), grouped_data_frames)

    return grouped_data_full.drop_duplicates()


def merge_dictionaries(dictionaries: Dict, key_type: str, reverse: bool = False) -> Dict:
    """Given any number of dictionaries, shallow copy and merge into a new dict, precedence goes to key value pairs
    in latter dictionaries.

    Function from StackOverFlow Post:
        https://stackoverflow.com/questions/38987/how-do-i-merge-two-dictionaries-in-a-single-expression-in-python

    Args:
        dictionaries: A nested dictionary.
        key_type: A string containing the key of one of the inner dictionaries.
        reverse: A bool indicating whether or not the dictionaries should be reversed before merging (default=False).

    Returns:
        combined_dictionary: A dictionary object containing.
    """

    combined_dictionary: Dict = {}

    for dictionary in dictionaries.keys():
        if reverse:
            combined_dictionary.update({v: k for k, v in dictionaries[dictionary][key_type].items()})
        else:
            combined_dictionary.update(dictionaries[dictionary][key_type])

    return combined_dictionary
