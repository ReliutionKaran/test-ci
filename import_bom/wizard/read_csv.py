# -*- coding: utf-8 -*-

import datetime
import base64
import io
import logging
import pandas as pd
from odoo import fields, models, _
from odoo.exceptions import ValidationError

_LOGGER = logging.getLogger("===== Import Bom with Lines =====")


class ImportProducts(models.TransientModel):
    _name = 'import.bom.wizard'
    _description = "Import BoM With Lines"

    csv_file = fields.Binary('Select File', required=True)
    csv_delimiter = fields.Selection([(',', 'Commas'),
                                      (';', 'Semicolons'),
                                      ('\t', 'Tabs'),
                                      ('|', 'Pipes')], string='CSV Delimiter', default=',')
    bom_type = fields.Selection(
        [('casing', 'Import Casings'), ('dial', 'Import Dial'), ('caseparts', 'Import Caseparts'),
         ('caliber', 'Import Movements'), ('models', 'Import Model'), ('band', 'Import Band')], string="BoM Type",
        default="casing")

    def import_bom(self):
        if self.bom_type == 'casing':
            self.import_casing()
        elif self.bom_type == 'band':
            self.import_band()
        elif self.bom_type == 'dial':
            self.import_dial()
        elif self.bom_type == 'caliber':
            self.import_caliber()
        elif self.bom_type == 'models':
            self.import_model_products()
        elif self.bom_type == 'caseparts':
            self.import_caseparts()

    def read_file(self, col_list, csv_delimiter=","):
        try:
            csv_data = base64.b64decode(self.csv_file)
            file = io.StringIO(csv_data.decode("utf-8"))
            csvfile = pd.read_csv(file, sep=csv_delimiter)
            csvfile.drop_duplicates(inplace=True)  # removes duplicate row from dataframe/Table
            csvfile.dropna(subset=col_list, inplace=True)
            csvfile.fillna('None', inplace=True)
            data = csvfile.to_dict('split')
            return data
        except Exception as error:
            # Could not get a csv dialect -> probably not a csv.
            raise ValidationError(f"Exception {error} occurs! May be the selected CSV Delimiter is not matched "
                                  f"with file delimiter!")

    def import_band(self):
        empty_cols, import_logs, products = ['BandNo'], "", set()
        _LOGGER.info(f"Start Process: {datetime.datetime.now()}")
        file_data = self.read_file(empty_cols, self.csv_delimiter)
        company_id = self.env.company.id
        product_product_obj = self.env['product.product']

        for row in file_data.get('data', {}):
            for product_name in row:
                products.add(str(product_name).strip())

        product_variant_ids = product_product_obj.search([('name', 'in', list(products))])
        bom_dict = {product_variant_id.name: product_variant_id.id for product_variant_id in product_variant_ids}
        bom_dict = self.create_band_products(file_data,
                                             bom_dict)  # CREATING PRODUCTS AT RUNTIME WHICH ARE NOT IN DATABASE #

        component_product_qty = 1
        for row in file_data.get('data', {}):
            band_no = str(row.pop(3))

            if band_no != 'None' and band_no in bom_dict:
                model_no = row[0]
                if model_no != 'None' and model_no not in bom_dict:
                    import_logs += 'Product ' + '"' + model_no + '"' + ' is not Imported \n'
                file_components = {row[5]} if row[5] and row[5] != 'None' else set()
                product_tmpl_id = self.env['product.product'].browse(bom_dict[band_no]).product_tmpl_id
                bom_id, error = self.create_or_get_existing_bom(band_no, product_tmpl_id, company_id,
                                                                component_product_qty)
                if error:
                    _LOGGER.info(f"Exception {error} occurs, ROW: {row}")
                    continue
                bom_comp = set(bom_line_id.product_id.name for bom_line_id in bom_id.bom_line_ids)
                component_to_add = file_components - bom_comp
                for cta in component_to_add:
                    component = self.env['product.product'].browse(bom_dict.get(str(cta), False))
                    bom_line = f"""
                                        INSERT INTO
                                            mrp_bom_line
                                                ("bom_id", "company_id", "product_id", "product_tmpl_id",
                                                "product_uom_id", "product_qty")
                                            VALUES
                                                ({bom_id.id}, {company_id},{component.product_variant_id.id}, 
                                                {component.product_tmpl_id.id},
                                                {component.uom_id.id}, {component_product_qty})
                                        """
                    try:
                        self._cr.execute(bom_line)
                    except Exception as error:
                        _LOGGER.info(f"Exception {error} occurs, ROW: {row}")
                        continue

                self.env.cr.commit()
        if import_logs:
            values = {
                'name': 'Citizen',
                'type': 'server',
                'level': 'info',
                'dbname': self.env.cr.dbname,
                'message': import_logs,
                'func': 'function_name',
                'path': 'path',
                'line': '0',
            }
            self.env['ir.logging'].sudo().create(values)
        _LOGGER.info(f"End Process: {datetime.datetime.now()}")

    def import_caseparts(self):
        empty_cols, import_logs, products = ['Case No'], "", set()
        _LOGGER.info(f"Start Process: {datetime.datetime.now()}")
        file_data = self.read_file(empty_cols, self.csv_delimiter)
        company_id = self.env.company.id
        product_product_obj = self.env['product.product']
        cols = [0, 3, 5, 7, 8, 10]
        for row in file_data.get('data', {}):
            for index, product_name in enumerate(row):
                if index in cols:
                    products.add(str(product_name).strip())

        product_variant_ids = product_product_obj.search([('name', 'in', list(products))])
        bom_dict = {product_variant_id.name: product_variant_id.id for product_variant_id in product_variant_ids}
        bom_dict = self.create_caseparts_products(file_data,
                                                  bom_dict)  # CREATING PRODUCTS AT RUNTIME WHICH ARE NOT IN DATABASE #

        component_product_qty = 1
        for row in file_data.get('data', {}):
            case_no = str(row.pop(0))
            if case_no != 'None' and case_no in bom_dict:
                file_components = set(prod for prod in row if prod in bom_dict and prod != 'None')
                product_tmpl_id = self.env['product.product'].browse(bom_dict[case_no]).product_tmpl_id
                bom_id, error = self.create_or_get_existing_bom(case_no, product_tmpl_id, company_id,
                                                                component_product_qty)
                if error:
                    _LOGGER.info(f"Exception {error} occurs, ROW: {row}")
                    continue
                bom_comp = set(bom_line_id.product_id.name for bom_line_id in bom_id.bom_line_ids)
                component_to_add = file_components - bom_comp
                for cta in component_to_add:
                    component = self.env['product.product'].browse(bom_dict.get(str(cta), False))
                    bom_line = f"""
                                            INSERT INTO
                                                mrp_bom_line
                                                    ("bom_id", "company_id", "product_id", "product_tmpl_id",
                                                    "product_uom_id", "product_qty")
                                                VALUES
                                                    ({bom_id.id}, {company_id},{component.product_variant_id.id},
                                                    {component.product_tmpl_id.id},
                                                    {component.uom_id.id}, {component_product_qty})
                                            """
                    try:
                        self._cr.execute(bom_line)
                    except Exception as error:
                        _LOGGER.info(f"Exception {error} occurs, ROW: {row}")
                        continue

                self.env.cr.commit()
        if import_logs:
            values = {
                'name': 'Citizen',
                'type': 'server',
                'level': 'info',
                'dbname': self.env.cr.dbname,
                'message': import_logs,
                'func': 'function_name',
                'path': 'path',
                'line': '0',
            }
            self.env['ir.logging'].sudo().create(values)
        _LOGGER.info(f"End Process: {datetime.datetime.now()}")

        return True

    def import_caliber(self):
        empty_cols, import_logs, products = ['Caliber No'], "", set()
        _LOGGER.info(f"Start Process: {datetime.datetime.now()}")
        file_data = self.read_file(empty_cols, self.csv_delimiter)
        company_id = self.env.company.id
        product_product_obj = self.env['product.product']

        cols = [0, 3, 5]
        for row in file_data.get('data', {}):
            for index, product_name in enumerate(row):
                if index in cols:
                    products.add(str(product_name).strip())

        product_variant_ids = product_product_obj.search([('name', 'in', list(products))])
        bom_dict = {product_variant_id.name: product_variant_id.id for product_variant_id in product_variant_ids}
        bom_dict = self.create_caliber_products(file_data,
                                                bom_dict)  # CREATING PRODUCTS AT RUNTIME WHICH ARE NOT IN DATABASE #

        component_product_qty = 1
        for row in file_data.get('data', {}):
            caliber_no = str(row.pop(0))
            if caliber_no != 'None' and caliber_no in bom_dict:
                file_components = set(prod for prod in row if prod in bom_dict and prod != 'None')
                product_tmpl_id = self.env['product.product'].browse(bom_dict[caliber_no]).product_tmpl_id
                bom_id, error = self.create_or_get_existing_bom(caliber_no, product_tmpl_id, company_id,
                                                                component_product_qty)
                if error:
                    _LOGGER.info(f"Exception {error} occurs, ROW: {row}")
                    continue
                bom_comp = set(bom_line_id.product_id.name for bom_line_id in bom_id.bom_line_ids)
                component_to_add = file_components - bom_comp
                for cta in component_to_add:
                    component = self.env['product.product'].browse(bom_dict.get(str(cta), False))
                    bom_line = f"""
                                        INSERT INTO
                                            mrp_bom_line
                                                ("bom_id", "company_id", "product_id", "product_tmpl_id",
                                                "product_uom_id", "product_qty")
                                            VALUES
                                                ({bom_id.id}, {company_id},{component.product_variant_id.id},
                                                {component.product_tmpl_id.id},
                                                {component.uom_id.id}, {component_product_qty})
                                        """
                    try:
                        self._cr.execute(bom_line)
                    except Exception as error:
                        _LOGGER.info(f"Exception {error} occurs, ROW: {row}")
                        continue

                self.env.cr.commit()
        if import_logs:
            values = {
                'name': 'Citizen',
                'type': 'server',
                'level': 'info',
                'dbname': self.env.cr.dbname,
                'message': import_logs,
                'func': 'function_name',
                'path': 'path',
                'line': '0',
            }
            self.env['ir.logging'].sudo().create(values)
        _LOGGER.info(f"End Process: {datetime.datetime.now()}")

        return True

    def import_dial(self):
        empty_cols, import_logs, products = ['Dial No'], "", set()
        _LOGGER.info(f"Start Process: {datetime.datetime.now()}")
        file_data = self.read_file(empty_cols, self.csv_delimiter)
        company_id = self.env.company.id
        product_product_obj = self.env['product.product']
        for row in file_data.get('data', {}):
            for product_name in row:
                if row[6] == product_name:
                    products.add(str(product_name).strip())

        product_variant_ids = product_product_obj.search([('name', 'in', list(products))])
        bom_dict = {product_variant_id.name: product_variant_id.id for product_variant_id in product_variant_ids}
        bom_dict = self.create_dial_products(file_data,
                                             bom_dict)  # CREATING PRODUCTS AT RUNTIME WHICH ARE NOT IN DATABASE #

        component_product_qty = 1
        for row in file_data.get('data', {}):
            dial_no = str(row.pop(1))
            if dial_no != 'None' and dial_no in bom_dict:
                model_no = row[2]
                if model_no != 'None' and model_no not in bom_dict:
                    import_logs += 'Product ' + '"' + model_no + '"' + ' is not Imported \n'
                file_components = {row[5]} if row[5] and row[5] != 'None' else set()
                product_tmpl_id = self.env['product.product'].browse(bom_dict[dial_no]).product_tmpl_id
                bom_id, error = self.create_or_get_existing_bom(dial_no, product_tmpl_id, company_id,
                                                                component_product_qty)
                if error:
                    _LOGGER.info(f"Exception {error} occurs, ROW: {row}")
                    continue
                bom_comp = set(bom_line_id.product_id.name for bom_line_id in bom_id.bom_line_ids)
                component_to_add = file_components - bom_comp
                for cta in component_to_add:
                    component = self.env['product.product'].browse(bom_dict.get(str(cta), False))
                    bom_line = f"""
                                        INSERT INTO
                                            mrp_bom_line
                                                ("bom_id", "company_id", "product_id", "product_tmpl_id",
                                                "product_uom_id", "product_qty")
                                            VALUES
                                                ({bom_id.id}, {company_id},{component.product_variant_id.id},
                                                {component.product_tmpl_id.id},
                                                {component.uom_id.id}, {component_product_qty})
                                        """
                    try:
                        self._cr.execute(bom_line)
                    except Exception as error:
                        _LOGGER.info(f"Exception {error} occurs, ROW: {row}")
                        continue

                self.env.cr.commit()
        if import_logs:
            values = {
                'name': 'Citizen',
                'type': 'server',
                'level': 'info',
                'dbname': self.env.cr.dbname,
                'message': import_logs,
                'func': 'function_name',
                'path': 'path',
                'line': '0',
            }
            self.env['ir.logging'].sudo().create(values)
        _LOGGER.info(f"End Process: {datetime.datetime.now()}")

        return True

    def import_model_products(self):
        empty_cols, import_logs, products = ['Model No'], "", set()
        _LOGGER.info(f"Start Process: {datetime.datetime.now()}")
        file_data = self.read_file(empty_cols, self.csv_delimiter)
        company_id = self.env.company.id
        product_product_obj = self.env['product.product']

        for row in file_data.get('data', {}):
            for product_name in row:
                if row[2] == product_name:
                    products.add(str(product_name).strip())

        product_variant_ids = product_product_obj.search([('name', 'in', list(products))])
        bom_dict = {product_variant_id.name: product_variant_id.id for product_variant_id in product_variant_ids}
        bom_dict = self.create_model_products(file_data,
                                              bom_dict)  # CREATING PRODUCTS AT RUNTIME WHICH ARE NOT IN DATABASE #

        component_product_qty = 1
        for row in file_data.get('data', {}):
            model_no = str(row.pop(0))

            if model_no != 'None' and model_no in bom_dict:
                file_components = {row[1]} if row[1] and row[1] != 'None' else set()
                product_tmpl_id = self.env['product.product'].browse(bom_dict[model_no]).product_tmpl_id
                bom_id, error = self.create_or_get_existing_bom(model_no, product_tmpl_id, company_id,
                                                                component_product_qty)
                if error:
                    _LOGGER.info(f"Exception {error} occurs, ROW: {row}")
                    continue
                bom_comp = set(bom_line_id.product_id.name for bom_line_id in bom_id.bom_line_ids)
                component_to_add = file_components - bom_comp
                for cta in component_to_add:
                    component = self.env['product.product'].browse(bom_dict.get(str(cta), False))
                    bom_line = f"""
                                                INSERT INTO
                                                    mrp_bom_line
                                                        ("bom_id", "company_id", "product_id", "product_tmpl_id",
                                                        "product_uom_id", "product_qty")
                                                    VALUES
                                                        ({bom_id.id}, {company_id},{component.product_variant_id.id},
                                                        {component.product_tmpl_id.id},
                                                        {component.uom_id.id}, {component_product_qty})
                                                """
                    try:
                        self._cr.execute(bom_line)
                    except Exception as error:
                        _LOGGER.info(f"Exception {error} occurs, ROW: {row}")
                        continue

                self.env.cr.commit()
        if import_logs:
            values = {
                'name': 'Citizen',
                'type': 'server',
                'level': 'info',
                'dbname': self.env.cr.dbname,
                'message': import_logs,
                'func': 'function_name',
                'path': 'path',
                'line': '0',
            }
            self.env['ir.logging'].sudo().create(values)
        _LOGGER.info(f"End Process: {datetime.datetime.now()}")

        return True

    def import_casing(self):
        empty_cols, import_logs, products = ['Case No'], "", set()
        _LOGGER.info(f"Start Process: {datetime.datetime.now()}")
        file_data = self.read_file(empty_cols, self.csv_delimiter)
        company_id = self.env.company.id
        product_product_obj = self.env['product.product']

        for row in file_data.get('data', {}):
            for product_name in row:
                products.add(str(product_name).strip())

        product_variant_ids = product_product_obj.search([('name', 'in', list(products))])
        bom_dict = {product_variant_id.name: product_variant_id.id for product_variant_id in product_variant_ids}
        bom_dict = self.create_casing_products(file_data,
                                               bom_dict)  # CREATING PRODUCTS AT RUNTIME WHICH ARE NOT IN DATABASE #

        component_product_qty = 1
        for row in file_data.get('data', {}):
            case_no = str(row.pop(1))
            if case_no != 'None' and case_no in bom_dict:
                model_no = row[0]
                if model_no != 'None' and model_no not in bom_dict:
                    import_logs += 'Product ' + '"' + model_no + '"' + ' is not Imported \n'
                file_components = set(prod for prod in row if prod in bom_dict and prod != 'None')
                product_tmpl_id = self.env['product.product'].browse(bom_dict[case_no]).product_tmpl_id
                bom_id, error = self.create_or_get_existing_bom(case_no, product_tmpl_id, company_id,
                                                                component_product_qty)
                if error:
                    _LOGGER.info(f"Exception {error} occurs, ROW: {row}")
                    continue
                bom_comp = set(bom_line_id.product_id.name for bom_line_id in bom_id.bom_line_ids)
                component_to_add = file_components - bom_comp
                for cta in component_to_add:
                    component = self.env['product.product'].browse(bom_dict.get(str(cta), False))
                    bom_line = f"""
                                       INSERT INTO
                                           mrp_bom_line
                                               ("bom_id", "company_id", "product_id", "product_tmpl_id",
                                               "product_uom_id", "product_qty")
                                           VALUES
                                               ({bom_id.id}, {company_id},{component.product_variant_id.id}, 
                                               {component.product_tmpl_id.id},
                                               {component.uom_id.id}, {component_product_qty})
                                       """
                    try:
                        self._cr.execute(bom_line)
                    except Exception as error:
                        _LOGGER.info(f"Exception {error} occurs, ROW: {row}")
                        continue

                self.env.cr.commit()
        if import_logs:
            values = {
                'name': 'Citizen',
                'type': 'server',
                'level': 'info',
                'dbname': self.env.cr.dbname,
                'message': import_logs,
                'func': 'function_name',
                'path': 'path',
                'line': '0',
            }
            self.env['ir.logging'].sudo().create(values)
        _LOGGER.info(f"End Process: {datetime.datetime.now()}")

        return True

    def create_casing_products(self, file_data, bom_dict):
        """
            @Usage: This method is create the products if not found in the system and prepared the dict with
            key:value pair in which product name is the key and product id is the value and after create all
            products system will return that dict.
            :param file_data: CSV File Date, Type : Dict
            :param bom_dict: It contains the Product Name and product values (Key:Value), Type: Dict
            :return: bom_dict -> Dict
        """
        for row in file_data.get('data', {}):
            for product in row:
                if product not in bom_dict and product != 'None' and product != row[0]:
                    default_values_dict = self.get_default_field_values(product, row)
                    statement = self.prepare_product_statements(default_values_dict, product)
                    try:
                        self._cr.execute(statement)
                        product_id = str([r['id'] for r in self.env.cr.dictfetchall()])[1:-1]
                        bom_dict.update({product: int(product_id)})
                        self.env.cr.commit()

                    except Exception as error:
                        _LOGGER.info(f"Exception {error} occurs, ROW: {row}")
                        continue
        return bom_dict

    def create_caliber_products(self, file_data, bom_dict):
        """
            @Usage: This method is create the products if not found in the system and prepared the dict with
            key:value pair in which product name is the key and product id is the value and after create all
            products system will return that dict.
            :param file_data: CSV File Date, Type : Dict
            :param bom_dict: It contains the Product Name and product values (Key:Value), Type: Dict
            :return: bom_dict -> Dict
        """
        cols = [0, 3, 5]
        for row in file_data.get('data', {}):
            for index, product in enumerate(row):
                if index in cols:
                    if product not in bom_dict and product != 'None':
                        default_values_dict = self.get_default_field_values(product, row)
                        statement = self.prepare_product_statements(default_values_dict, product)
                        try:
                            self._cr.execute(statement)
                            product_id = str([r['id'] for r in self.env.cr.dictfetchall()])[1:-1]
                            bom_dict.update({product: int(product_id)})
                            self.env.cr.commit()

                        except Exception as error:
                            _LOGGER.info(f"Exception {error} occurs, ROW: {row}")
                            continue
        return bom_dict

    def create_band_products(self, file_data, bom_dict):
        """
            @Usage: This method is create the products if not found in the system and prepared the dict with
            key:value pair in which product name is the key and product id is the value and after create all
            products system will return that dict.
            :param file_data: CSV File Date, Type : Dict
            :param bom_dict: It contains the Product Name and product values (Key:Value), Type: Dict
            :return: bom_dict -> Dict
        """
        for row in file_data.get('data', {}):
            for product in row:
                if row[3] == product or row[6] == product:
                    if product not in bom_dict and product != 'None':
                        default_values_dict = self.get_default_field_values(product, row)
                        statement = self.prepare_product_statements(default_values_dict, product)
                        try:
                            self._cr.execute(statement)
                            product_id = str([r['id'] for r in self.env.cr.dictfetchall()])[1:-1]
                            bom_dict.update({product: int(product_id)})
                            self.env.cr.commit()

                        except Exception as error:
                            _LOGGER.info(f"Exception {error} occurs, ROW: {row}")
                            continue
        return bom_dict

    def create_dial_products(self, file_data, bom_dict):
        """
            @Usage: This method is create the products if not found in the system and prepared the dict with
            key:value pair in which product name is the key and product id is the value and after create all
            products system will return that dict.
            :param file_data: CSV File Date, Type : Dict
            :param bom_dict: It contains the Product Name and product values (Key:Value), Type: Dict
            :return: bom_dict -> Dict
        """
        for row in file_data.get('data', {}):
            for product in row:
                if row[1] == product or row[6] == product:
                    if product not in bom_dict and product != 'None':
                        default_values_dict = self.get_default_field_values(product, row)
                        statement = self.prepare_product_statements(default_values_dict, product)
                        try:
                            self._cr.execute(statement)
                            product_id = str([r['id'] for r in self.env.cr.dictfetchall()])[1:-1]
                            bom_dict.update({product: int(product_id)})
                            self.env.cr.commit()

                        except Exception as error:
                            _LOGGER.info(f"Exception {error} occurs, ROW: {row}")
                            continue
        return bom_dict

    def create_model_products(self, file_data, bom_dict):
        """
            @Usage: This method is create the products if not found in the system and prepared the dict with
            key:value pair in which product name is the key and product id is the value and after create all
            products system will return that dict.
            :param file_data: CSV File Date, Type : Dict
            :param bom_dict: It contains the Product Name and product values (Key:Value), Type: Dict
            :return: bom_dict -> Dict
        """
        for row in file_data.get('data', {}):
            for product in row:
                if row[0] == product or row[2] == product:
                    if product not in bom_dict and product != 'None':
                        default_values_dict = self.get_default_field_values(product, row)
                        statement = self.prepare_product_statements(default_values_dict, product)
                        try:
                            self._cr.execute(statement)
                            product_id = str([r['id'] for r in self.env.cr.dictfetchall()])[1:-1]
                            bom_dict.update({product: int(product_id)})
                            self.env.cr.commit()

                        except Exception as error:
                            _LOGGER.info(f"Exception {error} occurs, ROW: {row}")
                            continue
        return bom_dict

    def create_caseparts_products(self, file_data, bom_dict):
        """
            @Usage: This method is create the products if not found in the system and prepared the dict with
            key:value pair in which product name is the key and product id is the value and after create all
            products system will return that dict.
            :param file_data: CSV File Date, Type : Dict
            :param bom_dict: It contains the Product Name and product values (Key:Value), Type: Dict
            :return: bom_dict -> Dict
        """
        cols = [0, 3, 5, 7, 8, 10]
        for row in file_data.get('data', {}):
            for index, product in enumerate(row):
                if index in cols:
                    default_values_dict = self.get_default_field_values(product, row)
                    statement = self.prepare_product_statements(default_values_dict, product)
                    try:
                        self._cr.execute(statement)
                        product_id = str([r['id'] for r in self.env.cr.dictfetchall()])[1:-1]
                        bom_dict.update({product: int(product_id)})
                        self.env.cr.commit()

                    except Exception as error:
                        _LOGGER.info(f"Exception {error} occurs, ROW: {row}")
                        continue
        return bom_dict

    def prepare_product_statements(self, default_values_dict, product):
        """
        :param default_values_dict: return product.template() values in Dict
        :param product: Product from the CSV file, Type: String
        :return: dict
        """
        categ_id = self.env.ref('product.product_category_all').id
        uom_id = self.env.ref('uom.product_uom_unit').id
        buy_route_id = self.env.ref('purchase_stock.route_warehouse0_buy').id
        required_fields = self.get_required_fields()
        statement = f"""
                                    WITH first_insert AS
                                        (
                                            INSERT INTO
                                                product_template
                                                    (
                                                        name,categ_id,uom_id,uom_po_id,detailed_type,tracking,
                                                        type,active{required_fields['sale_ok_field']}{required_fields['purchase_ok_field']}
                                                        {required_fields['sale_line_field']}{required_fields['purchase_line_field']}
                                                        {required_fields['base_unit_count_field']}{default_values_dict['is_case_field']}
                                                        {default_values_dict['is_dial_field']}{default_values_dict['is_caliber_field']}
                                                        {default_values_dict['is_bracelet_field']}
                                                    )
                                            VALUES
                                                (
                                                    '{product}',{categ_id},{uom_id},{uom_id},'product','none',
                                                    'product',True{required_fields['sale_ok_value']}{required_fields['purchase_ok_value']}
                                                    {required_fields['sale_line_field_values']}{required_fields['purchase_line_field_values']}
                                                    {required_fields['base_unit_count_field_value']}{default_values_dict['is_case_value']}
                                                    {default_values_dict['is_dial_value']}{default_values_dict['is_caliber_value']}
                                                    {default_values_dict['is_bracelet_value']}
                                                )
                                            RETURNING id
                                        )
                                    ,second_insert AS
                                    (
                                    INSERT INTO
                                        product_product
                                            (product_tmpl_id,active{required_fields['base_unit_count_field']})
                                        VALUES
                                            ((select id from first_insert),True{required_fields['base_unit_count_field_value']})
                                        RETURNING id
                                    )
                                    INSERT INTO
                                        stock_route_product
                                            (product_id,route_id)
                                        VALUES
                                            ((select id from first_insert),{buy_route_id})
                                        RETURNING (select id from second_insert)
                                    """
        return statement

    def create_or_get_existing_bom(self, part_no, product_tmpl_id, company_id, component_product_qty=1):
        """
            @Usage: This method is search the existing bom based on case_no if found then it will return existing
            bom if bom is not existing then it will create a new one and return that new bom.
            Also it will return the error message if any exception occurs
            :param part_no: CSV File Parts type Number, Type: String
            :param product_tmpl_id: product.template()
            :param company_id: Company Id, Type: Int
            :param component_product_qty: Component Product Quantity, Type: Int
            :return: bom_id -> mrp.bom(), error -> Message (String)
        """
        bom_id = self.env['mrp.bom'].search([('product_tmpl_id', '=', part_no)])
        error = ""
        if bom_id:
            return bom_id, error
        bom = f"""
                    INSERT INTO
                        mrp_bom
                            ("company_id", "product_tmpl_id", "product_uom_id", "product_qty",
                            "ready_to_produce", "consumption", "active", "type")
                        VALUES
                            ({company_id},{product_tmpl_id.id}, {product_tmpl_id.uom_id.id}, {component_product_qty},
                            'all_available', 'warning', true, 'normal')
                        RETURNING id
                """
        try:
            self._cr.execute(bom)
            bom_id = bom_id.browse(int(str([r[0] for r in self.env.cr.fetchall()])[1:-1]))
        except Exception as error:
            return bom_id, error
        return bom_id, error

    def get_required_fields(self):
        product_product_obj = self.env['product.product']
        required_fields = {
            "base_unit_count_field": '',
            "sale_line_field": '',
            "purchase_line_field": '',
            "base_unit_count_field_value": '',
            "sale_line_field_values": '',
            "purchase_line_field_values": '',
            "purchase_ok_field": '',
            "purchase_ok_value": '',
            "sale_ok_field": '',
            "sale_ok_value": '',
        }
        if hasattr(product_product_obj, 'base_unit_count'):
            required_fields.update({
                "base_unit_count_field": ",base_unit_count",
                "base_unit_count_field_value": ',1'
            })
        if hasattr(product_product_obj, 'sale_line_warn'):
            required_fields.update({
                "sale_line_field": ", sale_line_warn",
                "sale_line_field_values": ", 'warning'"
            })
        if hasattr(product_product_obj, 'purchase_line_warn'):
            required_fields.update({
                "purchase_line_field": ", purchase_line_warn",
                "purchase_line_field_values": ", 'warning'"
            })
        if hasattr(product_product_obj, 'purchase_ok'):
            required_fields.update({
                "purchase_ok_field": ", purchase_ok",
                "purchase_ok_value": ', True'
            })
        if hasattr(product_product_obj, 'sale_ok'):
            required_fields.update({
                "sale_ok_field": ", sale_ok",
                "sale_ok_value": ', True'
            })

        return required_fields

    def get_default_field_values(self, product, row):
        product_product_obj = self.env['product.product']
        bom_type = self.bom_type
        default_values_dict = {
            "is_case_field": '',
            "is_case_value": '',
            "is_dial_field": '',
            "is_dial_value": '',
            "is_caliber_field": '',
            "is_caliber_value": '',
            "is_bracelet_field": '',
            "is_bracelet_value": '',
        }
        if bom_type == 'band' or bom_type == 'casing':
            if product == row[3] or product == row[1] and hasattr(product_product_obj, 'is_bracelet'):
                default_values_dict.update({
                    "is_bracelet_field": ", is_bracelet",
                    "is_bracelet_value": ', True'
                })
        elif bom_type == 'casing':
            if product == row[1] and hasattr(product_product_obj, 'is_case'):
                default_values_dict.update({
                    "is_case_field": ", is_case",
                    "is_case_value": ', True'
                })
        elif bom_type == "dial" or bom_type == 'casing':
            if product == row[1] or product == row[1] and hasattr(product_product_obj, 'is_dial'):
                default_values_dict.update({
                    "is_dial_field": ", is_dial",
                    "is_dial_value": ', True'
                })
        elif bom_type == "caliber" or bom_type == 'casing':
            if product == row[0] or product == row[1] and hasattr(product_product_obj, 'is_caliber'):
                default_values_dict.update({
                    "is_caliber_field": ", is_caliber",
                    "is_caliber_value": ', True'
                })

        return default_values_dict
