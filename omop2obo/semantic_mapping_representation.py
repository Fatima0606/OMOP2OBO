#!/usr/bin/env python
# -*- coding: utf-8 -*-


# import needed libraries
import glob  # type: ignore
import os
import pandas as pd  # type: ignore
import re

from abc import ABCMeta, abstractmethod
from datetime import date, datetime  # type: ignore
from rdflib import Graph, Literal, Namespace, URIRef  # type: ignore
from rdflib.namespace import OWL, RDF, RDFS  # type: ignore
from tqdm import tqdm  # type: ignore
from typing import Dict, List, Optional
from uuid import uuid4

from omop2obo.utils import gets_class_ancestors, merges_ontologies

# set up environment variables
obo = Namespace('http://purl.obolibrary.org/obo/')
oboinowl = Namespace('http://www.geneontology.org/formats/oboInOwl#')
omo2obo = Namespace(' https://github.com/callahantiff/omop2obo/obo/ext/')


class SemanticMappingTransformer(object):
    __metaclass__ = ABCMeta

    def __init__(self, ontology_list: List, omop2obo_data_file: str, domain: str, map_type: str = 'multi',
                 ontology_directory: str = Optional[None], superclasses: Dict = Optional[None]) -> None:
        """This class is designed to facilitate the transformation of OMOP2OBO mappings into semantic
        representations. To do this, the class includes several methods that assist with processing different aspects
        of the mapping data. The class currently enables two types of mappings to be created: (1) Single. A single
        mapping processes each OMOP2OBO mapping by ontology, within that ontology; (2) Multi. A multi mapping first
        merges all relevant ontologies and then constructs new OMOP2OBO classes that span multiple ontologies.

        For additional information on this approach please see the dedicated project wiki page:
            https://github.com/callahantiff/OMOP2OBO/wiki/Semantic-Mapping-Representation

        Attributes:
            ontology_list: A list of ontology identifiers (i.e. ['HP', 'MONDO']).
            omop2obo_data_file: A Pandas DataFrame containing OMOP2OBO mapping data. Assumes that the mapping data is
                stored in an xlsx file sheet called "Aggregated_Mapping_Results" and that no additional filtering or
                preprocessing is needed.
                needed
            ontology_directory: A string pointing to a directory that contains OWL ontology files.
            domain: A string specifying the clinical domain. Must be "condition", "measurement", or "drug".
            map_type: A string indicating whether to build single (i.e. 'single') or multi-ontology (i.e. 'multi')
                classes. The default type is "multi".
           superclasses: A dictionary where keys are clinical domains and values are either a dictionary or a URIRef
                object. For example:
                    {'condition': {'phenotype': URIRef('http://purl.obolibrary.org/obo/HP_0000118'),
                                                  'disease': URIRef('http://purl.obolibrary.org/obo/MONDO_0000001')},
                                    'drug': URIRef('http://purl.obolibrary.org/obo/CHEBI_24431'),
                                    'measurement': URIRef('http://purl.obolibrary.org/obo/HP_0000118')}

        Returns:
            None.
        """

        # CREATE CLASS ATTRIBUTES
        self.graph: Graph = Graph()
        self.owltools_location = './omop2obo/libs/owltools'
        self.timestamp = '_' + datetime.strftime(datetime.strptime(str(date.today()), '%Y-%m-%d'), '%d%b%Y').upper()
        self.ontology_data_dict: Dict = {}
        self.class_data_dict: Dict = {}

        # EXISTING OMOP2OBO OWL FILE
        existing_mappings = glob.glob('resources/mapping_semantics/omop2obo*.owl')
        self.current_omop2obo = None if len(existing_mappings) == 0 else existing_mappings[0]

        # ONTOLOGY LIST
        if not isinstance(ontology_list, List):
            raise TypeError('ontology_list must be type str')
        elif len(ontology_list) == 0:
            raise ValueError('ontology_list cannot be an empty list')
        else:
            self.ontologies = ontology_list

        # OMOP2OBO MAPPING DATA
        if not isinstance(omop2obo_data_file, str):
            raise TypeError('omop2obo_data_file must be type str.')
        elif not os.path.exists(omop2obo_data_file):
            raise OSError('The {} file does not exist!'.format(omop2obo_data_file))
        elif os.stat(omop2obo_data_file).st_size == 0:
            raise TypeError('Input file: {} is empty'.format(omop2obo_data_file))
        else:
            print('Loading Mapping Data')
            self.omop2obo_data = pd.read_excel(omop2obo_data_file, sheet_name='Aggregated_Mapping_Results',
                                               sep=',', header=0)
            self.omop2obo_data.fillna('', inplace=True)

        # CLINICAL DOMAIN
        if not isinstance(domain, str):
            raise TypeError('domain must be type str.')
        elif domain.lower() not in ['condition', 'drug', 'measurement']:
            raise ValueError('domain must be one of following string: "condition", "drug", or "measurement"')
        else:
            self.domain = domain.lower()

        # ONTOLOGY DIRECTORY
        onts = 'resources/ontologies' if ontology_directory is None else ontology_directory
        ont_data = glob.glob(onts + '/*.owl')
        if not os.path.exists(onts):
            raise OSError("Can't find 'ontologies/' directory, this directory is a required input")
        elif len(ont_data) == 0:
            raise TypeError('The ontologies directory is empty')
        else:
            # check for ontology data
            ont_check = [x for x in ont_data if x.split('/')[-1].split('_')[0] in [y.lower() for y in self.ontologies]]
            if len(ont_check) == 0:
                raise ValueError('No ontology owl files match provided ontology list')
            else:
                self.ont_directory = ont_data

        # CLASS CONSTRUCTION TYPE
        if not isinstance(map_type, str):
            raise TypeError('map_type must be type string')
        else:
            self.construction_type = 'single' if map_type != 'multi' else map_type

        # check subclass dict input
        if self.construction_type == 'multi':
            if superclasses is not None:
                if not isinstance(superclasses, Dict):
                    self.superclass_dict: Optional[Dict] = superclasses
                else:
                    raise TypeError('superclasses must be type Dict')
            else:
                self.superclass_dict = {
                    'condition': {'phenotype': URIRef('http://purl.obolibrary.org/obo/HP_0000118'),
                                  'disease': URIRef('http://purl.obolibrary.org/obo/MONDO_0000001')},
                    'drug': URIRef('http://purl.obolibrary.org/obo/CHEBI_24431'),
                    'measurement': URIRef('http://purl.obolibrary.org/obo/HP_0000118')}
        else:
            self.superclass_dict = None

        # RO RELATIONS FOR MULTI-ONTOLOGY CLASSES
        if self.construction_type == 'multi':
            rel_data_loc = 'resources/mapping_semantics/omop2obo_class_relations.txt'
            if not os.path.exists(rel_data_loc):
                raise OSError('The {} file does not exist!'.format(rel_data_loc))
            elif os.stat(rel_data_loc).st_size == 0:
                raise TypeError('Input file: {} is empty'.format(rel_data_loc))
            else:
                print('Loading Multi-Ontology Class Construction Relations')
                rel_data = glob.glob('resources/mapping_semantics/omop2obo_class_relations.txt')[0]
                self.multi_class_relations: Optional[Dict] = {}
                with open(rel_data, 'r') as f:
                    for x in f.read().splitlines()[1:]:
                        row = [i.strip() for i in x.split(',')]
                        key = row[1] + '-' + row[3]
                        if row[0] in self.multi_class_relations.keys():
                            self.multi_class_relations[row[0]]['relations'][key] = URIRef(row[2])
                        else:
                            self.multi_class_relations[row[0]] = {'relations': {}}
                            self.multi_class_relations[row[0]]['relations'] = {key: URIRef(row[2])}
                f.close()
        else:
            self.multi_class_relations = None

    def loads_ontology_data(self) -> Dict:
        """Method iterates over each ontology in the ontologies attribute and loads them as RDFLib Graph objects. For
        both "single" and "multi" class construction_types the ontology prefixes are used as dictionary keys and the
        RDFLib Graph objects are the values. If the construction_type is "multi" then an additional key is added to
        the dictionary where the value contains all of the ontologies merged together.

        Returns:
            ontology_data_dict:A dictionary containing ontology data. If construction_type is "single" or "multi" then
                the keys correspond to the entries in ontology_list and values are RDFLib Graph objects. If the
                construction_type is "multi" then an additional key is added to store the merged ontology data.
        """

        ontology_data, ontology_files = {}, []
        write_loc = os.path.relpath('/'.join(self.ont_directory[0].split('/')[:-1]))

        for ont in self.ontologies:
            print('Loading: {}'.format(ont.upper()))
            # store ontology prefix as key and RDFLib graph objects as values
            ont_file = [x for x in self.ont_directory if ont in x][0]
            ontology_files.append(ont_file)
            ontology_data[ont] = Graph().parse(ont_file, format='xml')
        if self.construction_type == 'multi':  # merge all relevant ontologies and add to ontology_data dictionary
            omop2obo_merged_filepath = '/OMOP2OBO_MergedOntologies' + self.timestamp + '.owl'
            merges_ontologies(ontology_files, write_loc, omop2obo_merged_filepath, self.owltools_location)
            print('Loading merged ontology data: {}'.format(write_loc + omop2obo_merged_filepath))
            ontology_data['merged'] = Graph().parse(write_loc + omop2obo_merged_filepath, format='xml')

        return ontology_data

    @staticmethod
    def extracts_logic_information(logic: str, constructors: List, uri_info: Optional[Dict] = None) -> List:
        """Recursively parses a string containing logical constructor information (e.g. "AND(0,OR(1, 2))") with the
        goal of extracting each OWL constructor and the URI indexes it points to. The method returns a list of lists,
        where each inner list contains an OWL constructor and it's indexes or other OWL constructors if the logic
        string contains several chained constructors (e.g. "AND(OR(0, 1) ,OR(2, 3))").

        Args:
            logic: A string containing a logic statement (e.g. "AND(0, OR(1, 2), 3)").
            constructors: A list of OWL constructors (e.g. ['AND', 'OR']).
            uri_info: A nested list of OWL constructors and URI indexes (details on item under Returns). This is an
                optional parameter.

        Returns:
            uri_info: A nested list of OWL constructors and URI indexes. In each inner list there are two items where
                the first item contains a string representing an OWL constructor and the second item contains a
                comma-delimited string of URI indexes.
        """

        # instantiate list object if none passed to function
        uri_info = [] if uri_info is None else uri_info

        if (len(logic) == 0 and len(constructors) == 0) or logic == 'N/A':
            return uri_info
        elif ('()' in logic or ',' not in logic) or len(constructors) == 1:
            const, inner_constructors = constructors.pop(0), [x[0] for x in uri_info]
            if '()' in logic:
                uri_info.append([const, ', '.join(inner_constructors)])
            else:
                extracted_info = [re.search(r'(?<={}\().*?(?=\))'.format(const), logic).group(0)]
                uri_info.append([const, ', '.join(extracted_info + inner_constructors)])
            return SemanticMappingTransformer.extracts_logic_information('', constructors, uri_info)
        else:
            const = constructors.pop(0)
            extracted_info = re.search(r'(?<={}\().*?(?=\))'.format(const), logic).group(0)
            updated_logic = re.sub(r'\s,|,\s(?=\))', '', logic.replace('{}({})'.format(const, extracted_info), ''))
            uri_info.append([const, extracted_info])
            return SemanticMappingTransformer.extracts_logic_information(updated_logic, constructors, uri_info)

    # def complement_of_constructor(self, namespace: URIRef, class_info: List) -> List:
    #     """
    #
    #     Args:
    #         namespace:
    #         class_info:
    #
    #     Returns:
    #         complement_constructor: A list of triples needed to create a complement of constructor a given
    #     """
    #
    #     complement_constructor = []
    #     uri, label = class_info
    #
    #     # create triples
    #
    #
    #
    #     return complement_constructor

    # def union_of_constructor(self, namespace: URIRef, class_information) -> List:
    #
    #     union_constructor = []
    #     uid = URIRef(namespace + 'N' + uuid4().hex)
    #
    #     #

    # def intersection_of_constructor(self, namespace: URIRef, class_information) -> List:
    #
    #     union_constructor = []
    #     uid = URIRef(namespace + 'N' + uuid4().hex)
    #
    #     #

    def class_constructor(self, class_info: List, logic: List, ont: str, roots: Optional[List] = None) -> List:
        """

        Args:
            class_info:
            logic:
            ont: A string containing an ontology prefix (e.g. "hp", "chebi").
            roots:

        Returns:
            triples:
        """

        triples = []
        logic, uri, label = class_info

        self.superclass_dict

        return triples

    def transforms_mappings(self) -> None:
        """Method parses a Pandas DataFrame containing OMOP2OBO mappings and builds semantic representations of the
        mappings for single ontology or for a collection of ontologies. If the OMOP2OBO mapping file contains
        multiple ontologies, but the class construction type is "single" then an owl file is serialized for each

        Returns:
            None.
        """

        pass

    @abstractmethod
    def gets_class_construction_type(self) -> str:
        """"A string detailing whether or not the classes are constructed using a single or multiple ontologies."""

        pass


