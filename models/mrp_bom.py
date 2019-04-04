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
    average_final_weight = fields.Float(related='bom_line_ids.average_final_weight', 
        string='Average Final Weight (grm/pc)', readonly=True, compute='compute_average_final_weight')
    average_total_weight = fields.Float(related='bom_line_ids.average_total_weight', 
        string='Average Total Weight (grm/pc)', readonly=True, compute='compute_average_total_weight')
    average_final_content = fields.Float(related='bom_line_ids.average_final_content',
        string='Average Dry/Final Content', readonly=True, compute='compute_average_final_content')
    total_kgs_required = fields.Float(related='bom_line_ids.total_kgs_required',
        string='Total Kgs Reqired', readonly=True, compute='compute_total_kgs_required')
    is_recipe = fields.Float('Is Test')
    target_output = fields.Float('Target Output', compute='compute_target_output', store=True)

    @api.onchange('product_qty')
    def compute_target_output(self):
        self.target_output = self.product_qty
    
    @api.onchange('width', 'length')
    def compute_area(self):
        for record in self:
            record.area = record.width * record.length

    @api.onchange('area')
    @api.depends('bom_line_ids.micron', 'bom_line_ids.product_tmpl_id.density', 'bom_line_ids.coverage')
    def compute_average_final_weight(self):
        for record in self.bom_line_ids:
            record.average_final_weight = (self.area * record.micron * 
                record.product_tmpl_id.density * record.coverage) / 1000000
    
    @api.onchange('average_final_weight', 'target_output')
    def compute_average_final_content(self):
        for record in self:
            if record.average_final_weight and record.average_total_weight:
                record.average_final_content = (record.average_final_weight / record.average_total_weight) * record.target_output

    @api.onchange('bom_line_ids')
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
    average_final_weight = fields.Float('Average Final Weight (grm/pc)', readonly=True)
    average_total_weight = fields.Float('Average Total Weight (grm/pc)', readonly=True)
    average_final_content = fields.Float('Average Dry/Final Content', readonly=True)
    total_kgs_required = fields.Float('Total Kgs Reqired', readonly=True)

    @api.onchange('micron')
    @api.depends('micron', 'density', 'coverage')
    def compute_gsm(self):
        for record in self:
            record.gsm = record.micron * record.density * (record.coverage / 100)