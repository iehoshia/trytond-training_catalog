#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from trytond.model import ModelView, ModelSingleton, ModelSQL, fields

__all__ = ['TrainingSequences']

# TRAINING SEQUENCES
class TrainingSequences(ModelSingleton, ModelSQL, ModelView):
    'Training Module for Tryton'
    __name__ = 'training.sequences'
    
    catalog_sequence = fields.Property(fields.Many2One(
        'ir.sequence', 'Catalog Sequence', required=True,
        domain=[('code', '=', 'trainig.course')]))
    session_sequence = fields.Property(fields.Many2One(
        'ir.sequence', 'Session Sequence', required=True,
        domain=[('code', '=', 'training.session')]))