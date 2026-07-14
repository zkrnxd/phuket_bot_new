import pandas as pd
import re
from typing import List, Dict

class DataLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = {}
        self.load_all()
    
    def load_all(self):
        """Загружает все листы Excel"""
        try:
            xl = pd.ExcelFile(self.file_path)
            for sheet_name in xl.sheet_names:
                self.data[sheet_name] = pd.read_excel(self.file_path, sheet_name=sheet_name)
            self._clean_prices()
            self._create_indexes()
            print(f"✅ Загружено {len(self.data)} листов")
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
    
    def _clean_prices(self):
        """Очищает цены от символов"""
        projects = self.data.get("Projects")
        if projects is not None and "Цена от" in projects.columns:
            def clean_price(val):
                if pd.isna(val):
                    return None
                if isinstance(val, (int, float)):
                    return float(val)
                val = str(val)
                cleaned = re.sub(r'[^\d.]', '', val)
                try:
                    if 'млн' in val.lower():
                        return float(cleaned) * 1000000
                    return float(cleaned)
                except:
                    return None
            projects["Цена_очищ"] = projects["Цена от"].apply(clean_price)
    
    def _create_indexes(self):
        """Создает индексы для быстрого поиска"""
        projects = self.data.get("Projects")
        if projects is not None:
            self.by_district = {}
            self.by_type = {}
            self.by_developer = {}
            
            for _, row in projects.iterrows():
                district = row.get("Район")
                if pd.notna(district):
                    if district not in self.by_district:
                        self.by_district[district] = []
                    self.by_district[district].append(row)
                
                typ = row.get("Тип")
                if pd.notna(typ):
                    if typ not in self.by_type:
                        self.by_type[typ] = []
                    self.by_type[typ].append(row)
                
                dev = row.get("Застройщик")
                if pd.notna(dev):
                    if dev not in self.by_developer:
                        self.by_developer[dev] = []
                    self.by_developer[dev].append(row)
    
    def get_projects_by_district(self, district: str) -> List[Dict]:
        result = self.by_district.get(district, [])
        return sorted(result, key=lambda x: x.get("Цена_очищ", 0) or 0)
    
    def get_projects_by_type(self, typ: str) -> List[Dict]:
        result = self.by_type.get(typ, [])
        return sorted(result, key=lambda x: x.get("Цена_очищ", 0) or 0)
    
    def get_projects_by_developer(self, dev: str) -> List[Dict]:
        result = self.by_developer.get(dev, [])
        return sorted(result, key=lambda x: x.get("Цена_очищ", 0) or 0)
    
    def get_projects_by_price(self, min_price: float, max_price: float) -> List[Dict]:
        projects = self.data.get("Projects")
        if projects is None:
            return []
        result = []
        for _, row in projects.iterrows():
            price = row.get("Цена_очищ")
            if pd.isna(price):
                continue
            if min_price <= price <= max_price:
                result.append(row)
        return sorted(result, key=lambda x: x.get("Цена_очищ", 0))
    
    def get_projects_by_school(self, school_col: str, max_distance: float = 3.0) -> List[Dict]:
        projects = self.data.get("Projects")
        if projects is None:
            return []
        result = []
        for _, row in projects.iterrows():
            dist = row.get(school_col)
            if pd.isna(dist):
                continue
            try:
                if float(dist) <= max_distance:
                    result.append(row)
            except:
                continue
        return result
    
    def get_projects_by_beach(self, max_distance: int = 1000) -> List[Dict]:
        projects = self.data.get("Projects")
        if projects is None:
            return []
        result = []
        for _, row in projects.iterrows():
            dist = row.get("До моря,м")
            if pd.isna(dist):
                continue
            try:
                if float(dist) <= max_distance:
                    result.append(row)
            except:
                continue
        return sorted(result, key=lambda x: float(x.get("До моря,м", 9999)) if pd.notna(x.get("До моря,м")) else 9999)
    
    def get_districts(self) -> List[str]:
        districts = self.data.get("Districts")
        if districts is None:
            return []
        return districts["Район"].dropna().tolist()
    
    def get_beaches(self) -> List[Dict]:
        beaches = self.data.get("Beaches")
        if beaches is None:
            return []
        return beaches.to_dict('records')
    
    def get_schools(self) -> List[Dict]:
        schools = self.data.get("Schools")
        if schools is None:
            return []
        return schools.to_dict('records')
    
    def get_developers(self) -> List[Dict]:
        devs = self.data.get("Developers")
        if devs is None:
            return []
        return devs.to_dict('records')
    
    def get_kindergartens(self) -> List[Dict]:
        kg = self.data.get("Kindergartens")
        if kg is None:
            return []
        return kg.to_dict('records')
    
    def get_hospitals(self) -> List[Dict]:
        hospitals = self.data.get("Hospitals")
        if hospitals is None:
            return []
        return hospitals.to_dict('records')
    
    def get_visas(self) -> List[Dict]:
        visas = self.data.get("Visas")
        if visas is None:
            return []
        return visas.to_dict('records')
    
    def get_taxes(self) -> List[Dict]:
        taxes = self.data.get("Taxes")
        if taxes is None:
            return []
        return taxes.to_dict('records')
    
    def get_countries(self) -> List[Dict]:
        countries = self.data.get("Countries")
        if countries is None:
            return []
        return countries.to_dict('records')
    
    def get_rental_yield(self, district: str = None) -> List[Dict]:
        rental = self.data.get("Rental_Yield")
        if rental is None:
            return []
        if district:
            rows = rental[rental["Район"] == district]
            if not rows.empty:
                return rows.iloc[0].to_dict()
        return rental.to_dict('records')