import re
from typing import List, Dict, Any, Optional

def normalize_price(val: Any) -> float:
    """Safely converts string/number price to float."""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    try:
        clean = str(val).replace('€', '').replace(',', '.').strip()
        return float(clean)
    except (ValueError, TypeError):
        return 0.0

def calculate_ingredient_cost(
    quantity: float, 
    recipe_unit: str, 
    unit_price: float, 
    price_um: str = "Kg"
) -> float:
    """
    Calculates the exact cost of an ingredient based on recipe quantity, recipe unit, 
    and catalog price unit (Kg, L, Pz, etc.).
    """
    q = float(quantity)
    p = float(unit_price)
    
    r_unit = recipe_unit.lower().strip()
    p_unit = price_um.lower().strip()
    
    # Weight conversions (Base: Kg)
    if p_unit in ["kg", "chilo", "chilogrammo"]:
        if r_unit in ["g", "gr", "grammo", "grammi"]:
            return (q / 1000.0) * p
        elif r_unit in ["kg", "chilo", "chilogrammo"]:
            return q * p
        elif r_unit in ["etto", "etti", "hg"]:
            return (q / 10.0) * p
        elif r_unit in ["mg"]:
            return (q / 1000000.0) * p
            
    # Volume conversions (Base: Litro)
    elif p_unit in ["l", "lt", "litro", "litri"]:
        if r_unit in ["ml", "millilitri", "millilitro", "cc"]:
            return (q / 1000.0) * p
        elif r_unit in ["cl", "centilitri"]:
            return (q / 100.0) * p
        elif r_unit in ["l", "lt", "litro", "litri"]:
            return q * p
            
    # Piece / Packaging / Portion conversions (Base: Pz, Crt, Cnf)
    elif p_unit in ["pz", "pezzo", "pezzi", "porz", "porzione", "cnf", "crt", "vaschetta"]:
        if r_unit in ["pz", "pezzo", "pezzi", "porz", "porzione", "fetta", "fette"]:
            return q * p
        elif r_unit in ["g", "gr"] and q > 0:
            # If price is per piece but quantity in grams, assume 1 piece unless specified
            return p
            
    # Default direct multiplication
    return q * p

