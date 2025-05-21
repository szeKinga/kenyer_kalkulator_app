import streamlit as st
import json
from datetime import datetime
import os

from supabase import create_client, Client

st.set_page_config(page_title="Kenyér Kalkulátor", page_icon="🍞")

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
            },
            "transport_choices": {
                "total_distance_m": 0,
                "total_count": 0
            }
        }
        save_total_saving(data)
        return data
    else:
        with open(SAVINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if "total_saving" not in data:
            data["total_saving"] = 0.0

        if "first_calculation" not in data:
            data["first_calculation"] = datetime.now().strftime("%Y-%m-%d")
        
        if "by_category" not in data:
            data["by_category"] = {"Élelmiszer": 0.0}
        elif "Élelmiszer" not in data["by_category"]:
            data["by_category"]["Élelmiszer"] = 0.0

        if "transport_choices" not in data:
            data["transport_choices"] = {
                "total_distance_m": 0,
                "total_count": 0
            }
        save_total_saving(data)
        return data

if "total_data" not in st.session_state:
    st.session_state.total_data = load_total_saving()

total_data = st.session_state.total_data

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

# 1. Kategóriaválasztó legördülő
ingredient_categories = list(data["ingredients"].keys())
selected_category = st.selectbox("Válassz alapanyag kategóriát:", ingredient_categories)

# 2. Alapanyagválasztó legördülő a kiválasztott kategória alapján
ingredient_options = list(data["ingredients"][selected_category].keys()) + ["Egyéb"]
selected_ingredient = st.selectbox("Válassz alapanyagot:", ingredient_options)

# Ha "Egyéb" alapanyagot választ a felhasználó, kérjünk manuális nevet és árat
if selected_ingredient == "Egyéb":
    selected_ingredient = st.text_input("Add meg az alapanyag nevét:", value="Ismeretlen alapanyag")
    custom_price = st.number_input(f"Add meg a(z) {selected_ingredient} árát egységenként (Ft):", min_value=0.0, step=1.0)
    unit = st.text_input("Add meg az egységet (pl. g, db, dl):", value="g")
else:
    unit = data["ingredients"][selected_category][selected_ingredient]["unit"]
    custom_price = data["ingredients"][selected_category][selected_ingredient]["price_per_unit"]


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

st.markdown("---")
st.subheader("🚶‍♀️ Tudatos közlekedési döntéseid")

# --- CO2 értékek autótípusonként (gramm/km) ---
import streamlit as st
import os
import json
from datetime import datetime

SAVINGS_FILE = "savings.json"

# --- CO2 értékek autótípusonként (gramm/km) ---
CO2_VALUES = {
    "Benzines": 215,
    "Dízel": 180,
    "Elektromos": 75
}

# --- Beviteli mezők ---
transport_count = st.number_input(
    "Hányszor választottad ma az autó helyett a sétát/biciklizést/tömegközlekedést?",
    min_value=0,
    step=1,
    key="transport_count_input"
)

transport_distance = st.number_input(
    "Ha volt közte séta vagy biciklizés, hány métert tettél meg így?",
    min_value=0,
    step=100,
    key="transport_distance_input"
)

if st.button("➕ Mentés a közlekedési adatokhoz", key="save_transport_button"):
    # Mentett adatok frissítése
    total_data["transport_choices"]["total_distance_m"] += transport_distance
    total_data["transport_choices"]["total_count"] += transport_count

    # Inicializáljuk a co2_saved-et, ha még nincs
    if "co2_saved" not in total_data["transport_choices"]:
        total_data["transport_choices"]["co2_saved"] = {}

    saved_texts = []
    for car_type, grams_per_km in CO2_VALUES.items():
        saved_grams = (transport_distance / 1000) * grams_per_km  # gramm
        # Ha nincs még mentve ilyen típushoz, inicializáljuk
        if car_type not in total_data["transport_choices"]["co2_saved"]:
            total_data["transport_choices"]["co2_saved"][car_type] = 0.0
        total_data["transport_choices"]["co2_saved"][car_type] += saved_grams
        saved_texts.append(f"**{car_type}**: {saved_grams:.2f} g CO₂ megtakarítás")

    save_total_saving(total_data)

    st.success("Adatok mentve!")
    st.info("Nézd meg, hágy gramm CO₂-vel kímélted meg a bolygót ezzel a sétával/biciklizéssel:\n\n" + "\n".join(saved_texts))

st.markdown("---")
st.subheader("📊 Összesített környezetvédelmi hatás")

st.write(f"Összes alternatív közlekedési alkalmak száma: **{total_data['transport_choices']['total_count']}**")
st.write(f"Összes megtett távolság: **{total_data['transport_choices']['total_distance_m'] / 1000:.2f} km**")

st.write("**Elkerült CO₂ kibocsátás autótípusonként:**")
for car, grams in total_data["transport_choices"]["co2_saved"].items():
    st.write(f"- {car}: {grams:.2f} gramm CO₂")