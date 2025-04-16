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
    premiere_valeur_id = df['id'].dropna().iloc[0] if not df['id'].dropna().empty else 0

    # Étape 2 : Remplir les NaN dans 'id' avec cette valeur
    df['id'] = df['id'].fillna(premiere_valeur_id)

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

    print(df)

    # Now display the DataFrame
    produits = {}

    for _, row in df.iterrows():
        product_id = row['id']
        if product_id not in produits:
            produit_data = {k: row[k] for k in df.columns if k not in [
                'attribute', 'value', 'price',
                'attribute_line_ids/product_template_value_ids/id',
                'Vendors/Vendor', 'Vendors/Vendor Product Name', 'Vendors/Vendor Product Code',
                'Vendors/Price', 'Vendors/Quantity', 'Vendors/Start Date',
                'Vendors/End Date', 'Vendors/Delivery Lead Time', "seller_ids/product_id/id",
                "seller_ids/currency_id/id",
            ]}
            produit_data['attributes'] = {}
            produit_data['vendors'] = []
            produits[product_id] = produit_data
        # Gestion des attributs
        attr_name = str(row.get('attribute', '')).strip()
        attr_value = str(row.get('value', '')).strip()
        attr_price = convertStrTofloat(row.get('price', 0.0))

        if attr_name and attr_value:
            if attr_name not in produits[product_id]['attributes']:
                produits[product_id]['attributes'][attr_name] = []

            produits[product_id]['attributes'][attr_name].append({
                'value': attr_value,
                'price': convertStrTofloat(attr_price)
            })

        # Gestion des vendors
        vendor_name = str(row.get('Vendors/Vendor', '')).strip()
        currency_id = str(row.get('seller_ids/currency_id/id', '')).strip()
        taxes_ids = str(row.get('supplier_taxes_id', '')).strip()
        if vendor_name:
            vendor_info = {
                'vendor_id': vendor_name,
                'product_id': str(row.get('seller_ids/product_id/id', '')).strip(),
                'product_name': str(row.get('Vendors/Vendor Product Name', '')).strip(),
                'product_code': str(row.get('Vendors/Vendor Product Code', '')).strip(),
                'price': convertStrTofloat(row.get('Vendors/Price', 0.0)),
                'qty': int(row.get('Vendors/Quantity', 0)),
                'start_date': parse_date(row.get('Vendors/Start Date', '')),
                'end_date': parse_date(row.get('Vendors/End Date', '')),
                'time_lead': int(row.get('Vendors/Delivery Lead Time', 0)),
                'currency_id': currency_id,
                'taxes_ids': taxes_ids,
            }
            produits[product_id]['vendors'].append(vendor_info)

    # Réorganiser les attributs dans le format demandé
    for produit in produits.values():
        formatted_attributes = []
        for attr_name, values in produit['attributes'].items():
            formatted_attributes.append({
                'attribute': {
                    'name': attr_name,
                    'value': values
                }
            })
        produit['attributes'] = formatted_attributes
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
    if isinstance(cleanSentence(val), bool):
        return bool(val)
    return False


def generateProductVals(self, vals):
    cat = str(vals.get('categ_id/id', '')).strip()
    category = select_categoryId(self, cat)
    is_published = getValueBool(cleanSentence(vals.get('Is Published', False)))
    available_in_pos = getValueBool(cleanSentence(vals.get('available_in_pos', False)))
    allow_out_of_stock_order = getValueBool(cleanSentence(vals.get('allow_out_of_stock_order', False)))
    showDelivryMessage = getValueBool(cleanSentence(vals.get('showDelivryMessage', False)))
    show_availability = getValueBool(cleanSentence(vals.get('show_availability', False)))
    quantity = convertStrTofloat(cleanSentence(vals.get('Quantity On Hand', False)))
    weight = convertStrTofloat(cleanSentence(vals.get('weight', False)))
    product_vals = {
        'name': vals.get('name', ''),
        'standard_price': vals.get('standard_price', 0),
        'list_price': vals.get('Sales Price', 0),
        'default_code': cleanSentence(vals.get('default_code', '')),
        'barcode': cleanSentence(vals.get('barcode', '')),
        'is_published': is_published,
        'x_product_website_url': cleanSentence(vals.get('x_product_website_url', '')),
        'x_condition': cleanSentence(vals.get('x_condition', '')),
        'x_CPU': cleanSentence(vals.get('x_CPU', '')),
        'x_': cleanSentence(vals.get('x_', '')),
        'x_GPU': cleanSentence(vals.get('x_GPU', '')),
        'x_sreen_size': cleanSentence(vals.get('x_sreen_size', '')),
        'x_ram': cleanSentence(vals.get('x_ram', '')),
        'manufacturer_id': cleanSentence(vals.get('manufacturer_id', '')),
        'x_hddtype': cleanSentence(vals.get('x_hddtype', '')),
        'x_kind': cleanSentence(vals.get('x_kind', '')),
        'dr_label_id': cleanSentence(vals.get('dr_label_id/id', '')),
        'image_url': cleanSentence(vals.get('image_url', '')),
        'description_sale': cleanSentence(vals.get('description_sale', '')),
        'available_in_pos': available_in_pos,
        'out_of_stock_message': vals.get('out_of_stock_message', ''),
        'allow_out_of_stock_order': allow_out_of_stock_order,
        'showDelivryMessage': showDelivryMessage,
        'messageDelivryTimeStock': vals.get('messageDelivryTimeStock', ''),
        'messageDelivryTimeRemoteStock': vals.get('messageDelivryTimeRemoteStock', ''),
        'seo_name': cleanSentence(vals.get('seo_name', '')),
        'website_meta_title': cleanSentence(vals.get('website_meta_title', '')),
        'quantity': quantity,
        'website_meta_keywords': cleanSentence(vals.get('website_meta_keywords', '')),
        'website_description': cleanSentence(vals.get('website_description', '')),
        'show_availability': show_availability,
        'weight': weight,
        'tracking': select_tracking_type(self, vals.get('tracking', '')),
        'categ_id': category,
        'pos_categ_id': select_pos_categoryId(self, vals.get('pos_categ_id/id', None)),
        'public_categ_ids': [(6, 0, selectElementDataBase(self, vals.get('public_categ_ids/id', None)))],
        'dr_product_offer_ids': [(6, 0, selectElementDataBase(self, vals.get('dr_product_offer_ids/id', None)))],
        'dr_product_tab_ids': [(6, 0, selectElementDataBase(self, vals.get('dr_product_tab_ids/id', None)))],
        'supplier_taxes_id': [(6, 0, selectElementDataBase(self, vals.get('supplier_taxes_id', None)))],
    }
    return product_vals