def calculate_recipe_summary(
    ingredients: List[Dict[str, Any]], 
    target_food_cost_pct: float = 28.0,
    actual_selling_price_gross: Optional[float] = None,
    vat_rate: float = 10.0,
    portions: int = 1
) -> Dict[str, Any]:
    """
    Calculates comprehensive financial and culinary metrics for a recipe.
    """
    portions = max(1, int(portions))
    total_recipe_cost = 0.0
    items_breakdown = []
    
    for item in ingredients:
        qty = float(item.get("quantity", 0.0))
        r_unit = str(item.get("unit", "g"))
        unit_price = normalize_price(item.get("unit_price", 0.0))
        price_um = str(item.get("price_um", "Kg"))
        
        cost = calculate_ingredient_cost(qty, r_unit, unit_price, price_um)
        total_recipe_cost += cost
        
        items_breakdown.append({
            "cod_art": item.get("cod_art", ""),
            "name": item.get("name", "Ingrediente"),
            "quantity": qty,
            "unit": r_unit,
            "unit_price": unit_price,
            "price_um": price_um,
            "cost": cost,
            "cost_pct": 0.0 # Will be populated below
        })
        
    # Populate cost % per ingredient
    for item in items_breakdown:
        if total_recipe_cost > 0:
            item["cost_pct"] = (item["cost"] / total_recipe_cost) * 100.0
            
    food_cost_per_portion = total_recipe_cost / portions
    
    # Target Food Cost Calculations
    target_pct = max(1.0, float(target_food_cost_pct))
    recommended_selling_price_net = (food_cost_per_portion / (target_pct / 100.0)) if target_pct > 0 else 0.0
    recommended_selling_price_gross = recommended_selling_price_net * (1.0 + (vat_rate / 100.0))
    
    # Actual Selling Price Analysis
    if actual_selling_price_gross is not None and actual_selling_price_gross > 0:
        actual_gross = float(actual_selling_price_gross)
        actual_net = actual_gross / (1.0 + (vat_rate / 100.0))
        actual_food_cost_pct = (food_cost_per_portion / actual_net) * 100.0 if actual_net > 0 else 0.0
        gross_margin_per_portion = actual_net - food_cost_per_portion
    else:
        actual_gross = recommended_selling_price_gross
        actual_net = recommended_selling_price_net
        actual_food_cost_pct = target_pct
        gross_margin_per_portion = recommended_selling_price_net - food_cost_per_portion
        
    # Efficiency Assessment Status
    if actual_food_cost_pct <= 28.0:
        status = "ottimo"
        status_label = "🟢 Food Cost Ottimo (Margine Elevato)"
        status_color = "#15803D"
    elif actual_food_cost_pct <= 34.0:
        status = "equilibrato"
        status_label = "🟡 Food Cost Equilibrato (Standard Ho.Re.Ca)"
        status_color = "#D97706"
    else:
        status = "critico"
        status_label = "🔴 Food Cost Critico (Incidenza Costi Alta)"
        status_color = "#DC2626"
        
    return {
        "portions": portions,
        "total_recipe_cost": total_recipe_cost,
        "food_cost_per_portion": food_cost_per_portion,
        "target_food_cost_pct": target_pct,
        "recommended_selling_price_net": recommended_selling_price_net,
        "recommended_selling_price_gross": recommended_selling_price_gross,
        "actual_selling_price_net": actual_net,
        "actual_selling_price_gross": actual_gross,
        "actual_food_cost_pct": actual_food_cost_pct,
        "gross_margin_per_portion": gross_margin_per_portion,
        "vat_rate": vat_rate,
        "status": status,
        "status_label": status_label,
        "status_color": status_color,
        "items_breakdown": items_breakdown
    }

