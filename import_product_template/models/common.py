import base64
import pandas as pd
import io
from datetime import datetime


def cleanSentence(name):
    result = str(name).replace('.0', '')
    return result


def convertStrTofloat(name):
    if isinstance(name, float) or isinstance(name, int):
        return float(name)
    return 0


def parse_date(value):
    """Essaye de parser la date au format datetime.date ou retourne une string vide."""
    if isinstance(value, datetime):
        return value.date().isoformat()
    try:
        return pd.to_datetime(value, dayfirst=True).date().isoformat()
    except Exception:
        return ''


def convertXlsOrCsvToDicts(file):
    fichier_decoded = base64.b64decode(file)
    fichier_io = io.BytesIO(fichier_decoded)
    try:
        df = pd.read_excel(fichier_io)
    except Exception:
        try:
            fichier_io.seek(0)
            df = pd.read_csv(fichier_io, sep=',')
        except Exception as e:
            raise ValueError(f"Impossible de lire le fichier fourni : {str(e)}")
    premiere_valeur_id = df['ID'].dropna().iloc[0] if not df['ID'].dropna().empty else 0

    # Étape 2 : Remplir les NaN dans 'id' avec cette valeur
    df['ID'] = df['ID'].fillna(premiere_valeur_id)

    # Étape 3 : Remplacer les autres NaN (dans les autres colonnes) par 0
    colonnes_autres = df.columns.difference(['id'])
    df[colonnes_autres] = df[colonnes_autres].fillna('')

    # df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    # df.columns = [str(col).strip() for col in df.columns]
    # df.fillna(method='ffill', inplace=True)

    pd.set_option('display.max_rows', None)  # Show all rows
    pd.set_option('display.max_columns', None)  # Show all columns
    pd.set_option('display.width', None)  # Auto-detect terminal width
    pd.set_option('display.max_colwidth', None)  # Show full column content


    # Now display the DataFrame
    produits = {}

    for _, row in df.iterrows():
        # print(f'\n\n row {row} \n\n')
        product_id = row['ID']
        if product_id not in produits:
            produit_data = {k: row[k] for k in df.columns if k not in [
                'Attributes', 'Value', 'Price',
                'Vendor', 'Vendor Product Name', 'Vendor Product Code',
                'Vendors/Price', 'Vendors/Quantity', 'Vendors/Start Date',
                'Vendors/End Date', 'Delivery Lead Time', "Product Variant",
                "Vendors Currency",
            ]}
            produit_data['Attributes'] = {}
            produit_data['Vendor'] = []
            produits[product_id] = produit_data
        # Gestion des attributs
        attr_name = str(row.get('Attributes', '')).strip()
        attr_value = str(row.get('Value', '')).strip()
        attr_price = convertStrTofloat(row.get('Price', 0.0))

        if attr_name and attr_value:
            if attr_name not in produits[product_id]['Attributes']:
                produits[product_id]['Attributes'][attr_name] = []

            produits[product_id]['Attributes'][attr_name].append({
                'value': attr_value,
                'price': convertStrTofloat(attr_price)
            })
        # Gestion des vendors
        vendor_name = cleanSentence(row.get('Vendor', '')).strip()
        currency_id = cleanSentence(row.get('Vendors Currency', '')).strip()
        taxes_ids = cleanSentence(row.get('Vendor Taxes', '')).strip()
        if vendor_name:
            vendor_info = {
                'vendor_id': vendor_name,
                'product_id': cleanSentence(row.get('Product Variant', '')).strip(),
                'product_name': cleanSentence(row.get('Vendor Product Name', '')).strip(),
                'product_code': cleanSentence(row.get('Vendor Product Code', '')).strip(),
                'price': convertStrTofloat(row.get('Vendors/Price', 0.0)),
                'qty': convertStrTofloat(row.get('Vendors/Quantity', 0)),
                'start_date': parse_date(row.get('Vendors/Start Date', '')),
                'end_date': parse_date(row.get('Vendors/End Date', '')),
                'time_lead': convertStrTofloat(row.get('Delivery Lead Time', 0)),
                'currency_id': currency_id,
                'taxes_ids': taxes_ids,
            }
            produits[product_id]['Vendor'].append(vendor_info)
    # Réorganiser les attributs dans le format demandé
    for produit in produits.values():
        formatted_attributes = []
        for attr_name, values in produit['Attributes'].items():
            formatted_attributes.append({
                'attribute': {
                    'name': attr_name,
                    'value': values
                }
            })
        produit['Attributes'] = formatted_attributes

    return list(produits.values())


def parse_date(value):
    """Essaye de parser la date au format datetime.date ou retourne une string vide."""

    if isinstance(value, datetime):
        return value.date().isoformat()
    try:
        return pd.to_datetime(value, dayfirst=True).date().isoformat()
    except Exception:
        return ''


def select_detailed_type(self, name):
    if 'Consumable' == name:
        return 'consu'
    elif 'Service' == name:
        return 'service'
    else:
        return 'product'


def select_tracking_type(self, name):
    if 'By Unique Serial Number' == name:
        return 'serial'
    elif 'By Lots' == name:
        return 'lot'
    else:
        return 'none'

def select_tracking_type_with_key(name):
    if 'serial' == name:
        return 'By Unique Serial Number'
    elif 'lot' == name:
        return 'By Lots'
    else:
        return 'No Tracking'

def generateNewRow():
    result = []
    for i in range(0, 42):
        result.append('')
    return result

def generateNewRowAttribute():
    result = []
    for i in range(0, 52):
        result.append('')
    return result


