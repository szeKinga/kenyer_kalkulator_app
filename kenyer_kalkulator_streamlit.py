import streamlit as st
import json
from datetime import datetime
import os

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
    Üdvözöllek a “Legyél mindig tudatos!” oldalon.

    Az oldal célja, hogy rávilágítást nyújtson, milyen előnyökkel jár, ha nem csak a gúlyáslevest főzzük meg otthon, hanem a kenyeret is, amit mellé eszünk, esetleg a gyerekünknek otthon sütött kiflit csomagolunk tízóraira.
    """
)

show_more = st.toggle("Tovább olvasom 👀")

if show_more:
    st.markdown("""
    A házilag készített ételek egészségesebbek, de sajnos ez nehezen számszerűsíthető. Véleményem szerint a környezetünket is óvjuk vele, de sajnos szintén nehéz forintban kifejezni. DE, a jó hír az, hogy a tudatosság ezen formájával spórolhatunk is, ami viszont már számszerűsíthető, hurrá 😊

    Add meg a bolti termékek árát, majd a házi készítéshez használt alapanyagok mennyiségét, és azonnal szembesülsz a forintosított különbséggel.

    Az elején persze számolgatni, méregetni kell, átgondolni, hány uzsonnára elegndő az a tepsi kakaóscsiga, és mennyibe került volna ugyanez a pékségben. De ne aggódj, hamar bele lehet rázódni!

    Figyeld az összesítést, ha mindig ugyan azon az eszközön használod az alkalmazást, látod, hogy növekszik napról napra, hétről hétre, hónapról hónapra a homemade szemlélet által keletkezett megtakarításod.

    És ami a legjobb, mindezzel nem csak a pénztárcádat, hanem a saját és a családod egészségét is óvod 😊 

    Legyél mindig tudatos!
    """)

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

st.header("1. Kategória kiválasztása")
category_choice = st.selectbox("Válassz egy kategóriát:", ["Élelmiszer", "Használt cikkek", "Könyvtár"])

if category_choice == "Élelmiszer":
    st.header("2. Bolti termék kiválasztása")

    bread_options = data["store_bread_types"] + ["Egyéb"]
    selected_product = st.selectbox("Válassz egy bolti terméktípust:", bread_options)

    if selected_product == "Egyéb":
        selected_product = st.text_input("Add meg a termék típusát:", value="Ismeretlen kenyér")

    store_price_input = st.text_input(f"Add meg a(z) {selected_product} bolti árát (Ft):", value="")
    store_price = float(store_price_input) if store_price_input else 0.0

    st.header("3. Alapanyagok kiválasztása")

    categories = list(data["ingredients"].keys())
    selected_category = st.selectbox("Válassz kategóriát:", categories)

    ingredient_options = list(data["ingredients"][selected_category].keys()) + ["Egyéb"]
    selected_ingredient = st.selectbox("Válassz alapanyagot:", ingredient_options)

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
    st.header("4. Kalkuláció")

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
        

elif category_choice == "Használt cikkek":
    st.header("2. Használt cikkek kalkuláció")
    used_price = st.number_input("Mennyit költöttél a használt cikkekre? (Ft)", min_value=0.0, step=1.0)
    new_price = st.number_input("Mennyibe került volna újonnan a boltban? (Ft)", min_value=0.0, step=1.0)
    saving_used = new_price - used_price if new_price > used_price else 0.0
    st.session_state.saving_used = saving_used
    if st.button("📊 Kalkulálás - Használt cikkek"):
        st.success(f"Megtakarítás: {saving_used:.2f} Ft")
        total_data["total_saving"] += saving_used
        total_data["by_category"]["Használt cikkek"] += saving_used
        save_total_saving(total_data)
        st.session_state.calculated = True

elif category_choice == "Könyvtár":
    st.header("2. Könyvtári megtakarítás")
    book_price = st.number_input("Mennyibe került volna a könyv (Ft)?", min_value=0.0, step=1.0)
    st.session_state.saving_library = book_price
    if st.button("📚 Kalkulálás - Könyvtár"):
        st.success(f"Megtakarítás a könyvtár által: {book_price:.2f} Ft")
        total_data["total_saving"] += book_price
        total_data["by_category"]["Könyvtár"] += book_price
        save_total_saving(total_data)
        st.session_state.calculated = True

st.markdown("---")
st.subheader("💰 Összesített megtakarításod")

total_data = load_total_saving()
st.write(f"Első kalkuláció dátuma: {total_data.get('first_calculation', 'N/A')}")
st.write(f"Összes megtakarítás eddig: **{total_data['total_saving']:.2f} Ft**")

st.write("Kategóriánkénti megtakarítás:")
st.write(f"- 🥖 Élelmiszer: {total_data['by_category']['Élelmiszer']:.2f} Ft")
st.write(f"- ♻️ Használt cikkek: {total_data['by_category']['Használt cikkek']:.2f} Ft")
st.write(f"- 📚 Könyvtár: {total_data['by_category']['Könyvtár']:.2f} Ft")
