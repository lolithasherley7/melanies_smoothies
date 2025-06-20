import streamlit as st
from snowflake.snowpark.functions import col
import requests

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie")

# Input for name
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write(f"The name on the Smoothie will be: {name_on_order}")

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit list from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Optional: show fruit list
st.dataframe(pd_df)

# Let user pick fruits
options = pd_df['FRUIT_NAME'].tolist()
ingredients_list = st.multiselect("Choose up to 5 ingredients:", options, max_selections=5)

# ✅ Helper function for API calls ONLY (not for inserting)
def singularize(name: str) -> str:
    name = name.lower()
    if name.endswith('ies'):
        return name[:-3] + 'y'    # blueberries → berry
    elif name.endswith('s') and not name.endswith('ss'):
        return name[:-1]          # apples → apple
    else:
        return name

if ingredients_list and name_on_order:
    st.write("Selected fruits:", ingredients_list)

    # ✅ FIXED: Strip spaces, insert exactly what the user selected
    ingredients_clean = [f.strip() for f in ingredients_list]
    ingredients_string = ', '.join(ingredients_clean)

    # Display nutrition info using singularized names
    for fruit in ingredients_clean:
        search_key = pd_df.loc[pd_df['FRUIT_NAME'] == fruit, 'SEARCH_ON'].iloc[0]
        normalized_key = singularize(search_key.lower())

        st.subheader(f"{fruit} Nutrition Information")

        # Fruityvice API
        fruityvice_url = f"https://fruityvice.com/api/fruit/{normalized_key}"
        fruityvice_response = requests.get(fruityvice_url)
        if fruityvice_response.ok:
            st.dataframe(fruityvice_response.json(), use_container_width=True)
        else:
            st.write(f"Fruityvice data not found for {fruit}")

        # SmoothieFroot API
        smoothiefroot_url = f"https://my.smoothiefroot.com/api/fruit/{normalized_key}"
        smoothiefroot_response = requests.get(smoothiefroot_url)
        if smoothiefroot_response.ok:
            st.dataframe(smoothiefroot_response.json(), use_container_width=True)
        else:
            st.write(f"SmoothieFroot data not found for {fruit}")

    # SQL insert for smoothie order
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders("INGREDIENTS", "NAME_ON_ORDER") 
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    st.write(my_insert_stmt)

    # Submit button
    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
