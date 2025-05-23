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
    Üdvözöllek a Legyél mindig tudatos! appban, az alkalmazásnak 3 fő mozgatórugója van, táplálkozzunk egészségesebben, csökkentsük a környezetünk terhelését és spóroljunk.
    
    Játszunk a számokkal, nézd meg mennyit spórolsz! Az app használatával könnyen ki tudod számolni, hogy ha szakítasz a pékséggel, bolti rágcsikkal és édességekkel, mennyi pénz marad a zsebedben, amelett, hogy megvonod magadtól a felesleges káros élelmiszerösszetevőket.

    """
)

show_more = st.toggle("Tovább olvasom 👀")

if show_more:
    st.markdown("""

    A homemade szemlélettel kíméljük a pénztárcánkat, ez egy vizuális motiváció tud lenni. Azzal a kenyérrel, amit én mostanában sütni szoktam, kb. 400 Ft-ot takarítok meg és még összetevőit tekintve is sokkal inkább kedvemre való. Az is kiderült, hogy a tésztát bekeverni pont annyi idő, amíg kivárom a sort a pékségben, a többit már intézi a dagasztó gép és a sütő. A homemade életmód kíván némi átgondoltságot és tudatosságot, igényel tervezést, de ha megvan a kellő motiváció, akkor hozzá lehet szokni.

    A pénztárcánk kímélése mellett engedjük, hogy a homemade szemlélet végezze a dolgát:

     - kísérletezzünk alternativ, a szervezetet kevésbé terhelő összetevőkkel

     - ne kergessünk hiú ábrándokat, valóban több időt fogunk a konyhában tölteni, DE be lehet vonni a gyerekeket, kíváló közös program és hasznos lehet, ha azt látják, hogy nem mindent a boltban, készen veszünk meg
     
     - ha a szervezetünk tehermentesítve van, akkor jobban van energiája a betegségeknek ellenállni
     
     - ritkábban vagyunk betegek, kevesebb gyógyszert kell alkalmaznunk, ezzel megint csak spórolunk
     
     - ha csökken a gyógyszerbevitel, akkor az előállítás ritmusának is lassulnia kell, tehát csökken a gyárak károsanyag kibocsátása
     
     - ezáltal javul a levegő minőség, lelassul a globális felmelegedés, javul az életminőség

    A homemade szemlélet számos előnnyel bír, a jó hír az, hogy amíg a lomha és hosszú távon kimutatható pozitívumok beérnek, addig is tudjuk a megtakarításunkat számolni 😊
    
    Ez a szemlélet ihlette az alkalmazást, de egy kicsit tovább gondoltam, kibővítettem egy második blokkal, ami azt számolja, hogy ha az autót gyaloglásra vagy kerékpárra cseréljük, a megadott táv megtételével hány gramm széndioxidtól vontad meg a bolygót, mennyi üzemanyag költséget spóroltál meg magadnak, és mennyi kalóriát égettél el ezzel a remek döntéssel 😊
    
    Játszunk el a gondolattal, egy héten hányszor adódik olyan alkalom, hogy el kell ugranod gyorsan valahova (elfogyott a tejföl, megérkezett a az automatába a csomag, ...)?! Ha heti 3-szor teszel meg alkalmanként 2 km-t gyalog vagy biciklivel, az éves szinten 260 km. Az app segítségével könnyen ki tudod számolni, ezzel mennyi üzemanyagköltséget spóroltál meg és hány gramm CO₂-től kíméled meg a levegőt. És ez csak TE vagy, rajtad kívül él még 8 milliárd ember a Földön...
    
    Vigyázat, mert a homemade magatartás és a mozgás függőséget okoz! 😊
                
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


# Kategória azonosítása a kiválasztott alapanyag alapján

if selected_ingredient == "Egyéb":
    custom_ingredient_name = st.text_input("Add meg az új alapanyag nevét:")
    custom_price_per_unit = st.number_input("Add meg az új alapanyag árát (Ft egységenként):", min_value=0.0, step=1.0)
    custom_unit = st.text_input("Add meg az új alapanyag mértékegységét (pl. g, db, dl):", value="g")
