from odoo import models, fields, api
from datetime import datetime


class gasto_comprobacion(models.Model):
    _name='codeson.gasto_comprobacion'
    folio = fields.Char()
    fecha = fields.Date()
    descripcion = fields.Text()
    empleado = fields.Many2one('hr.employee')
    forma_pago = fields.Many2one('codeson.forma_pago')
    cuenta_banco = fields.Many2one('codeson.cuenta_banco')
    folio_cheque = fields.Char('Folio de cheque')
    importe = fields.Float('Importe')
