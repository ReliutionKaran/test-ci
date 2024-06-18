from odoo import fields, models, api

class ResCompany(models.Model):
    _name = "res.company"
    _inherit = "res.company"

    company_logo = fields.Binary(string="Company Logo")
    term_and_condition = fields.Html(string="Term & Condition")
