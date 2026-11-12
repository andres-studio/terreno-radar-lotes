import importlib.util, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('monitor',Path(__file__).resolve().parents[1]/'scripts/monitor.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class MonitorTests(unittest.TestCase):
 def test_no_change_does_not_invent_price_event(self):
  r={'price':100,'area':20};one=m.merge({},r,'2026-01-01');two=m.merge(one,r,'2026-01-02');self.assertEqual(len(two['history']),1);self.assertEqual(two['observed_at'],'2026-01-02')
 def test_area_change_is_preserved(self):
  one=m.merge({},{'price':100,'area':20},'a');two=m.merge(one,{'price':100,'area':25},'b');self.assertEqual(len(two['history']),2)
 def test_product_currency_not_assumed(self):
  p=m.Page();p.ld=[{'name':'Lote Jardín','offers':{'price':400}}];self.assertIsNone(m.structured(p,'Jardín','Antioquia'))
 def test_generic_page_price_not_extracted(self):
  with self.assertRaises(ValueError):m.extract('<p>Lotes Jardín Antioquia precio $100.000.000</p>',{'city':'Jardín','department':'Antioquia'})
 def test_wrong_municipality_not_admitted(self):
  p=m.Page();p.ld=[{'name':'Lote Andes','offers':{'price':400,'priceCurrency':'COP'}}];self.assertIsNone(m.structured(p,'Jardín','Antioquia'))
 def test_project_lower_bounds_are_not_comparable(self):
  r=m.extract('<p>Jardín áreas desde 1.890 m² y precios publicados desde $395 millones</p>',{'city':'Jardín','department':'Antioquia','parser':'monte-horeb','title':'Proyecto'});self.assertTrue(r['price_from']);self.assertEqual(r['price'],395000000);self.assertEqual(r['area'],1890)
 def test_sqm_unit_not_assumed(self):
  p=m.Page();p.ld=[{'name':'Lote Jardín','offers':{'price':400,'priceCurrency':'COP'},'landArea':{'value':2,'unitText':'ha'}}];self.assertIsNone(m.structured(p,'Jardín','Antioquia')['area'])
 def test_flags_missing_and_false_do_not_create_price_change(self):
  old={'id':'keep','history':[{'at':'old','price':100,'area':20,'price_from':False,'area_from':False}]}
  result=m.merge(old,{'price':100,'area':20},'new');self.assertEqual(len(result['history']),1);self.assertEqual(result['id'],'keep')
 def test_ciencuadras_land_area_parser(self):
  html='<p>Lote Jardín Antioquia</p><p>Valor de compra: $435,000,000</p><p>Área lote: 4123.0 m²</p>'
  result=m.extract(html,{'city':'Jardín','department':'Antioquia','parser':'ciencuadras','title':'Verdún'})
  self.assertEqual(result['price'],435000000);self.assertEqual(result['area'],4123)
 def test_espaciourbano_does_not_mix_related_prices(self):
  source={'city':'Jardín','department':'Antioquia','parser':'espaciourbano','title':'Urbano','url':'https://www.emisasoluciones.com/Ficha.asp?xId=1629339'}
  text='<p>Jardín Código 1629339 EN VENTA $340,000,000 Area total 121 M2.</p><p>Destacado $900,000,000</p>'
  r=m.extract(text,source);self.assertEqual(r['price'],340000000);self.assertEqual(r['area'],121)
  with self.assertRaises(ValueError):m.extract(text.replace('Código 1629339','Código 1234'),source)
if __name__=='__main__':unittest.main()
