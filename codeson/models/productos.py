from odoo import models, fields, api

class producto(models.Model):
    _inherit = 'product.template'
    obj_gasto = fields.Char(compute="_calc_objeto")

    @api.one
    def _calc_objeto(self):    #EN FORMA DE STRING
        try:
            partida_str = self.obj_gasto=self.default_code[:5]
            obj_orm = self.env['codeson.clas_obj_gasto']
            partida = obj_orm.search([('partida','=',partida_str)])
        except:
            pass

        self.obj_gasto = ""
        try:
            partida = partida[0]
            self.obj_gasto = "[" + partida.partida + "] " + partida.name
        except:
            pass



    clas1 = fields.Many2one('codeson.clas_obj_gasto',domain="[('partida','=like','%0000')]")
    clas2 = fields.Many2one('codeson.clas_obj_gasto',domain="[('partida','not like','%0000'),('partida','=like','%000'),('padre','=',clas1)]")
    clas3 = fields.Many2one('codeson.clas_obj_gasto',domain="[('partida','not like','%0000'),('partida','not like','%000'),('padre','=',clas2)]")
    partida_especifica = fields.Many2one('codeson.clas_obj_gasto',domain="[('partida','not like','%0000'),('partida','not like','%000'),('padre','=',clas3)]")

    consecutivo = fields.Integer()
    codigo = fields.Char()

    partida = fields.Char()# NUM
    de_importacion = fields.Boolean('Importado',compute="_check_importado")

    @api.one
    def _check_importado(self):
        try:
            if self.codigo[5] == '0':
                self.de_importacion = True
            else:
                self.de_importacion = False
                self.codigo = self.default_code
        except:
            pass


    @api.onchange('clas1')
    def _clear_clas2_clas3(self):
        self.clas2 = False
        self.clas3 = False

    @api.onchange('clas2')
    def _clear_clas2(self):
        self.clas3 = False

    @api.onchange('clas3')
    def _camb_clas3(self):
        self.partida_especifica = False

    @api.onchange('partida_especifica')
    def _camb_p_esp(self):
        if self.partida_especifica == False:
            self.consecutivo = False
        else:
            try:
                obj_orm = self.env['product.template']
                self.consecutivo = len(obj_orm.search([('default_code','=like',self.partida_especifica.partida + '1%')])) + 1
                self.codigo = self.partida_especifica.partida + "1" + str(self.consecutivo).rjust(4,'0')
                self.default_code = self.codigo
            except:
                pass

#    @api.onchange('partida_especifica')
#    def _on_part_ch(self):
#        obj_orm = self.env['product.template']
#        objetos = obj_orm.search([('default_code','=like',str(self.clas3.partida) + '%')])
