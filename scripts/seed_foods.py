"""Seed the Foods table with ~200 curated French staples.

Usage:
    python scripts/seed_foods.py

Requires AIRTABLE_PAT in the environment (loaded from .env if present).
Adds only foods whose name isn't already in the table — re-running is safe.
"""

import os
import sys
from pathlib import Path

# add repo root to path so `from calo...` works when run from anywhere
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from pyairtable import Api

from calo.airtable_ids import BASE_ID, FOODS_FIELDS, FOODS_TABLE

load_dotenv()


# Curated French food list — values per 100g (kcal, protein g, carbs g, fat g,
# fiber g, standard portion g). Sourced from CIQUAL / Open Food Facts averages.
# Format: (name, category, kcal, protein, carbs, fat, fiber, portion)
FOODS: list[tuple[str, str, int, float, float, float, float, int]] = [
    # --- viandes ---
    ("Bœuf bourguignon", "viande", 178, 14.0, 8.0, 9.0, 1.0, 200),
    ("Steak de bœuf grillé", "viande", 250, 26.0, 0.0, 16.0, 0.0, 150),
    ("Faux-filet grillé", "viande", 232, 28.0, 0.0, 13.0, 0.0, 150),
    ("Côte de bœuf grillée", "viande", 290, 25.0, 0.0, 21.0, 0.0, 250),
    ("Steak haché 15% MG cuit", "viande", 225, 25.0, 0.0, 14.0, 0.0, 125),
    ("Bavette grillée", "viande", 217, 28.0, 0.0, 12.0, 0.0, 150),
    ("Côte d'agneau grillée", "viande", 280, 25.0, 0.0, 20.0, 0.0, 130),
    ("Gigot d'agneau rôti", "viande", 240, 28.0, 0.0, 14.0, 0.0, 150),
    ("Filet mignon de porc rôti", "viande", 170, 27.0, 0.0, 7.0, 0.0, 150),
    ("Côte de porc grillée", "viande", 220, 26.0, 0.0, 13.0, 0.0, 150),
    ("Escalope de veau grillée", "viande", 165, 30.0, 0.0, 5.0, 0.0, 150),
    ("Cuisse de poulet rôtie", "viande", 184, 24.0, 0.0, 10.0, 0.0, 180),
    ("Aile de poulet grillée", "viande", 200, 23.0, 0.0, 12.0, 0.0, 100),
    ("Escalope de dinde grillée", "viande", 135, 30.0, 0.0, 1.5, 0.0, 150),
    ("Magret de canard cuit", "viande", 220, 28.0, 0.0, 12.0, 0.0, 150),
    ("Confit de canard cuisse", "viande", 290, 27.0, 0.0, 21.0, 0.0, 180),
    ("Lapin rôti", "viande", 156, 28.0, 0.0, 5.0, 0.0, 150),
    ("Foie de veau poêlé", "viande", 165, 22.0, 4.0, 7.0, 0.0, 100),
    # --- poissons ---
    ("Cabillaud cuit", "poisson", 88, 20.0, 0.0, 0.7, 0.0, 130),
    ("Colin cuit", "poisson", 95, 21.0, 0.0, 1.0, 0.0, 130),
    ("Lieu noir cuit", "poisson", 100, 22.0, 0.0, 1.0, 0.0, 130),
    ("Sole cuite", "poisson", 90, 19.0, 0.0, 1.5, 0.0, 130),
    ("Daurade cuite", "poisson", 130, 22.0, 0.0, 5.0, 0.0, 150),
    ("Bar cuit", "poisson", 110, 22.0, 0.0, 2.5, 0.0, 150),
    ("Truite cuite", "poisson", 168, 22.0, 0.0, 9.0, 0.0, 130),
    ("Saumon fumé", "poisson", 195, 24.0, 0.0, 11.0, 0.0, 60),
    ("Sardines à l'huile", "poisson", 230, 25.0, 0.0, 14.0, 0.0, 90),
    ("Sardines à la tomate", "poisson", 165, 18.0, 5.0, 8.0, 1.0, 90),
    ("Maquereau cuit", "poisson", 230, 22.0, 0.0, 16.0, 0.0, 130),
    ("Hareng fumé", "poisson", 215, 19.0, 0.0, 15.0, 0.0, 70),
    ("Anchois à l'huile", "poisson", 200, 28.0, 0.0, 10.0, 0.0, 30),
    ("Crevettes cuites", "poisson", 100, 21.0, 1.0, 1.5, 0.0, 120),
    ("Moules cuites", "poisson", 100, 17.0, 7.0, 2.5, 0.0, 250),
    ("Coquilles Saint-Jacques", "poisson", 90, 17.0, 4.0, 1.0, 0.0, 100),
    ("Calamars cuits", "poisson", 95, 18.0, 4.0, 1.5, 0.0, 100),
    ("Surimi", "poisson", 95, 11.0, 12.0, 0.5, 0.0, 100),
    # --- œufs ---
    ("Œuf au plat", "œuf", 200, 13.0, 1.0, 16.0, 0.0, 60),
    ("Œuf brouillé au beurre", "œuf", 200, 13.0, 1.5, 15.0, 0.0, 100),
    ("Omelette nature", "œuf", 170, 13.0, 1.0, 13.0, 0.0, 150),
    ("Œuf à la coque", "œuf", 145, 13.0, 1.0, 10.0, 0.0, 60),
    ("Œuf dur", "œuf", 155, 13.0, 1.0, 11.0, 0.0, 60),
    # --- laitiers / fromages ---
    ("Yaourt grec entier", "laitier", 110, 6.0, 4.0, 7.0, 0.0, 150),
    ("Yaourt grec 0%", "laitier", 60, 10.0, 4.0, 0.4, 0.0, 150),
    ("Skyr nature", "laitier", 65, 11.0, 4.0, 0.2, 0.0, 150),
    ("Petit suisse 0%", "laitier", 50, 9.0, 4.0, 0.1, 0.0, 60),
    ("Petit suisse 40% MG", "laitier", 165, 9.0, 4.0, 12.0, 0.0, 60),
    ("Fromage blanc 20% MG", "laitier", 80, 8.0, 4.0, 3.5, 0.0, 100),
    ("Crème fraîche épaisse 30%", "laitier", 290, 2.0, 3.0, 30.0, 0.0, 30),
    ("Crème fraîche allégée 15%", "laitier", 160, 3.0, 4.0, 15.0, 0.0, 30),
    ("Mozzarella di Bufala", "fromage", 260, 18.0, 1.0, 21.0, 0.0, 50),
    ("Burrata", "fromage", 320, 17.0, 2.0, 28.0, 0.0, 80),
    ("Feta", "fromage", 265, 14.0, 4.0, 21.0, 0.0, 30),
    ("Chèvre frais", "fromage", 215, 16.0, 2.0, 16.0, 0.0, 30),
    ("Chèvre sec", "fromage", 360, 27.0, 1.0, 28.0, 0.0, 30),
    ("Brie", "fromage", 330, 20.0, 0.5, 28.0, 0.0, 30),
    ("Camembert", "fromage", 300, 20.0, 0.5, 24.0, 0.0, 30),
    ("Roquefort", "fromage", 370, 22.0, 1.0, 31.0, 0.0, 30),
    ("Bleu d'Auvergne", "fromage", 340, 21.0, 0.5, 28.0, 0.0, 30),
    ("Parmesan", "fromage", 400, 36.0, 0.0, 28.0, 0.0, 20),
    ("Reblochon", "fromage", 340, 20.0, 0.5, 29.0, 0.0, 30),
    ("Raclette", "fromage", 370, 23.0, 0.5, 30.0, 0.0, 150),
    ("Tomme de Savoie", "fromage", 330, 23.0, 0.5, 27.0, 0.0, 30),
    ("Mimolette", "fromage", 380, 25.0, 0.5, 31.0, 0.0, 30),
    ("Ricotta", "fromage", 175, 11.0, 3.0, 13.0, 0.0, 50),
    # --- légumes ---
    ("Épinards cuits", "légume", 25, 3.0, 3.0, 0.3, 2.5, 150),
    ("Courgette cuite", "légume", 20, 1.4, 2.5, 0.3, 1.1, 150),
    ("Aubergine cuite", "légume", 35, 1.0, 6.0, 0.2, 3.0, 150),
    ("Poivron rouge cuit", "légume", 30, 1.0, 6.0, 0.4, 2.0, 150),
    ("Endive crue", "légume", 17, 1.0, 3.0, 0.1, 3.1, 100),
    ("Fenouil cuit", "légume", 27, 1.0, 6.0, 0.2, 3.0, 150),
    ("Asperge cuite", "légume", 22, 2.4, 4.0, 0.2, 2.0, 150),
    ("Artichaut cuit", "légume", 47, 3.3, 11.0, 0.2, 5.4, 200),
    ("Champignons de Paris cuits", "légume", 28, 3.0, 3.4, 0.5, 1.0, 100),
    ("Cèpes cuits", "légume", 31, 3.2, 3.5, 0.6, 5.0, 100),
    ("Choux de Bruxelles cuits", "légume", 36, 3.0, 7.0, 0.5, 2.6, 150),
    ("Chou-fleur cuit", "légume", 24, 2.0, 4.0, 0.5, 2.0, 150),
    ("Chou rouge cuit", "légume", 31, 1.4, 7.4, 0.2, 2.0, 150),
    ("Haricots verts cuits", "légume", 25, 1.8, 5.0, 0.2, 2.7, 150),
    ("Haricots beurre cuits", "légume", 25, 1.5, 5.0, 0.2, 2.0, 150),
    ("Petits pois cuits", "légume", 80, 5.0, 12.0, 0.5, 5.5, 150),
    ("Maïs en boîte", "légume", 90, 3.0, 17.0, 1.0, 2.4, 100),
    ("Betterave cuite", "légume", 44, 1.5, 9.0, 0.2, 2.8, 100),
    ("Radis cru", "légume", 18, 1.0, 3.0, 0.1, 1.6, 80),
    ("Concombre cru", "légume", 15, 0.7, 2.7, 0.1, 0.5, 100),
    ("Poireau cuit", "légume", 30, 1.5, 6.0, 0.3, 2.5, 150),
    ("Oignon cru", "légume", 40, 1.1, 9.0, 0.1, 1.7, 50),
    ("Échalote crue", "légume", 75, 2.5, 17.0, 0.1, 3.2, 30),
    ("Ail cru", "légume", 150, 6.4, 33.0, 0.5, 2.1, 5),
    ("Ratatouille", "plat composé", 50, 1.0, 6.0, 2.5, 2.0, 250),
    # --- fruits ---
    ("Fraise", "fruit", 32, 0.7, 7.0, 0.3, 2.0, 150),
    ("Framboise", "fruit", 52, 1.2, 12.0, 0.7, 6.5, 100),
    ("Myrtille", "fruit", 57, 0.7, 14.0, 0.3, 2.4, 100),
    ("Mûre", "fruit", 43, 1.4, 10.0, 0.5, 5.3, 100),
    ("Cassis", "fruit", 63, 1.4, 15.0, 0.4, 4.3, 100),
    ("Cerise", "fruit", 63, 1.0, 15.0, 0.2, 2.1, 150),
    ("Pêche", "fruit", 39, 0.9, 9.5, 0.3, 1.5, 150),
    ("Nectarine", "fruit", 44, 1.1, 11.0, 0.3, 1.7, 150),
    ("Abricot", "fruit", 48, 1.4, 11.0, 0.4, 2.0, 60),
    ("Prune", "fruit", 46, 0.7, 11.4, 0.3, 1.4, 60),
    ("Raisin", "fruit", 69, 0.7, 18.0, 0.2, 0.9, 150),
    ("Poire", "fruit", 57, 0.4, 15.0, 0.1, 3.1, 150),
    ("Orange", "fruit", 47, 0.9, 12.0, 0.1, 2.4, 150),
    ("Mandarine", "fruit", 53, 0.8, 13.0, 0.3, 1.8, 80),
    ("Clémentine", "fruit", 47, 0.9, 12.0, 0.2, 1.7, 80),
    ("Pamplemousse", "fruit", 42, 0.8, 11.0, 0.1, 1.6, 150),
    ("Citron", "fruit", 29, 1.1, 9.0, 0.3, 2.8, 50),
    ("Kiwi", "fruit", 61, 1.1, 15.0, 0.5, 3.0, 100),
    ("Mangue", "fruit", 60, 0.8, 15.0, 0.4, 1.6, 150),
    ("Ananas", "fruit", 50, 0.5, 13.0, 0.1, 1.4, 150),
    ("Papaye", "fruit", 43, 0.5, 11.0, 0.3, 1.7, 150),
    ("Grenade", "fruit", 83, 1.7, 19.0, 1.2, 4.0, 100),
    ("Melon", "fruit", 34, 0.8, 8.0, 0.2, 0.9, 200),
    ("Pastèque", "fruit", 30, 0.6, 8.0, 0.2, 0.4, 200),
    ("Figue fraîche", "fruit", 74, 0.8, 19.0, 0.3, 2.9, 80),
    ("Pruneau sec", "fruit", 240, 2.2, 64.0, 0.4, 7.1, 30),
    ("Datte sèche", "fruit", 282, 2.4, 75.0, 0.4, 8.0, 25),
    ("Raisin sec", "fruit", 299, 3.1, 79.0, 0.5, 3.7, 30),
    ("Noix de coco fraîche", "fruit", 354, 3.3, 15.0, 33.0, 9.0, 30),
    # --- féculents / céréales ---
    ("Couscous cuit", "féculent", 112, 3.8, 23.0, 0.2, 1.4, 200),
    ("Boulgour cuit", "féculent", 83, 3.1, 18.0, 0.2, 4.5, 200),
    ("Quinoa cuit", "féculent", 120, 4.4, 21.0, 1.9, 2.8, 200),
    ("Polenta cuite", "féculent", 70, 2.0, 14.0, 0.5, 1.0, 250),
    ("Sarrasin cuit", "féculent", 90, 3.4, 19.0, 0.6, 2.7, 200),
    ("Riz complet cuit", "féculent", 130, 2.7, 27.0, 1.0, 1.8, 150),
    ("Riz basmati cuit", "féculent", 135, 3.0, 28.0, 0.5, 0.6, 150),
    ("Lentilles cuites", "féculent", 116, 9.0, 20.0, 0.4, 8.0, 200),
    ("Lentilles corail cuites", "féculent", 130, 9.0, 22.0, 0.4, 8.0, 200),
    ("Pois chiches cuits", "féculent", 165, 9.0, 27.0, 2.6, 8.0, 200),
    ("Haricots rouges cuits", "féculent", 130, 8.7, 22.0, 0.5, 6.4, 200),
    ("Haricots blancs cuits", "féculent", 120, 8.0, 20.0, 0.6, 6.0, 200),
    ("Pois cassés cuits", "féculent", 115, 8.0, 20.0, 0.4, 8.0, 200),
    ("Patate douce cuite", "féculent", 90, 1.6, 21.0, 0.1, 3.3, 200),
    ("Avoine cuite", "féculent", 71, 2.5, 12.0, 1.5, 1.7, 250),
    ("Semoule de blé cuite", "féculent", 110, 4.0, 23.0, 0.4, 1.5, 200),
    # --- pains / viennoiseries ---
    ("Baguette tradition", "féculent", 270, 9.0, 56.0, 1.0, 3.0, 80),
    ("Pain de mie", "féculent", 280, 8.5, 50.0, 4.5, 3.0, 60),
    ("Pain aux céréales", "féculent", 255, 10.0, 43.0, 4.0, 7.0, 50),
    ("Pain au seigle", "féculent", 230, 8.0, 45.0, 1.3, 7.0, 50),
    ("Croissant beurre", "snack", 415, 8.0, 45.0, 22.0, 2.0, 60),
    ("Pain au chocolat", "snack", 430, 8.0, 47.0, 23.0, 2.0, 70),
    ("Brioche", "snack", 365, 8.0, 53.0, 13.0, 1.5, 50),
    ("Pain perdu", "snack", 220, 6.0, 27.0, 9.0, 1.0, 80),
    ("Biscotte", "féculent", 380, 11.0, 75.0, 4.0, 4.0, 8),
    ("Tartine pain beurre confiture", "snack", 305, 5.0, 47.0, 11.0, 2.0, 60),
    # --- charcuterie ---
    ("Jambon blanc cuit", "viande", 110, 20.0, 0.5, 3.0, 0.0, 40),
    ("Jambon de Bayonne", "viande", 250, 28.0, 0.5, 15.0, 0.0, 30),
    ("Saucisson sec", "viande", 410, 26.0, 1.5, 33.0, 0.0, 30),
    ("Chorizo", "viande", 420, 24.0, 2.0, 35.0, 0.0, 30),
    ("Rillettes", "viande", 460, 18.0, 0.5, 43.0, 0.0, 30),
    ("Pâté de campagne", "viande", 320, 14.0, 4.0, 28.0, 1.0, 40),
    ("Mortadelle", "viande", 320, 14.0, 3.0, 28.0, 0.0, 30),
    ("Lardons", "viande", 350, 14.0, 0.5, 33.0, 0.0, 50),
    ("Andouillette", "viande", 270, 16.0, 1.0, 22.0, 0.0, 150),
    ("Boudin noir", "viande", 380, 14.0, 5.0, 35.0, 0.0, 130),
    # --- plats français ---
    ("Cassoulet", "plat composé", 175, 9.5, 16.0, 8.0, 5.0, 300),
    ("Blanquette de veau", "plat composé", 130, 12.0, 5.0, 7.0, 0.5, 300),
    ("Bœuf bourguignon (plat)", "plat composé", 185, 16.0, 7.0, 10.0, 1.0, 300),
    ("Quiche lorraine", "plat composé", 280, 9.0, 18.0, 19.0, 1.0, 150),
    ("Gratin dauphinois", "plat composé", 130, 3.0, 13.0, 7.5, 1.5, 200),
    ("Hachis Parmentier", "plat composé", 130, 7.0, 12.0, 5.5, 1.5, 300),
    ("Coq au vin", "plat composé", 150, 18.0, 4.0, 7.0, 0.5, 300),
    ("Pot-au-feu", "plat composé", 120, 12.0, 6.0, 5.0, 1.5, 350),
    ("Choucroute garnie", "plat composé", 180, 9.0, 8.0, 13.0, 3.0, 400),
    ("Tartiflette", "plat composé", 200, 8.0, 15.0, 13.0, 1.5, 300),
    ("Salade Niçoise", "plat composé", 130, 8.0, 7.0, 8.0, 2.0, 350),
    ("Salade César", "plat composé", 165, 7.0, 6.0, 13.0, 1.5, 300),
    ("Tarte aux pommes", "snack", 240, 3.0, 36.0, 10.0, 2.0, 120),
    ("Crème brûlée", "snack", 290, 5.0, 22.0, 21.0, 0.0, 130),
    ("Mousse au chocolat", "snack", 270, 5.0, 28.0, 16.0, 1.5, 100),
    # --- restau / take away ---
    ("Pizza margherita", "plat composé", 250, 11.0, 30.0, 10.0, 2.0, 300),
    ("Pizza 4 fromages", "plat composé", 290, 13.0, 28.0, 14.0, 2.0, 300),
    ("Pizza pepperoni", "plat composé", 290, 12.0, 28.0, 14.0, 2.0, 300),
    ("Sandwich jambon-beurre", "plat composé", 290, 11.0, 35.0, 11.0, 2.0, 200),
    ("Sandwich poulet crudités", "plat composé", 220, 11.0, 28.0, 7.0, 2.0, 250),
    ("Kebab (sandwich)", "plat composé", 280, 13.0, 28.0, 12.0, 2.0, 350),
    ("Burger classique", "plat composé", 290, 14.0, 25.0, 14.0, 2.0, 250),
    ("Cheeseburger", "plat composé", 310, 15.0, 25.0, 16.0, 2.0, 250),
    ("Frites", "féculent", 312, 3.5, 41.0, 15.0, 3.5, 150),
    ("Wrap poulet", "plat composé", 230, 11.0, 26.0, 9.0, 2.0, 250),
    ("Sushi (6 pièces moyennes)", "plat composé", 150, 6.0, 28.0, 1.5, 1.5, 150),
    ("Maki saumon (6 pièces)", "plat composé", 145, 6.0, 27.0, 1.0, 1.0, 120),
    ("Nem au poulet", "snack", 220, 9.0, 22.0, 11.0, 1.5, 50),
    ("Rouleau de printemps", "plat composé", 100, 5.0, 15.0, 2.0, 2.0, 100),
    ("Ramen", "plat composé", 130, 7.0, 18.0, 4.0, 1.5, 500),
    ("Pad thai poulet", "plat composé", 180, 9.0, 22.0, 6.0, 2.0, 350),
    # --- snacks / sucré ---
    ("Chocolat au lait", "snack", 535, 7.5, 58.0, 31.0, 2.0, 25),
    ("Chocolat blanc", "snack", 540, 6.0, 60.0, 31.0, 0.0, 25),
    ("Biscuit type Petit Beurre", "snack", 425, 7.0, 75.0, 11.0, 2.0, 25),
    ("Cookie chocolat", "snack", 470, 5.0, 60.0, 22.0, 2.0, 30),
    ("Madeleine", "snack", 420, 6.0, 50.0, 22.0, 1.0, 25),
    ("Éclair au chocolat", "snack", 250, 5.0, 32.0, 12.0, 1.0, 80),
    ("Religieuse", "snack", 280, 6.0, 30.0, 16.0, 1.0, 80),
    ("Tarte au citron", "snack", 290, 4.0, 38.0, 13.0, 1.0, 120),
    ("Mille-feuille", "snack", 350, 4.0, 38.0, 20.0, 1.0, 100),
    ("Glace vanille", "snack", 200, 3.5, 24.0, 10.0, 0.5, 100),
    ("Sorbet citron", "snack", 110, 0.5, 27.0, 0.1, 0.5, 100),
    ("Miel", "autre", 304, 0.3, 82.0, 0.0, 0.2, 20),
    ("Confiture de fraises", "autre", 250, 0.5, 60.0, 0.1, 1.0, 20),
    ("Pâte à tartiner chocolat noisette", "autre", 540, 6.0, 57.0, 31.0, 4.0, 20),
    ("Sucre blanc", "autre", 400, 0.0, 100.0, 0.0, 0.0, 5),
    # --- boissons ---
    ("Café noir", "boisson", 2, 0.1, 0.0, 0.0, 0.0, 100),
    ("Café au lait", "boisson", 50, 2.5, 5.0, 2.0, 0.0, 200),
    ("Cappuccino", "boisson", 60, 3.0, 6.0, 2.5, 0.0, 200),
    ("Thé sans sucre", "boisson", 1, 0.0, 0.0, 0.0, 0.0, 250),
    ("Jus d'orange pressé", "boisson", 45, 0.7, 10.5, 0.2, 0.3, 200),
    ("Jus de pomme", "boisson", 46, 0.1, 11.0, 0.1, 0.2, 200),
    ("Smoothie fruits rouges", "boisson", 60, 1.0, 14.0, 0.3, 1.5, 250),
    ("Coca-Cola", "boisson", 42, 0.0, 10.6, 0.0, 0.0, 330),
    ("Coca Zéro", "boisson", 0, 0.0, 0.0, 0.0, 0.0, 330),
    ("Limonade", "boisson", 40, 0.0, 10.0, 0.0, 0.0, 330),
    ("Bière blonde 5°", "boisson", 43, 0.5, 3.7, 0.0, 0.0, 250),
    ("Bière IPA 6°", "boisson", 55, 0.5, 4.5, 0.0, 0.0, 330),
    ("Vin rouge 12°", "boisson", 83, 0.1, 2.5, 0.0, 0.0, 120),
    ("Vin blanc 12°", "boisson", 82, 0.1, 2.6, 0.0, 0.0, 120),
    ("Champagne", "boisson", 80, 0.3, 2.0, 0.0, 0.0, 100),
    ("Spritz", "boisson", 85, 0.0, 8.0, 0.0, 0.0, 200),
    ("Mojito", "boisson", 130, 0.0, 18.0, 0.0, 0.0, 200),
    ("Whisky sec", "boisson", 240, 0.0, 0.0, 0.0, 0.0, 40),
    # --- petit-déj / divers ---
    ("Granola maison", "féculent", 460, 11.0, 60.0, 20.0, 7.0, 50),
    ("Muesli sans sucre", "féculent", 360, 11.0, 65.0, 6.0, 9.0, 50),
    ("Corn Flakes nature", "féculent", 360, 7.0, 85.0, 0.5, 3.0, 30),
    ("Porridge avoine au lait", "plat composé", 95, 4.0, 14.0, 2.5, 1.7, 250),
    ("Pancake", "snack", 230, 6.0, 35.0, 7.0, 1.5, 80),
    ("Crêpe nature", "snack", 215, 6.0, 32.0, 7.0, 1.0, 80),
    ("Beurre de cacahuète", "autre", 590, 25.0, 18.0, 50.0, 7.0, 20),
    ("Houmous", "autre", 230, 8.0, 13.0, 15.0, 5.0, 50),
    ("Tapenade olives", "autre", 290, 2.0, 5.0, 30.0, 5.0, 20),
    ("Sauce vinaigrette", "sauce", 450, 0.5, 5.0, 48.0, 0.0, 15),
    ("Mayonnaise", "sauce", 700, 1.0, 1.5, 75.0, 0.0, 15),
    ("Ketchup", "sauce", 105, 1.5, 25.0, 0.2, 1.0, 15),
    ("Moutarde", "sauce", 130, 6.0, 9.0, 8.0, 5.0, 10),
    ("Sauce soja", "sauce", 50, 8.0, 5.0, 0.1, 0.0, 15),
    ("Sauce tomate", "sauce", 50, 1.5, 9.0, 1.0, 1.5, 100),
    ("Pesto basilic", "sauce", 450, 4.0, 6.0, 47.0, 1.0, 20),
]


