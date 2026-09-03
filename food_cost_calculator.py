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

# Pre-loaded Template Recipes with real items from Italian Food Trading catalog
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
                "name": "Farina 00 W250 Qualitaly (Impasto/Pallina)",
                "quantity": 180,
                "unit": "g",
                "unit_price": 1.15,
                "price_um": "Kg"
            },
            {
                "cod_art": "A010101",
                "name": "Polpa di Pomodoro Fine per Pizza",
                "quantity": 90,
                "unit": "g",
                "unit_price": 1.45,
                "price_um": "Kg"
            },
            {
                "cod_art": "A060101",
                "name": "Mozzarella Fiordilatte Julienne",
                "quantity": 110,
                "unit": "g",
                "unit_price": 6.80,
                "price_um": "Kg"
            },
            {
                "cod_art": "A120101",
                "name": "Olio Extra Vergine di Oliva 100% Italiano",
                "quantity": 10,
                "unit": "ml",
                "unit_price": 9.50,
                "price_um": "L"
            },
            {
                "cod_art": "EXTRA",
                "name": "Basilico fresco, lievito, sale & cottura forno",
                "quantity": 1,
                "unit": "Pz",
                "unit_price": 0.25,
                "price_um": "Pz"
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
                "name": "Farina 00 W350 Qualitaly (Lievitazione 48h)",
                "quantity": 180,
                "unit": "g",
                "unit_price": 1.21,
                "price_um": "Kg"
            },
            {
                "cod_art": "A010101",
                "name": "Polpa Pomodoro San Marzano DOP",
                "quantity": 80,
                "unit": "g",
                "unit_price": 2.10,
                "price_um": "Kg"
            },
            {
                "cod_art": "A060101",
                "name": "Mozzarella Fiordilatte in cottura",
                "quantity": 80,
                "unit": "g",
                "unit_price": 6.80,
                "price_um": "Kg"
            },
            {
                "cod_art": "A050922",
                "name": "PROSC.COTTO 'ORAZIO' A.Q. ALLA BRACE COATI",
                "quantity": 70,
                "unit": "g",
                "unit_price": 7.50,
                "price_um": "Kg"
            },
            {
                "cod_art": "A060401",
                "name": "Burrata Pugliese Cuore Morbido 100g",
                "quantity": 1,
                "unit": "Pz",
                "unit_price": 1.40,
                "price_um": "Pz"
            },
            {
                "cod_art": "A120101",
                "name": "Olio EVO & Granella di Nocciole Tostate",
                "quantity": 15,
                "unit": "g",
                "unit_price": 12.00,
                "price_um": "Kg"
            }
        ]
    },
    "🥩 Tagliata di Roast-Beef Grass Fed con Rucola e Grana": {
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
                "cod_art": "A070101",
                "name": "Rucola selvatica fresca",
                "quantity": 35,
                "unit": "g",
                "unit_price": 5.50,
                "price_um": "Kg"
            },
            {
                "cod_art": "A060201",
                "name": "Grana Padano DOP Riserva in Scaglie",
                "quantity": 30,
                "unit": "g",
                "unit_price": 14.80,
                "price_um": "Kg"
            },
            {
                "cod_art": "A120101",
                "name": "Olio Extra Vergine di Oliva & Glassa Balsamica",
                "quantity": 20,
                "unit": "ml",
                "unit_price": 11.00,
                "price_um": "L"
            },
            {
                "cod_art": "EXTRA",
                "name": "Sale Maldon in fiocchi e pane d'accompagnamento",
                "quantity": 1,
                "unit": "Pz",
                "unit_price": 0.40,
                "price_um": "Pz"
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
                "name": "Prosciutto Cotto Orazio alla Brace",
                "quantity": 120,
                "unit": "g",
                "unit_price": 7.50,
                "price_um": "Kg"
            },
            {
                "cod_art": "A050101",
                "name": "Prosciutto Crudo di Parma DOP 24 Mesi",
                "quantity": 120,
                "unit": "g",
                "unit_price": 19.50,
                "price_um": "Kg"
            },
            {
                "cod_art": "A060201",
                "name": "Grana Padano DOP Riserva & Pecorino Toscano",
                "quantity": 160,
                "unit": "g",
                "unit_price": 15.20,
                "price_um": "Kg"
            },
            {
                "cod_art": "A060401",
                "name": "Burratina Pugliese 100g",
                "quantity": 2,
                "unit": "Pz",
                "unit_price": 1.40,
                "price_um": "Pz"
            },
            {
                "cod_art": "A100101",
                "name": "Focaccia ligure all'olio & Mostarda di frutta",
                "quantity": 1,
                "unit": "Pz",
                "unit_price": 1.50,
                "price_um": "Pz"
            }
        ]
    }
}