else:
    custom_ingredient_name = selected_ingredient

    if selected_category in data["ingredients"] and selected_ingredient in data["ingredients"][selected_category]:
        custom_price_per_unit = data["ingredients"][selected_category][selected_ingredient]["price_per_unit"]
        custom_unit = data["ingredients"][selected_category][selected_ingredient]["unit"]
    else:
        custom_price_per_unit = st.number_input(
            f"Add meg a(z) {selected_ingredient} árát (Ft egységenként):", min_value=0.0, step=1.0, key=f"custom_price_{selected_ingredient}"
        )
        custom_unit = st.text_input(
            f"Add meg a(z) {selected_ingredient} mértékegységét (pl. g, db, dl):", value="g", key=f"custom_unit_{selected_ingredient}"
        )

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
        material_cost = price_per_unit * qty
        st.write(
            f"- {name}: {qty} {unit} "
            f"(egységár: {price_per_unit:.2f} Ft/{unit}), "
            f"anyagköltség: {material_cost:.2f} Ft"
        )

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
st.write(f"Megtakarítás: **{int(round(total_data['total_saving']))} Ft**")

st.markdown("---")
st.markdown("<h2 style='font-size: 36px;'>Tudatos közlekedési döntéseid</h2>", unsafe_allow_html=True)

import streamlit as st
import json

# Példa adatszerkezet, valóságban betöltés és mentés is kell
total_data = {
    "transport_choices": {
        "total_distance_m": 0,
        "total_count": 0,
        "co2_saved": {},
        "burned_calories_walk": 0.0,
        "burned_calories_bike":0.0
    }
}

CO2_VALUES = {
    "Benzines": 215,
    "Dízel": 180,
    "Elektromos": 75
}

FUEL_COSTS = {
    "Benzines": {"consumption_l_per_100km": 7.0, "price_per_l": 620},
    "Dízel": {"consumption_l_per_100km": 5.5, "price_per_l": 650},
    "Elektromos": {"consumption_kWh_per_100km": 18.0, "price_per_kWh": 100}
}

# --- Beviteli mezők ---
st.subheader("🚶‍♂️ Közlekedési adatok megadása")

transport_type = st.selectbox(
    "Milyen módon közlekedtél az autó helyett?",
    options=["Gyaloglás", "Biciklizés"],
    key="transport_type"
)

transport_choice = st.selectbox(
    "Milyen járművet cserélted le a környezetkímélő közlekedésre?",
    options=["Benzines", "Dízel", "Elektromos"],
    key="transport_choice"
)

