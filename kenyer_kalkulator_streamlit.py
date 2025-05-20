import streamlit as st
import json
from datetime import datetime
import os

from supabase import create_client, Client

# Supabase init
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Fájlnevek ---
DATA_FILE = "data.json"
SAVINGS_FILE = "savings.json"

def save_total_saving(total_saving_data):
    with open(SAVINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(total_saving_data, f, ensure_ascii=False, indent=2)

def load_total_saving():
    if not os.path.exists(SAVINGS_FILE):
        data = {
            "total_saving": 0.0,
            "first_calculation": datetime.now().strftime("%Y-%m-%d"),
            "by_category": {
                "Élelmiszer": 0.0,
                "Használt cikkek": 0.0,
                "Könyvtár": 0.0
            }
        }
        save_total_saving(data)
        return data
    else:
        with open(SAVINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

if "total_data" not in st.session_state:
    st.session_state.total_data = load_total_saving()

total_data = st.session_state.total_data

st.set_page_config(page_title="Kenyér Kalkulátor", page_icon="🍞")

# --- Adatok betöltése ---
def load_data():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

# --- Streamlit oldalbeállítás ---
st.title("Legyél mindig tudatos!")
st.markdown(
    """
    Nézd meg mennyit spórolsz! Az app használatával könnyen ki tudod számolni, hogy ha szakítasz a pékséggel, bolti rágcsikkal és édességekkel, mennyi pénz marad a zsebedben.

    """
)

show_more = st.toggle("Tovább olvasom 👀")

if show_more:
    st.markdown("""

    A homemade szemlélettel kíméljük a pénztárcánkat, ez egy vizuális motiváció tud lenni. Azzal a kenyérrel, amit én mostanában sütni szoktam, kb. 400 Ft-ot takarítok meg és még összetevőit tekintve is sokkal inkább kedvemre való. Az is kiderült, hogy a tésztát bekeverni pont annyi idő, amíg kivárom a sort a pékségben, a többit már intézi a dagasztó gép és a sütő. A homemade életmód kíván némi átgondoltságot és tudatosságot, igényel tervezést, de ha megvan a kellő motiváció, akkor hozzá lehet szokni.

    A pénztárcánk kímélése mellett engedjük, hogy a homemade szemlélet végezze a dolgát:

     - kísérletezzünk alternativ, a szervezetet kevésbé terhelő összetevőkkel

     - ne kergessünk hiú ábrándokat, sokkal többet fogunk állni a konyhában, DE be lehet vonni a gyerekeket, kíváló közös program és hasznos lehet, ha azt látják, hogy nem mindent a boltban veszünk meg
     
     - ha a szervezetünk tehermentesítve van, akkor jobban van energiája a betegségeknek ellenállni
     
     - ritkábban vagyunk betegek, kevesebb gyógyszert kell alkalmaznunk, ezzel megint csak spórolunk
     
     - ha csökken a gyógyszerbevitel, akkor az előállítás ritmusának is lassulnia kell, tehát csökken a gyárak károsanyag kibocsátása
     
     - ezáltal javul a levegő minőség, lelassul a globális felmelegedés, javul az életminőség

    A homemade szemlélet számos előnnyel bír, a jó hír az, hogy amíg a lomha és hosszú távon kimutatható pozitívumok beérnek, addig is tudjuk a megtakarításunkat számolni 😊
                
    Legyél mindig tudatos!

    """
)



# --- Session State inicializálás ---
if "quantities" not in st.session_state:
    st.session_state.quantities = {}

if "calculated" not in st.session_state:
    st.session_state.calculated = False

if "homemade_cost" not in st.session_state:
    st.session_state.homemade_cost = 0.0

if "saving" not in st.session_state:
    st.session_state.saving = 0.0

# --- JSON betöltése ---
def load_data():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()

# --- 1. Kategória kiválasztása ---

st.header("1. Bolti termék kiválasztása")

bread_options = data["store_bread_types"] + ["Egyéb"]
selected_product = st.selectbox("Válassz egy bolti terméktípust:", bread_options)

if selected_product == "Egyéb":
    selected_product = st.text_input("Add meg a termék típusát:", value="Ismeretlen kenyér")

store_price_input = st.text_input(f"Add meg a(z) {selected_product} bolti árát (Ft):", value="")
store_price = float(store_price_input) if store_price_input else 0.0

st.header("2. Alapanyagok kiválasztása")

all_ingredients = {}
for category in data["ingredients"].values():
    all_ingredients.update(category)

ingredient_options = list(all_ingredients.keys()) + ["Egyéb"]
selected_ingredient = st.selectbox("Válassz alapanyagot:", ingredient_options)

# Kategória azonosítása a kiválasztott alapanyag alapján
selected_category = None
for category_name, ingredients_dict in data["ingredients"].items():
    if selected_ingredient in ingredients_dict:
        selected_category = category_name
        break


if selected_ingredient == "Egyéb":
    custom_ingredient_name = st.text_input("Add meg az új alapanyag nevét:")
    custom_price_per_unit = st.number_input("Add meg az új alapanyag árát (Ft egységenként):", min_value=0.0, step=1.0)
    custom_unit = st.text_input("Add meg az új alapanyag mértékegységét (pl. g, db, dl):", value="g")
else:
    custom_ingredient_name = selected_ingredient
    custom_price_per_unit = data["ingredients"][selected_category][selected_ingredient]["price_per_unit"]
    custom_unit = data["ingredients"][selected_category][selected_ingredient]["unit"]

quantity_input = st.text_input(
    f"Add meg a(z) {selected_ingredient} mennyiségét ({custom_unit}):",
    value="",
    key=f"quantity_input_{selected_ingredient}"
)

quantity = float(quantity_input) if quantity_input else 0.0

if st.button("➕ Hozzáadás az alapanyagokhoz"):
    if custom_ingredient_name and quantity > 0:
        st.session_state.quantities[custom_ingredient_name] = (quantity, custom_price_per_unit, custom_unit)
        st.success(f"{custom_ingredient_name} hozzáadva a listához!")

# --- Kalkuláció csak élelmiszer esetén ---
    st.header("3. Kalkuláció")

    if st.session_state.quantities:
        st.subheader("Eddigi alapanyagok:")
        for name, (qty, price_per_unit, unit) in st.session_state.quantities.items():
            st.write(f"- {name}: {qty} {unit} (egységár: {price_per_unit:.2f} Ft/{unit})")

        if st.button("📊 Kalkulálás"):
            homemade_cost = 0
            for name, (qty, price_per_unit, unit) in st.session_state.quantities.items():
                homemade_cost += price_per_unit * qty
            
            saving = store_price - homemade_cost

            st.session_state.homemade_cost = homemade_cost
            st.session_state.saving = saving
            st.session_state.calculated = True

            # Mentés közvetlenül kalkuláció után
            st.session_state.total_data["total_saving"] += saving
            st.session_state.total_data["by_category"]["Élelmiszer"] += saving
            save_total_saving(st.session_state.total_data)

        if st.session_state.calculated:
            st.write(f"- Házi készítés költsége: **{st.session_state.homemade_cost:.2f} Ft**")
            st.write(f"- Megtakarítás: **{st.session_state.saving:.2f} Ft**")
            
            if st.button("🔄 Új kalkuláció indítása"):
                st.session_state.quantities = {}
                st.session_state.calculated = False
                st.rerun()

        else:
            st.info("Adj hozzá legalább egy alapanyagot a kalkulációhoz.")

st.markdown("---")
st.subheader("💰 Összesített megtakarításod")

total_data = load_total_saving()
st.write(f"Első kalkuláció dátuma: {total_data.get('first_calculation', 'N/A')}")
st.write(f"Megtakarítás: **{total_data['total_saving']:.2f} Ft**")
