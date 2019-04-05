from odoo import models, api, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    raw_material_category = fields.Selection([
        ('plain', 'Plain/Printed film'),
        ('laminate1', 'Laminate 1'),
        ('laminate2', 'Laminate 2'),
        ('ink', 'Ink'),
        ('solvent', 'Solvent'),
        ('adhessive', 'Adhessive')], string='Raw Material Category')