class SingleOntologyConstruction(SemanticMappingTransformer):

    def gets_class_construction_type(self) -> str:
        """"A string representing the type of knowledge graph being built."""

        return 'Single Ontology Class Construction'

    def transforms_mappings(self) -> None:
        """

        Returns:
             None.
        """

        # STEP 1 - Load Ontologies
        self.ontology_data_dict = self.loads_ontology_data()

        # STEP 2 - Process mapping data
        for idx, row in tqdm(omop2obo_data.iterrows(), total=omop2obo_data.shape[0]):
            clin_id, label, cui, sem_typ = row['CONCEPT_ID'], row['CONCEPT_LABEL'], row['CUI'], row['SEMANTIC_TYPE']
            class_data_dict[clin_id] = {'label': label, 'cui': cui, 'semantic_type': sem_typ}

            for ont in ontologies:
                # get information to needed to build classes
                logic, uri, label = row[ont.upper() + '_LOGIC'], row[ont.upper() + '_URI'], row[ont.upper() + '_LABEL']
                mapping, evidence = row[ont.upper() + '_MAPPING'], row[ont.upper() + '_EVIDENCE']
                class_info = [logic, uri, label, mapping, evidence]

                # extract OWL constructors and order inside out (inner constructors appear first)
                constructors = [x for x in ['AND', 'OR', 'NOT'] if x in logic][::-1]
                logic_info = SingleOntologyConstruction.extracts_logic_information(logic, constructors.copy())

                # check for ontology ancestor -- only done for CHEBI
                if ont.upper() == 'CHEBI':
                    root_nodes = {x: gets_class_ancestors(self.ontology_data_dict[ont], [x]) for x in uri.split(' | ')}
                else:
                    root_nodes = None

                # single ontology construction
                class_constructor(class_info, logic_info, ont, root_nodes)

        # multiple ontology construction (multiple ontology method only)
        # calls evidence adding and mapping information

        # STEP 3 - Add Classes to Ontology Data

        # STEP 4 - Serialize Updated Ontologies

        return None


class MultipleOntologyConstruction(SemanticMappingTransformer):

    def gets_class_construction_type(self) -> str:
        """"A string representing the type of knowledge graph being built."""

        return 'Multiple Ontology Class Construction'

    # function here to assemble multiple ontology mappings --> only done for this child class

    # def transforms_mappings(self):
    #
    #
    #     for idx, row in omop2obo_data.iterrows():
    #         logic = row['HP_LOGIC']
    #         uri = row['HP_URI']
    #         labels = row['HP_LABEL']
    #
    #         # for each ontology
    #
    #         # multi or single?
    #
    #
    #     # get
    #
    #     return None