transport_count = st.number_input(
    "Hányszor választottad ma az autó helyett a sétát/biciklizést?",
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

# --- Súlymegadás (EZ KERÜL LEGELŐRE!) ---
st.subheader("⚖️ Kalória kalkulátor (opcionális)")
wants_to_add_weight = st.radio("Szeretnél testsúlyt megadni a kalória kalkulációhoz?", ["Nem", "Igen"])

if wants_to_add_weight == "Igen":
    user_weight = st.number_input("Add meg a testsúlyodat (kg):", min_value=20.0, max_value=300.0, value=70.0, step=0.5)
else:
    user_weight = 70.0
    st.info("Nem adtál meg testsúlyt, az alapértelmezett 70 kg-al számolunk.")

# --- Összesített adatbetöltés ---
if os.path.exists("savings.json"):
    with open("savings.json", "r", encoding="utf-8") as f:
        total_data = json.load(f)
else:
    total_data = {}

# Biztosítjuk az elvárt adatstruktúrát, ha hiányzik valami
total_data.setdefault("transport_choices", {})
total_data["transport_choices"].setdefault("total_distance_m", 0)
total_data["transport_choices"].setdefault("total_count", 0)
total_data["transport_choices"].setdefault("co2_saved", {})
total_data["transport_choices"].setdefault("burned_calories_walk", 0.0)
total_data["transport_choices"].setdefault("burned_calories_bike", 0.0)
total_data["transport_choices"].setdefault("fuel_cost_saved", {})

# --- Kalkuláció ---
if st.button("🔥 Kalkulál és ment"):

    # Elmentjük az alkalmak és távolság számát
    total_data["transport_choices"]["total_distance_m"] += transport_distance
    total_data["transport_choices"]["total_count"] += transport_count

    # Kalóriaégetés számítása
    if transport_distance > 0:
        distance_km = transport_distance / 1000
        walk_kcal = 0.9 * user_weight * distance_km
        bike_kcal = 0.4 * user_weight * distance_km

        if transport_type == "Gyaloglás":
            total_data["transport_choices"]["burned_calories_walk"] += walk_kcal
            st.success(f"💪 Ezzel a választással {walk_kcal:.1f} kcal-t égettél el gyaloglással.")
        elif transport_type == "Biciklizés":
            total_data["transport_choices"]["burned_calories_bike"] += bike_kcal
            st.success(f"💪 Ezzel a választással {bike_kcal:.1f} kcal-t égettél el biciklizéssel.")            

    # CO₂ megtakarítás számítása mindig történik, függetlenül a távolságtól
    distance_km = transport_distance / 1000
    grams_per_km = CO2_VALUES.get(transport_choice, 0)
    saved_grams = distance_km * grams_per_km

    total_data["transport_choices"]["co2_saved"].setdefault(transport_choice, 0.0)
    total_data["transport_choices"]["co2_saved"][transport_choice] += saved_grams

    # Üzemanyagköltség megtakarítás kiszámítása
    fuel_data = FUEL_COSTS.get(transport_choice)

    if fuel_data:
        if transport_choice == "Elektromos":
            consumption_per_km = fuel_data["consumption_kWh_per_100km"] / 100
            fuel_price = fuel_data["price_per_kWh"]
        else:
            consumption_per_km = fuel_data["consumption_l_per_100km"] / 100
            fuel_price = fuel_data["price_per_l"]

        saved_fuel = distance_km * consumption_per_km
        saved_cost = saved_fuel * fuel_price
    else:
        saved_cost = 0
    
    total_data["transport_choices"]["fuel_cost_saved"].setdefault(transport_choice, 0.0)
    total_data["transport_choices"]["fuel_cost_saved"][transport_choice] += saved_cost

    saved_texts = []
    saved_texts.append(f"**{transport_choice}**: {saved_grams:.2f} g CO₂ / {saved_cost:.0f} Ft megtakarítás")

    st.success("Adatok mentve!")
    if transport_distance > 0:
        st.info("Nézd meg, hány gramm CO₂-vel kímélted meg a bolygót ezzel a sétával/biciklizéssel:\n\n" + "\n".join(saved_texts))
    else:
        st.info("Nézd meg, hány gramm CO₂-vel kímélted meg a bolygót az alternatív közlekedés választásával:\n\n" + "\n".join(saved_texts))

    with open("savings.json", "w", encoding="utf-8") as f:
        json.dump(total_data, f, ensure_ascii=False, indent=2)

# --- Összegzés ---
st.markdown("---")
st.subheader("📊 Összesített környezetvédelmi hatás")

st.write(f"Összes gyaloglással elégetett kalória: **{total_data['transport_choices']['burned_calories_walk']:.1f} kcal**")
st.write(f"Összes biciklizéssel elégetett kalória: **{total_data['transport_choices']['burned_calories_bike']:.1f} kcal**")

st.write(f"Összes alternatív közlekedési alkalmak száma: **{total_data['transport_choices']['total_count']}**")
st.write(f"Összes megtett távolság: **{total_data['transport_choices']['total_distance_m'] / 1000:.2f} km**")

st.write("**Elkerült CO₂ kibocsátás autótípusonként:**")
for car, grams in total_data["transport_choices"]["co2_saved"].items():
    if grams > 0:
        st.write(f"- {car}: {grams:.2f} gramm CO₂")

st.write("**Üzemanyagköltség-megtakarítás autótípusonként:**")
for car, cost in total_data["transport_choices"]["fuel_cost_saved"].items():
    if cost > 0:
        st.write(f"- {car}: {cost:.0f} Ft")
