# -*- coding: utf-8 -*-

from odoo import models, fields, api

class instalacion(models.Model):
    _name = "codeson.instalacion"
    name = fields.Char("Nombre")

class proyecto_proceso(models.Model):
    _name = "codeson.proyecto_proceso"
    name = fields.Char("Nombre")
    clave = fields.Char("Clave")

class unidad_administrativa(models.Model):
    _name = "codeson.unidad_administrativa"
    name = fields.Char("Nombre")
    clave = fields.Char("Clave")
    registro = fields.Boolean("¿Es de registro? (Ramo / Unidad responsable)")

class clasificador_objeto_gasto(models.Model):
    _name = 'codeson.clas_obj_gasto'
    name = fields.Char('Nombre')
    partida = fields.Char('Partida')
    utilizar = fields.Boolean('Utilizar')
    registro = fields.Boolean('Registro')
    padre = fields.Many2one('codeson.clas_obj_gasto',compute="_calcular_padre",store=True)

    @api.one
    def name_get(self):
        return (self.id,"[" + str(self.partida) +  "] " + str(self.name))

    @api.one
    def _calcular_padre(self):
        foo = self.partida.strip('0')  # convierte 11000 en 11  y 11010 en 1101
        obj_orm = self.env['codeson.clas_obj_gasto']
        if len(foo) == 1:
            self.padre = False
        if len(foo) == 2:
            self.padre = obj_orm.search([('partida','=',foo[0].ljust(5,'0'))])
        if len(foo) == 3:
            self.padre = obj_orm.search([('partida','=',foo[0:2].ljust(5,'0'))])
        if len(foo) > 3:
            self.padre = obj_orm.search([('partida','=',foo[0:3].ljust(5,'0'))])


class unidad_medida(models.Model):
    _name = 'codeson.unidad_medida'
    name = fields.Char('Nombre')