def main() -> int:
    pat = os.environ.get("AIRTABLE_PAT")
    if not pat:
        print("ERROR: AIRTABLE_PAT not set. Add it to your .env file.", file=sys.stderr)
        return 1

    api = Api(pat)
    table = api.table(BASE_ID, FOODS_TABLE)

    print("Loading existing foods to skip duplicates…")
    existing_names = {
        (r["fields"].get(FOODS_FIELDS["name_fr"]) or "").strip().lower()
        for r in table.all(fields=[FOODS_FIELDS["name_fr"]])
    }
    print(f"  {len(existing_names)} foods already in the base.")

    to_create = []
    skipped = 0
    for name, category, kcal, p, c, f, fiber, portion in FOODS:
        if name.strip().lower() in existing_names:
            skipped += 1
            continue
        to_create.append(
            {
                FOODS_FIELDS["name_fr"]: name,
                FOODS_FIELDS["category"]: category,
                FOODS_FIELDS["kcal_per_100g"]: kcal,
                FOODS_FIELDS["protein_per_100g"]: p,
                FOODS_FIELDS["carbs_per_100g"]: c,
                FOODS_FIELDS["fat_per_100g"]: f,
                FOODS_FIELDS["fiber_per_100g"]: fiber,
                FOODS_FIELDS["standard_portion_g"]: portion,
                FOODS_FIELDS["source"]: "starter",
                FOODS_FIELDS["active"]: True,
            }
        )

    print(f"  {skipped} duplicates skipped, {len(to_create)} new foods to add.")

    # Airtable accepts up to 10 records per write.
    batch_size = 10
    added = 0
    for i in range(0, len(to_create), batch_size):
        batch = to_create[i : i + batch_size]
        table.batch_create(batch, typecast=True)
        added += len(batch)
        print(f"  + {added}/{len(to_create)} added")

    print(f"\nDone. Foods table now has {len(existing_names) + added} entries.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
