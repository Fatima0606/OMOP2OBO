#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Analytic Utility Functions.

Data Manipulation
* reconfigures_dataframe

"""

# import needed libraries
import numpy as np  # type: ignore
import pandas as pd  # type: ignore

from typing import List


def reconfigures_dataframe(split_list: List, data_frame: pd.DataFrame) -> pd.DataFrame:
    """Takes a Pandas DataFrame and a list of strings representing important categories and reconfigures the DataFrame
    such that all it's stacked by category-specific data and a new column is added to represent which rows belong to
    each category. An example of the expected input and output data are shown below.

    INPUT DATA:
       CONCEPT_ID              CONCEPT_LABEL      HP_URI      MONDO_URI
            22288  Hereditary elliptocytosis  HP_0004445  MONDO_0008165

    OUTPUT DATA:
           CONCEPT_ID          CONCEPT_LABEL      CATEGORY  CATEGORY_URI
            22288  Hereditary elliptocytosis           HP     HP_0004445
            22288  Hereditary elliptocytosis        MONDO  MONDO_0008165

    Args:
        split_list: A list of string, where each string represents an ontology (e.g. ['HP, 'MONDO']).
        data_frame: A pandas data frame containing data. It is assumed that there will be columns in the data frame
            that correspond to at least one of the categories in split_list.

    Returns:
        reconfigured_data: A Pandas DataFrame that has been reconfigured such that the data are stacked by
            category-specific data and a new column is added to represent which rows belong to each category.
    """

    # get non-ontology columns
    non_category_columns = [x for x in data_frame.columns if not any(i for i in split_list if i.lower() in x.lower())]

    # make sure that all blank variables are converted to NaN
    data_frame = data_frame.replace(r'^\s*$', np.nan, regex=True)

    # identify which columns belong to each of the input ontologies
    category_split_data = []
    for x in split_list:
        # get category-specific columns
        cat_columns = [i for i in data_frame.columns if x.lower() in i.lower()]
        # subset original data to include non-category and specific single category data
        cat_data = data_frame[non_category_columns + cat_columns].drop_duplicates()
        # drop rows where all category columns are NaN and blank string
        cat_data = cat_data.dropna(subset=cat_columns, how='all')
        cat_data.columns = non_category_columns + [col.upper().replace(x.upper(), 'CATEGORY') for col in cat_columns]
        # add category specific column
        cat_data['CATEGORY'] = [x] * len(cat_data)
        category_split_data.append(cat_data)

    # concatenate stacked data into single DataFrame
    reconfigured_data = pd.concat(category_split_data)

    return reconfigured_data


def splits_concept_levels(data: pd.DataFrame, type_col: str) -> List:
    """Takes a Pandas DataFrame and a string containing a keyword and with the keyword, splits the input DataFrame
    into concept and ancestor-level data. The keyword is used to obtain relevant columns where the data differs for
    concepts and ancestors.

    Args:
        data: A Pandas DataFrame containing stacked mapping results.
        type_col: A string containing the data type to parse (e.g. "DBXREF" or "STRING").

    Returns:
        A list of tuples, each tuple contains a Pandas DataFrame and a list, the first contains a subset of the
            original data to a specific set of columns and the list contains all ontology concepts that were
            annotated to the OMOP concepts contained in the Pandas DataFrame. The first tuple contains data at the
            concept level and the second tuple contains data at the ancestor level.
    """

    # extract relevant columns
    all_cols = [x for x in data.columns if type_col not in x]
    conc_type = [x for x in data.columns
                 if 'CONCEPT' in x.upper() and type_col.upper() in x.upper()]
    conc_type_uri = [x for x in conc_type if x.upper().endswith('URI')][0]
    anc_type = [x for x in data.columns
                if 'ANCESTOR' in x.upper() and type_col.upper() in x.upper()]
    anc_type_uri = [x for x in anc_type if x.upper().endswith('URI')][0]

    # extract concept codes from ancestor codes
    concept = data[all_cols + [x for x in data.columns
                               if 'CONCEPT_' + type_col in x]].dropna(subset=conc_type, how='all').drop_duplicates()
    ancestor = data[all_cols + [x for x in data.columns
                                if 'ANCESTOR_' + type_col in x]].dropna(subset=anc_type, how='all').drop_duplicates()

    # get counts of ontology concepts at each concept level
    concept_ont_codes = [i for j in [x.split(' | ') for x in list(concept[conc_type_uri])] for i in j]
    ancestor_ont_codes = [i for j in [x.split(' | ') for x in list(ancestor[anc_type_uri])] for i in j]

    return [(concept, concept_ont_codes), (ancestor, ancestor_ont_codes)]
