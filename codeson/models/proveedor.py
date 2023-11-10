from odoo import models, fields, api


class proveedores(models.Model):
    _inherit = 'res.partner'
    clave = fields.Integer(string="Clave")