# Pre-loaded Template Recipes strictly verified with real items from Italian Food Trading catalog
RECIPE_TEMPLATES = {
    "🍕 Pizza Margherita Tradizionale": {
        "name": "Pizza Margherita Classica",
        "category": "Pizzeria",
        "portions": 1,
        "target_pct": 25.0,
        "actual_price": 7.50,
        "ingredients": [
            {
                "cod_art": "A110414QU",
                "name": "FARINA DI GRANO TENERO 00 W250 Qualitaly",
                "quantity": 180,
                "unit": "g",
                "unit_price": 1.07,
                "price_um": "Kg"
            },
            {
                "cod_art": "A140212",
                "name": "POLPA DI POMODORO FINE 3/1 gr.2500 marchio IFT",
                "quantity": 90,
                "unit": "g",
                "unit_price": 1.83,
                "price_um": "Kg"
            },
            {
                "cod_art": "A060451",
                "name": "MOZZARELLA FIORDILATTE JULIENNE VASCH. 2,5 KG marchio Qualitaly",
                "quantity": 110,
                "unit": "g",
                "unit_price": 7.01,
                "price_um": "Kg"
            },
            {
                "cod_art": "A120813",
                "name": "OLIO EXTRA VERGINE BOTT.VETRO LT.1 marchio Tavola Viva",
                "quantity": 10,
                "unit": "ml",
                "unit_price": 7.26,
                "price_um": "L"
            }
        ]
    },
    "🌟 Pizza Gourmet Orazio alla Brace & Burrata": {
        "name": "Pizza Gourmet con Prosciutto Orazio alla Brace e Burrata",
        "category": "Pizzeria Gourmet",
        "portions": 1,
        "target_pct": 28.0,
        "actual_price": 13.50,
        "ingredients": [
            {
                "cod_art": "A110413QU",
                "name": "FARINA DI GRANO TENERO 00 W350 Qualitaly",
                "quantity": 180,
                "unit": "g",
                "unit_price": 1.21,
                "price_um": "Kg"
            },
            {
                "cod_art": "A140212",
                "name": "POLPA DI POMODORO FINE 3/1 gr.2500 marchio IFT",
                "quantity": 80,
                "unit": "g",
                "unit_price": 1.83,
                "price_um": "Kg"
            },
            {
                "cod_art": "A060451",
                "name": "MOZZARELLA FIORDILATTE JULIENNE VASCH. 2,5 KG marchio Qualitaly",
                "quantity": 80,
                "unit": "g",
                "unit_price": 7.01,
                "price_um": "Kg"
            },
            {
                "cod_art": "A050922",
                "name": "PROSC.COTTO 'ORAZIO' A.Q. ALLA BRACE - CML",
                "quantity": 70,
                "unit": "g",
                "unit_price": 11.19,
                "price_um": "Kg"
            },
            {
                "cod_art": "A080895",
                "name": "BURRATA GR.100 SECCHIELLO SABELLI",
                "quantity": 1,
                "unit": "Pz",
                "unit_price": 1.75,
                "price_um": "Pz"
            },
            {
                "cod_art": "A120813",
                "name": "OLIO EXTRA VERGINE BOTT.VETRO LT.1 marchio Tavola Viva",
                "quantity": 10,
                "unit": "ml",
                "unit_price": 7.26,
                "price_um": "L"
            }
        ]
    },
    "🥩 Tagliata di Roast-Beef Grass Fed con Grana Padano": {
        "name": "Tagliata di Roast-Beef Grass Fed Argentina",
        "category": "Secondi Piatti",
        "portions": 1,
        "target_pct": 32.0,
        "actual_price": 22.00,
        "ingredients": [
            {
                "cod_art": "A001012",
                "name": "ROAST-BEEF BOVINO FRESCO GRASS FED ARGENTINA S/V",
                "quantity": 250,
                "unit": "g",
                "unit_price": 25.98,
                "price_um": "Kg"
            },
            {
                "cod_art": "A061198",
                "name": "GRANA PADANO SCAGLIE KG.1 SACCO ZP",
                "quantity": 30,
                "unit": "g",
                "unit_price": 20.70,
                "price_um": "Kg"
            },
            {
                "cod_art": "A120813",
                "name": "OLIO EXTRA VERGINE BOTT.VETRO LT.1 marchio Tavola Viva",
                "quantity": 15,
                "unit": "ml",
                "unit_price": 7.26,
                "price_um": "L"
            }
        ]
    },
    "🧀 Tagliere Degustazione Eccellenze IFT (4 Persone)": {
        "name": "Gran Tagliere Degustazione Salumi & Formaggi",
        "category": "Antipasti & Taglieri",
        "portions": 4,
        "target_pct": 30.0,
        "actual_price": 32.00,
        "ingredients": [
            {
                "cod_art": "A050922",
                "name": "PROSC.COTTO 'ORAZIO' A.Q. ALLA BRACE - CML",
                "quantity": 120,
                "unit": "g",
                "unit_price": 11.19,
                "price_um": "Kg"
            },
            {
                "cod_art": "A050302",
                "name": "PROSC.CRUDO NAZIONALE 7+ DISOSSATO/PRESSATO SOAVE 14/16 MESI",
                "quantity": 120,
                "unit": "g",
                "unit_price": 18.60,
                "price_um": "Kg"
            },
            {
                "cod_art": "A061132",
                "name": "GRANA PADANO DOP RISERVA 1/8 STAG. OLTRE 20 MESI ZP",
                "quantity": 160,
                "unit": "g",
                "unit_price": 19.72,
                "price_um": "Kg"
            },
            {
                "cod_art": "A080895",
                "name": "BURRATA GR.100 SECCHIELLO SABELLI",
                "quantity": 2,
                "unit": "Pz",
                "unit_price": 1.75,
                "price_um": "Pz"
            },
            {
                "cod_art": "A120813",
                "name": "OLIO EXTRA VERGINE BOTT.VETRO LT.1 marchio Tavola Viva",
                "quantity": 20,
                "unit": "ml",
                "unit_price": 7.26,
                "price_um": "L"
            }
        ]
    }
}
