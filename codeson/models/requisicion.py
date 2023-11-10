# -*- coding: utf-8 -*-

from odoo import models, fields, api

class compra(models.Model):
    _inherit = 'purchase.order'
    autoriza = fields.Many2one('hr.employee', 'Autoriza')
    puesto_autoriza = fields.Char('Puesto de quien autoriza', related="autoriza.job_id.name")
    servicio_requerido = fields.Text('Servicio requerido')
    solicita = fields.Many2one('hr.employee','Solicita')
    puesto_solicita = fields.Char('Puesto de solicitante', related="solicita.job_id.name")
    instalacion = fields.Many2one('codeson.instalacion')
    unidad_administrativa = fields.Many2one('codeson.unidad_administrativa',domain="[('id','in',unidad_administrativa_permitidas)]")
    unidad_administrativa_permitidas = fields.Many2many('codeson.unidad_administrativa',related="creador.unidad_administrativa")
    creador = fields.Many2one('res.users',default=lambda self: self.env.user)



class requisicion(models.Model):
    _inherit = 'purchase.requisition'
    
    autoriza = fields.Many2one('hr.employee', 'Autoriza',required=True)
    puesto_autoriza = fields.Char('Puesto de quien autoriza', related="autoriza.job_id.name")
    servicio_requerido = fields.Text('Servicio requerido',required=True)
    solicita = fields.Many2one('hr.employee','Solicita',required=True)
    puesto_solicita = fields.Char('Puesto de solicitante', related="solicita.job_id.name")
    instalacion = fields.Many2one('codeson.instalacion')
    unidad_administrativa = fields.Many2one('codeson.unidad_administrativa',domain="[('id','in',unidad_administrativa_permitidas)]")
    unidad_administrativa_permitidas = fields.Many2many('codeson.unidad_administrativa',related="creador.unidad_administrativa")
    creador = fields.Many2one('res.users',default=lambda self: self.env.user)



class requisicion_linea(models.Model):
    _inherit = 'purchase.requisition.line'
    codigo = fields.Char(related='product_id.default_code',string="Código")
    obj_gasto = fields.Char(related="product_id.obj_gasto",string="Partida")
    unidad_medida = fields.Many2one('codeson.unidad_medida',string="Unidad de medida", required=True, default=2)
    detalles = fields.Char(string="Detalles")

class compra(models.Model):
    _inherit = 'purchase.order'
    autoriza = fields.Many2one('hr.employee', 'Autoriza')
    puesto_autoriza = fields.Char('Puesto de quien autoriza', related="autoriza.job_id.name")
    solicita = fields.Many2one('hr.employee','Solicita')
    puesto_solicita = fields.Char('Puesto de solicitante', related="solicita.job_id.name")
    instalacion = fields.Many2one('codeson.instalacion')
    unidad_administrativa = fields.Many2one('codeson.unidad_administrativa',domain="[('id','in',unidad_administrativa_permitidas)]")
    unidad_administrativa_permitidas = fields.Many2many('codeson.unidad_administrativa',related="creador.unidad_administrativa")
    creador = fields.Many2one('res.users',default=lambda self: self.env.user)

class compra_linea(models.Model):
    _inherit = 'purchase.order.line'
    unidad_administrativa = fields.Many2one('codeson.unidad_administrativa')
    codigo = fields.Char(related='product_id.default_code',string="Código")
    obj_gasto = fields.Char(related="product_id.obj_gasto",string="Partida")
    unidad_medida = fields.Many2one('codeson.unidad_medida',string="Unidad de medida", default=2)
    detalles = fields.Char(string="Detalles")



#SOLICITIA Y AUTORIZA A LA ORDEN DE compra
#UNIDAD ADMINISTRATIVA E INSTALACIÓnote
#LINEAS DE DIRECCION ó UNIDAD POR ELEMENTO