def select_categoryId(self, categ_id):
    res = 1
    categ_id = str(categ_id).strip()
    try:
        res = self.env.ref(categ_id)
        res = res.id
    except Exception as e:
        return res
    return res


def select_pos_categoryId(self, categ_id):
    res = None
    categ_id = str(categ_id).strip()
    try:
        res = self.env.ref(categ_id)
        res = res.id
    except Exception as e:
        return None
    return res


def select_categoryIds(self, categ_ids):
    result = []
    for categ_id in categ_ids:
        try:
            categ_id = self.env.ref(categ_id)
            if not categ_id: continue
            result.append(categ_id.id)
        except Exception as e:
            continue
    return result


def selectElementDataBase(self, item_ids):
    result = []
    item_ids = str(item_ids).split(',')
    for item_id in item_ids:
        item_id = str(item_id).strip()
        try:
            item = self.env.ref(item_id)
            result.append(item.id)
        except Exception as e:
            continue
    return result


def selectOneElementDataBase(self, item_id):
    res = None
    try:
        res = self.env.ref(item_id)
    except Exception as e:
        return None
    return res


def getValueBool(val):
    val = cleanSentence(val)
    val = val.strip().upper()
    if val == 'TRUE':
        return True
    else: return False

    if isinstance(cleanSentence(val), bool):
        return bool(val)
    return False


def generateProductVals(self, vals):
    cat = str(vals.get('Inventory Categ', '')).strip()
    category = select_categoryId(self, cat)
    is_published = getValueBool(cleanSentence(vals.get('Is Published', False)))
    available_in_pos = getValueBool(cleanSentence(vals.get('Available in POS T/F', False)))
    allow_out_of_stock_order = getValueBool(cleanSentence(vals.get('Out of Stock T/F', False)))
    showDelivryMessage = getValueBool(cleanSentence(vals.get('Dis/Hide Dliv Mes T/F', False)))
    show_availability = getValueBool(cleanSentence(vals.get('Show Avil Qty T/F', False)))
    # quantity = convertStrTofloat(cleanSentence(vals.get('Quantity On Hand', False)))
    weight = convertStrTofloat(cleanSentence(vals.get('Weight', False)))
    product_vals = {
        'name': vals.get('Name', ''),
        'standard_price': vals.get('Cost', 0),
        'list_price': vals.get('Sales Price', 0),
        'default_code': cleanSentence(vals.get('SKU', '')),
        'barcode': cleanSentence(vals.get('Barcode', '')),
        'is_published': is_published,
        'x_product_website_url': cleanSentence(vals.get('Website URL Bz', '')),
        'x_condition': cleanSentence(vals.get('Condition Bz', '')),
        'x_CPU': cleanSentence(vals.get('CPU Bz', '')),
        'x_': cleanSentence(vals.get('Rubric Bz', '')),
        'x_GPU': cleanSentence(vals.get('GPU Bz', '')),
        'x_sreen_size': cleanSentence(vals.get('Sreen Size Bz', '')),
        'x_ram': cleanSentence(vals.get('RAM Bz', '')),
        'manufacturer_id_int': cleanSentence(vals.get('manufacturer_id', 0)),
        'x_hddtype': cleanSentence(vals.get('Hard Drive Type Bz', '')),
        'x_kind': cleanSentence(vals.get('Hard Drive Type Bz', '')),
        'dr_label_id': cleanSentence(vals.get('Label', '')),
        'image_url': cleanSentence(vals.get('Image URL', '')),
        'description_sale': cleanSentence(vals.get('Sale Description', '')),
        'available_in_pos': available_in_pos,
        'out_of_stock_message': vals.get('Out of Stock Message', ''),
        'allow_out_of_stock_order': allow_out_of_stock_order,
        'showDelivryMessage': showDelivryMessage,
        'messageDelivryTimeStock': vals.get('Stock Message', ''),
        'messageDelivryTimeRemoteStock': vals.get('Remote Stock Message', ''),
        'seo_name': cleanSentence(vals.get('SEO Name', '')),
        'website_meta_title': cleanSentence(vals.get('Meta Title', '')),
        'website_meta_description': cleanSentence(vals.get('Meta Description', '')),
        # 'quantity': 0,
        'website_meta_keywords': cleanSentence(vals.get('Meta Keywords', '')),
        'website_description': cleanSentence(vals.get('Website Description html', '')),
        'show_availability': show_availability,
        'weight': weight,
        'tracking': select_tracking_type(self, vals.get('Tracking', '')),
        'categ_id': category,
        'pos_categ_id': select_pos_categoryId(self, vals.get('POS Categ', None)),
        'public_categ_ids': [(6, 0, selectElementDataBase(self, vals.get('Website Categ', None)))],
        'dr_product_offer_ids': [(6, 0, selectElementDataBase(self, vals.get('Offers', None)))],
        'dr_product_tab_ids': [(6, 0, selectElementDataBase(self, vals.get('Tabs', None)))],
        'supplier_taxes_id': [(6, 0, selectElementDataBase(self, vals.get('Vendor Taxes', None)))],
    }
    return product_vals


def generateExportId(el):
    try:
        el.export_data(['ID'])
        xml_id = el.export_data(['ID']).get('datas')[0][0]
        xml_id = el.get_metadata()[0].get('xmlid')
        return xml_id
    except Exception: return None


def prepareVlasProduct(rec):
    print(f'\n\n Rec {rec} \n\n')
    vals = {}
    vals['is_published'] = rec.get('Is Published', False)
    vals['name'] = rec.get('Name', '')
    vals['detailed_type'] = rec.get('Product Type', 'product')
    vals['standard_price'] = rec.get('Cost', 0)
    vals['list_price'] = rec.get('Sales Price', 0)

    return vals