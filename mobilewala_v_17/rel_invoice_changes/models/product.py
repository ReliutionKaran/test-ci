from odoo import fields, models, api

class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = "product.template"

    warranty_id = fields.Many2one('rel.warranty', string='Warranty')
    color_id = fields.Many2one('rel.color', string='Color')


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = "product.product"

    def _compute_display_name(self):
        for record in self:
            if record.color_id:
                record.display_name = f"{record.name} - {record.color_id.color}"
            else:
                record.display_name = record.name