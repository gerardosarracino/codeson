from odoo import models, fields, api
from datetime import datetime

class evidencia_apoyo(models.Model):
    _name='codeson.evidencia_apoyo'
    folio = fields.Char(
                        string='Folio',
                        required=True,
                        copy=False,
                        default= lambda self: self.env['ir.sequence'].next_by_code('evidencia_apoyo')
                        )
    fecha_vencimiento = fields.Date()
    apoyo = fields.Many2one('codeson.apoyo')
    fecha_apoyo = fields.Date(related="apoyo.fecha")
    currency_id = currency_id = fields.Many2one('res.currency', string='Currency')
    monto = fields.Monetary('Total',related="apoyo.amount_total")
    estado_evidencia = fields.Selection([
        ('no_iniciado','No iniciado'),
        ('cancelado','Cancelado'),
        ('completado','Completado')
    ],default="no_iniciado")

    documentacion_count = fields.Integer(compute="_contar_documentos")

    @api.one
    def _contar_documentos(self):
        count = self.env['codeson.documento_apoyo'].search_count([
            ('apoyo_id','=',self.apoyo.id)
            ])
        self.documentacion_count = count


class documento_apoyo(models.Model):
    _name='codeson.documento_apoyo'
    name=fields.Char(string="Nombre")
    file=fields.Binary(required=True)
    file_name=fields.Char(required=True)
    apoyo_id=fields.Many2one('codeson.apoyo')
