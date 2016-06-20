



from sqlalchemy import create_engine, Column, Integer, Float, String, Numeric, ForeignKey

from sqlalchemy.orm import sessionmaker, relationship
import os
import csv




class SequenceTable:
    __tablename__ = 'sequencetable'
    id = Column(Integer, primary_key=True)
    sequence_a = Column(String)
    sequence_b = Column(String)
    sci_score = relationship("SCIScoreTable")

class CombinationsTable:
    __tablename__ = 'combinationstable'
    id = Column(Integer, primary_key=True)
    e = Column(Numeric)
    o = Column(Numeric)
    t = Column(Numeric)
    k = Column(Numeric)
    Tt = Column(Integer)
    Ss = Column(Integer)
    sci_score = relationship("SCIScoreTable")

    @classmethod
    def from_file_name(cls, filename):
        params = os.path.basename(filename)
        params = params.replace('.dotaligner.out.sci', '')
        params = params.split('_')
        params = [ { x[0] : x[1]} for x in params]
        entry = cls(e=params['e'], o=params['o'], t = params['t'] , k = params['k'], Tt = params['T'], Ss =['S'])
        return entry

class SCIScoreTable:
    __tablename__ =  'sci_score'
    id = Column(Integer, primary_key=True)
    sequence_pair_id = Column(Integer, ForeignKey('sequencetable.id'))
    combination_id = Column(Integer, ForeignKey('combinationstable.id'))
    sci_score = Column(Numeric)


class dbPopulator:

    def __init__(self, directory, dbInstance):
        files = os.listdir(directory)
        files = [ os.path.join(directory, x ) for x in files ]
        self.directory = directory
        self.files  = files
        self.db = dbInstance

    def populate_database(self, combinationTable):
        combinations = []
        for x in self.files:
            combinations_entry = combinationTable.from_file_name(x)
            combinations.append(combinations)

    def get_sci_from_file(self, file):
        with open(file) as csvfile:
            reader = csv.DictReader(csvfile, delimiter='\t' )
            for entry in reader:
                sequence_a_id = self._extract_sequence_name(entry['SequenceA'])
                sequence_b_id = self._extract_sequence_name(entry['SequenceB'])
                sci_score = entry['SCI']

    def _extract_sequence_name(self, sequence_name):
        sequence_name = os.path.basename(sequence_name)
        sequence_name = sequence_name.replace('_dp.pp', '')
        return sequence_name







class dbManager:
    def __init__(self, dbname, engine):
        self.id = dbname
        self.engine = create_engine(engine, echo=True)

    def start_session(self):
        self.session = sessionmaker(bind=self.engine)

    def add_to_session(self, instance):
        session = self.session()
        session.add(instance)
        session.commit()

    def add_all_session(self, instances):
        session = self.session()
        session.add_all(instances)
        session.commit()



def get_sci_score(filename):
    sci_score = {}
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            sequence_pair = "%s-%s" % ( row['SequenceA'] , row['SequenceB'])
            sci_score = row['SCI']
            sequence_a_clean = row['SequenceA'].replace('data/ps/', '_dp.pp')










def get_parameters(filename):
    """
    :param filename: filename and get parameters from filename
    :return: dictionary containing key value pair with key as the parameter and the value.
    """
    params = os.path.basename(filename)
    params = params.replace('results.sci' , '')
    params = params.split('_')
    params_dict = {}
    for x in params:
        p = x.split('-')
        params_dict[p[0]] = p[1]
    return params_dict










