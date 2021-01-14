import xlwt
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class PartnerXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, lines):

        couriers = self.env['courier.courier'].search(
            [('date', '=', data['date']),
             ('booking_level', '=', 'international_delivery'),
             ('receiver_id.country_id.name', '=', data['destination'])])
        print(couriers)

        sheet1 = workbook.add_worksheet("courier manifest(Arman)")
        data_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'})
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 2,
            'align': 'center',
            'valign': 'vcenter'})
        sheet1.set_column('D:F', 20)
        sheet1.set_column('B:B', 20)
        sheet1.set_column('A:A', 6)
        sheet1.set_column('C:C', 20)
        sheet1.set_column('J:J', 20)
        sheet1.set_column('K:K', 1)
        sheet1.set_column('L:N', 20)
        sheet1.set_default_row(25)
        sheet1.merge_range('A1:J1', 'COURIER MANIFEST/INV: ' + data['mawb_no'], merge_format)
        sheet1.merge_range('A2:C2', 'ORIGIN:', merge_format)
        sheet1.merge_range('D2:F2', 'MAWB NO.' + data['mawb_no'], merge_format)
        sheet1.merge_range('G2:J2', 'DESTINATION:' + data['destination'], merge_format)
        sheet1.merge_range('A3:C3', 'FLIGHT NO.:' + data['flight_number'], merge_format)
        sheet1.merge_range('D3:F3', 'ETD:' + data['etd'] + '  ETA:' + data['eta'], merge_format)
        sheet1.merge_range('G3:J3', 'DATE:' + data['date'], merge_format)
        sheet1.write('A4', 'ITEM', merge_format)
        sheet1.write('B4', 'HAWB', merge_format)
        sheet1.write('C4', 'REF. NO.', merge_format)
        sheet1.write('D4', 'SHIPPER', merge_format)
        sheet1.write('E4', 'CONSIGNEE', merge_format)
        sheet1.write('F4', 'DESCRIPTION', merge_format)
        sheet1.write('G4', 'QTY. (PC.)', merge_format)
        sheet1.write('H4', 'WT. (KG.)', merge_format)
        sheet1.write('I4', 'VALUE ($)', merge_format)
        sheet1.write('J4', 'DESTINATION', merge_format)
        sheet1.write('L4', 'CONTACT DETAIL', merge_format)
        sheet1.write('M4', 'AMOUNT (AED)', merge_format)
        sheet1.write('N4', 'MODE OF PAYMENT', merge_format)
        row = 4
        item = 1
        qty = 0
        weight = 0
        value = 0
        price = 0
        for courier in couriers:
            sheet1.write(row, 0, item, data_format)
            sheet1.write(row, 1, courier.number, data_format)
            sheet1.write(row, 2, '', data_format)
            sheet1.write(row, 3, courier.sender_id.name, data_format)
            sheet1.write(row, 4, courier.receiver_id.name, data_format)
            sheet1.write(row, 5, '', data_format)
            sheet1.write(row, 6, courier.no_of_pieces, data_format)
            sheet1.write(row, 7, courier.total_weight, data_format)
            sheet1.write(row, 8, courier.declared_value_inUSD, data_format)
            sheet1.write(row, 9, courier.receiver_id.country_id.name, data_format)
            sheet1.write(row, 11, courier.receiver_id.phone, data_format)
            sheet1.write(row, 12, courier.final_price, data_format)
            if courier.cod:
                sheet1.write(row, 13, 'COD', data_format)
            else:
                sheet1.write(row, 13, 'Prepaid', data_format)
            qty = qty + courier.no_of_pieces
            weight = weight + courier.total_weight
            value = value + courier.declared_value_inUSD
            price = price + courier.final_price
            item = item + 1
            row = row + 1

        sheet1.write(row, 5, 'Total', merge_format)
        sheet1.write(row, 6, qty, merge_format)
        sheet1.write(row, 7, weight, merge_format)
        sheet1.write(row, 8, value, merge_format)
        sheet1.write(row, 12, price, merge_format)

        sheet1.merge_range(row + 1, 0, row + 1, 2, 'ACTUAL WEIGHT:', merge_format)
        sheet1.write(row + 1, 3, 'VOL.WT:', merge_format)
        sheet1.write(row + 1, 4, 'TOTAL DOX:', merge_format)
        sheet1.merge_range(row + 1, 5, row + 1, 6, 'TOTAL NON DOX:', merge_format)
        sheet1.merge_range(row + 1, 7, row + 1, 9, 'TOTAL PCS:', merge_format)


PartnerXlsx('report.courier.courier.xlsx',
            'courier.courier')
