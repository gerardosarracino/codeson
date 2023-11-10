from odoo import models, fields, api

class usuarios_sistema(models.Model):
    _inherit = 'res.users'
    unidad_administrativa = fields.Many2many('codeson.unidad_administrativa')

class empleados_sistema(models.Model):
    _inherit = 'hr.employee'
    nivel = fields.Many2one('codeson.usuarios_nivel')
    unidad_administrativa = fields.Many2many('codeson.unidad_administrativa')
    saludo = fields.Char(string="Saludo (Sr./Ing/Sra...)")
    director = fields.Boolean(string="¿Es director?")
    clave = fields.Char(string="Clave de Empleado")

class empleados_nivel(models.Model):
    _name = 'codeson.usuarios_nivel'
    name = fields.Char('Nombre de nivel')
