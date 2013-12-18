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

STATE = [('draft', 'Draft'),
         ('opened', 'Opened'),
         ('confirmed', 'Confirmed'),
         ('closed', 'Closed'),
         ('cancelled', 'Cancelled')]

class TrainingSession(ModelView, ModelSQL):
    'Session'
    __name__ = 'training.session'

    name = fields.Char('Name', required=True)
    state = fields.Selection(STATE,
                                   'State',
                                   required=True,
                                   readonly=True,
                                   help="The status of the session",
                                  )
    done = fields.boolean('Done')
    offer = fields.Many2One('training.offer',
                                     'Offer',
                                     required=True,
                                     help="Allows to select a validated offer for the session",
                                     domain=[('state', '=', 'validated')]
                                    )
    
    start_date = fields.Date('Start Date',
                                 required=True,
                                 help="The date of the planned session"
                                )
    date_end = fields.Date('End Date',
                                 help="The end date of the planned session"
                                )
    catalog = fields.Many2One('training.catalog',
                                        'Catalog',
                                        help="The catalog for the session",
                                        required=True)
    faculty = fields.Many2One('training.faculty',
                                    'Responsible',
                                    required=True, 
                                    domain = [('is_faculty','=',True)])
    participant_count = fields.Integer('Participant Count')
    min_limit = fields.Integer('Mininum Threshold',
                               help="The minimum threshold is the minimum of the minimum threshold of each seance",
                                )
    max_limit = fields.Integer('Maximum Threshold',
                                      help="The maximum threshold is the minimum of the maximum threshold of each seance"
                                      )
    active = fields.Boolean('Active')
    #pending hourly

    @staticmethod
    def default_state():
        return 'draft'
    
    @staticmethod
    def default_min_limit():
        return 1
    
    @staticmethod
    def default_max_limit():
        return 1
    
    @staticmethod
    def default_active():
        return True

class TrainingCatalog(ModelView, ModelSQL):
    'Catalog'
    __name__ = 'training.catalog'

    name = fields.Char('Title', required=True)
    year = fields.Integer('Year', required=True,
                                help="The year when the catalog has been published")
    sessions = fields.One2Many('training.session',
                                        'catalog',
                                        'Sessions',
                                        help="The sessions in the catalog")
    note = fields.Text('Note',
                             translate=True,
                             help="Allows to write a note for the catalog"),
    state = fields.Selection(STATE,
                              'State', required=True,
                              help="The status of the catalog")
    @staticmethod
    def default_year():
        year =  datetime.year
        return year 
    
    @staticmethod
    def default_state(): 
        return 'draft'