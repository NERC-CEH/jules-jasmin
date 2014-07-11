# Header
from sqlalchemy import engine_from_config, Column, Integer, String, ForeignKey, Table, DateTime, create_engine, Text, Boolean, \
    ForeignKeyConstraint, BigInteger, Float
from sqlalchemy.orm import relationship
from joj.model.meta import Session, Base
from contextlib import contextmanager

## Model definitions below ##

class Model(Base):
    """Represents the calculation model used by an Ecomaps analysis"""

    __tablename__ = 'models'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    description = Column(String(500))
    code_path = Column(String(500))

    def __repr__(self):
        """String representation of the model"""

        return "<Model(name=%s, description=%s)>" % (self.name, self.description)

class Analysis(Base):
    """A running of the model, stores setup and result information in the same entity"""

    __tablename__ = 'analyses'

    attributes = {}

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    point_data_dataset_id = Column(Integer, ForeignKey('datasets.id'))
    run_date = Column(DateTime)
    run_by = Column(Integer, ForeignKey('users.id'))
    result_dataset_id = Column(Integer, ForeignKey('datasets.id'))
    viewable_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    model_id = Column(Integer, ForeignKey('models.id'))
    aic = Column(String(50))
    result_image = Column(Text(length=2**31))
    progress_message = Column(String(255))
    complete = Column(Boolean)
    model_formula = Column(String(255))
    input_hash = Column(BigInteger)
    deleted = Column(Boolean)
    description = Column(String(1000))

    unit_of_time = Column(String(255))
    random_group = Column(String(255))
    model_variable = Column(String(255))
    data_type = Column(String(255))
    fit_image = Column(Text(length=2**31))
    job_id = Column(Integer)

    # FK Relationships
    run_by_user = relationship("User", foreign_keys=[run_by])
    point_dataset = relationship("Dataset", foreign_keys=[point_data_dataset_id], lazy='joined', innerjoin=True)
    result_dataset = relationship("Dataset", foreign_keys=[result_dataset_id], lazy='joined')
    viewable_by_user = relationship("User", foreign_keys=[viewable_by])
    model = relationship("Model")

    # M2M for coverage datasets
    coverage_datasets = relationship("AnalysisCoverageDataset", lazy='joined')

    def __repr__(self):
        """String representation of the analysis"""

        return "<Analysis(name=%s, run_date=%s, run_by=%s)>" % (self.name, self.run_date, self.run_by)

class AnalysisCoverageDatasetColumn(Base):

    __tablename__ = 'analysis_coverage_dataset_columns'

    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer)
    dataset_id = Column(Integer)
    column = Column(String(255))
    time_index = Column(Integer)

    #analysis_coverage_dataset = relationship('AnalysisCoverageDataset', foreign_keys=[analysis_id, dataset_id])

    __table_args__ = (ForeignKeyConstraint([analysis_id, dataset_id],
                                           ['analysis_coverage_datasets.analysis_id', 'analysis_coverage_datasets.dataset_id']),
                      {})

class AnalysisCoverageDataset(Base):
    """Provides a link between an analysis and a coverage dataset"""

    __tablename__ = 'analysis_coverage_datasets'

    analysis_id = Column(Integer, ForeignKey('analyses.id'), primary_key=True)
    dataset_id = Column(Integer, ForeignKey('datasets.id'), primary_key=True)

    columns = relationship('AnalysisCoverageDatasetColumn', lazy='joined')

    dataset = relationship('Dataset', lazy='joined')

    def __init__(self, dataset=None, dataset_id=None):
        """Convenience, lets you pass in a dataset or an id"""

        if dataset:
            self.dataset=dataset
        elif dataset_id:
            self.dataset_id = dataset_id
