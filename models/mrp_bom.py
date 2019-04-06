# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    width = fields.Float('Width (mm)')
    length = fields.Float('Length (mm)')
    area = fields.Float('Area (mm)', compute='compute_area', readonly=True, store=True)
    trim = fields.Float('Trim (mm)')
    number_of_ups = fields.Integer('Number of Ups (width)', default=1)
    product_qty = fields.Float('Target Output')
    average_total_weight = fields.Float(string='Average Total Weight (grm/pc)', 
        compute='compute_average_total_weight', readonly=True, store=True)
    is_recipe = fields.Float('Is Test')
    target_output = fields.Float('Target Output', compute='compute_target_output', store=True)
    average_yield = fields.Float('Average Yield (Pcs/Kg)', compute='compute_average_yield')
    expected_pcs_per_target_putput = fields.Float('Expected Pcs per Target Output', 
        compute='compute_expected_pcs_per_target_output')

    @api.onchange('product_qty')
    @api.depends('product_qty')
    def compute_target_output(self):
        for record in self:
            record.target_output = record.product_qty
    
    @api.onchange('width', 'length')
    @api.depends('width', 'length')
    def compute_area(self):
        for record in self:
            record.area = record.width * record.length

    @api.onchange('bom_line_ids')
    @api.depends('bom_line_ids')
    def compute_average_total_weight(self):
        for record in self:
            record.average_total_weight = sum(record.mapped('bom_line_ids.average_final_weight'))
    
    @api.onchange('average_total_weight')
    @api.depends('average_total_weight')
    def compute_average_yield(self):
        for record in self:
            if record.average_total_weight:
                record.average_yield = 1000 / record.average_total_weight
    
    @api.onchange('target_output', 'average_yield')
    @api.depends('target_output', 'average_yield')
    def compute_expected_pcs_per_target_output(self):
        for record in self:
            record.expected_pcs_per_target_putput = record.product_qty * record.average_yield

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
    total_kgs_required = fields.Float('Total Kgs Reqired',
        compute='compute_total_kgs_required', readonly=True, store=True)
    product_qty = fields.Float(related='total_kgs_required', store=True)

    @api.onchange('micron')
    @api.depends('micron', 'density', 'coverage')
    def compute_gsm(self):
        for record in self:
            record.gsm = record.micron * record.density * (record.coverage / 100)

    @api.onchange('micron', 'bom_id.area')
    @api.depends('bom_id.area', 'micron', 'product_tmpl_id.density', 'coverage', 'sequence')
    def compute_average_final_weight(self):
        for record in self:
            record.average_final_weight = (record.bom_id.area * record.micron * 
                record.product_tmpl_id.density * (record.coverage / 100)) / 1000000

    @api.onchange('average_final_weight', 'average_total_weight', 'sequence')
    @api.depends('average_final_weight', 'bom_id.width', 'bom_id.number_of_ups', 'average_total_weight', 'bom_id.target_output')
    def compute_total_kgs_required(self):
        for record in self:
            if record.average_total_weight and record.bom_id.number_of_ups:
                if record.product_tmpl_id.raw_material_category == 'plain':
                    record.total_kgs_required = ((record.average_final_weight / record.bom_id.width) * 
                        ((record.bom_id.width * record.bom_id.number_of_ups) + record.bom_id.trim) / 
                        (record.average_total_weight * record.bom_id.number_of_ups) * record.bom_id.target_output) + 15
                elif record.product_tmpl_id.raw_material_category == 'laminate1' or record.product_tmpl_id.raw_material_category == 'laminate2':
                    record.total_kgs_required = ((record.average_final_weight / record.bom_id.width) * 
                        ((record.bom_id.width * record.bom_id.number_of_ups) + record.bom_id.trim) / 
                        (record.average_total_weight * record.bom_id.number_of_ups) * record.bom_id.target_output)
                elif record.product_tmpl_id.raw_material_category == 'adhessive':
                    record.total_kgs_required = ((record.average_final_weight / record.bom_id.width) * 
                        ((record.bom_id.width * record.bom_id.number_of_ups) + 10) / 
                        (record.average_total_weight * record.bom_id.number_of_ups) * record.bom_id.target_output)
                    record.average_final_content = record.total_kgs_required
                elif record.product_tmpl_id.raw_material_category == 'ink':
                    record.total_kgs_required = ((record.average_final_weight / record.bom_id.width) * 
                        ((record.bom_id.width * record.bom_id.number_of_ups) + record.bom_id.trim) / 
                        (record.average_total_weight * record.bom_id.number_of_ups)) * record.bom_id.target_output / 0.3

    @api.onchange('average_final_weight', 'average_total_weight', 'sequence')
    @api.depends('average_final_weight', 'bom_id.target_output', 'average_total_weight')
    def compute_average_final_content(self):
        for record in self:
            if record.average_final_weight and record.average_total_weight:
                if record.product_tmpl_id.raw_material_category == 'plain' or 'laminate1':
                    record.average_final_content = (record.average_final_weight / 
                        record.average_total_weight) * record.bom_id.target_output
                elif record.product_tmpl_id.raw_material_category == 'ink':
                    record.average_final_content = ((record.average_final_weight / record.bom_id.width) * 
                        ((record.bom_id.width * record.bom_id.number_of_ups) + record.bom_id.trim) / 
                        (record.average_total_weight * record.bom_id.number_of_ups)) * record.bom_id.target_output