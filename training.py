#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from decimal import Decimal
from datetime import datetime, timedelta, date
import operator
from itertools import izip, groupby
from sql import Column, Literal
from sql.aggregate import Sum
from sql.conditionals import Coalesce

from trytond.model import Workflow, ModelView, ModelSQL, fields
from trytond.wizard import Wizard, StateView, StateAction, StateTransition, \
    Button
from trytond.report import Report
from trytond.tools import reduce_ids
from trytond.pyson import Eval, PYSONEncoder, Date, Id
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond import backend

STATES = {
    'readonly': (Eval('state') != 'draft'),
}

STATES_CONFIRMED = {
    'readonly': (Eval('state') != 'draft'),
    'required': (Eval('state') == 'confirmed'),
}

GUARANTEE = [
    ('payment', 'Payment'),
    ('voucher', 'Voucher'),
    ('credit_card', 'Credit Card'),
    ('letter', 'Letter'),
    ]

class TrainingCatalog(ModelView, ModelSQL):
    'Catalog'
    __name__ = 'training.catalog'

    
    name = fields.Char('Title', size=64, required=True, select=1),
    year = fields.Integer('Year', required=True,
                                help="The year when the catalog has been published")
    sessions = fields.One2Many('training.session',
                                        'catalog',
                                        'Sessions',
                                        help="The sessions in the catalog")
    note = fields.Text('Note',
                             translate=True,
                             help="Allows to write a note for the catalog"),
    state = fields.Selection([('draft','Draft'),
                              ('validated', 'Validated'),
                              ('inprogress', 'In Progress'),
                              ('deprecated', 'Deprecated'),
                              ('cancelled','Cancelled'),],
                              'State', required=True, readonly=True,
                              help="The status of the catalog")
    
    def default_year(self):
        year =  datetime.now()
        return year 
    
    def default_state(self): 
        return 'draft'

class TrainingGroup(ModelView, ModelSQL):
    'Group'
    __name__ = 'training.group'
    
    name = fields.Char('Name', required=True, help="The group's name",)
    session = fields.Many2One('training.session', 'Session', required=True, ondelete='CASCADE')
    seances = fields.One2Many('training.seance', 'group', 'Seances', readonly=True)

    @classmethod
    def __setup__(cls):
        super(TrainingGroup, cls).__setup__()
        cls._sql_constraints += [
            ('uniq_name_session', 'UNIQUE(name, session_id)', 'It already exists a group with this name.'),
            ]
