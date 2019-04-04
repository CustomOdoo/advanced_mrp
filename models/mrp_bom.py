# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    width = fields.Float('Width')
    length = fields.Float('Length')
    area = fields.Float('Area', compute='compute_area', readonly=True, store=True)
    trim = fields.Float('Trim')
    number_of_ups = fields.Integer('Number of Ups (width)')
    product_qty = fields.Float('Target Output')
    average_total_weight = fields.Float(string='Average Total Weight (grm/pc)', 
        compute='compute_average_total_weight', readonly=True, store=True)
    is_recipe = fields.Float('Is Test')
    target_output = fields.Float('Target Output', compute='compute_target_output', store=True)

    @api.onchange('product_qty')
    @api.depends('product_qty')
    def compute_target_output(self):
        self.target_output = self.product_qty
    
    @api.onchange('width', 'length')
    @api.depends('width', 'length')
    def compute_area(self):
        for record in self:
            record.area = record.width * record.length

    @api.onchange('bom_line_ids')
    @api.depends('bom_line_ids')
    def compute_average_total_weight(self):
        for record in self:
            print("############", "AV Total Weight", sum(record.mapped('bom_line_ids.average_final_weight')))
            record.average_total_weight = sum(record.mapped('bom_line_ids.average_final_weight'))

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_tmpl_id = fields.Many2one('product.template', domain=[('is_raw_material','=',True)])
    micron = fields.Float('Micron')
    density = fields.Float(related='product_tmpl_id.density', string='Density', readonly=True)
    coverage = fields.Float('Coverage', default=100)
    gsm = fields.Float('GSM', compute='compute_gsm', readonly=True)
    average_final_weight = fields.Float('Average Final Weight (grm/pc)',
        compute='compute_average_final_weight', readonly=True)
    average_total_weight = fields.Float('Average Total Weight (grm/pc)', 
        related='bom_id.average_total_weight', readonly=True)
    average_final_content = fields.Float('Average Dry/Final Content',
        compute='compute_average_final_content', readonly=True)
    total_kgs_required = fields.Float('Total Kgs Reqired', readonly=True)

    @api.onchange('micron')
    @api.depends('micron', 'density', 'coverage')
    def compute_gsm(self):
        for record in self:
            record.gsm = record.micron * record.density * (record.coverage / 100)

    @api.onchange('micron', 'bom_id.area')
    @api.depends('bom_id.area', 'micron', 'product_tmpl_id.density', 'coverage')
    def compute_average_final_weight(self):
        for record in self:
            record.average_final_weight = (record.bom_id.area * record.micron * 
                record.product_tmpl_id.density * record.coverage) / 1000000

    @api.onchange('average_final_weight', 'average_total_weight', 'bom_id.target_output')
    @api.depends('average_final_weight', 'bom_id.target_output', 'average_total_weight')
    def compute_average_final_content(self):
        for record in self:
            if record.average_final_weight and record.average_total_weight:
                record.average_final_content = (record.average_final_weight / record.average_total_weight) * record.bom_id.target_output
