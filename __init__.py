# This file is part of subscription module of Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .configuration import *
from .training import *

def register():
    Pool.register(
        TrainingSequences,
        TrainingCatalog,
        TrainingSession,
        module='training_catalog', type_='model')
