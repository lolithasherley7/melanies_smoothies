import streamlit as st
from snowflake.snowpark.functions import col
import requests

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie")

name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write(f"The name on the Smoothie will be: {name_on_order}")

cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit data from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Show the fruit table (optional)
st.dataframe(pd_df)

# Multiselect shows user-friendly FRUIT_NAME
options = pd_df['FRUIT_NAME'].tolist()
ingredients_list = st.multiselect("Choose up to 5 ingredients:", options, max_selections=5)

# Helper function to singularize for API calls
def singularize(name: str) -> str:
    name = name.lower()
    if name.endswith('ies'):
        return name[:-3] + 'y'    # berries -> berry
    elif name.endswith('s') and not name.endswith('ss'):
        return name[:-1]          # apples -> apple
    else:
        return name

if ingredients_list and name_on_order:
    st.write("Selected fruits:", ingredients_list)
    ingredients_string = ' '.join(ingredients_list)

    for fruit in ingredients_list:
        # Get SEARCH_ON value for API queries
        search_key = pd_df.loc[pd_df['FRUIT_NAME'] == fruit, 'SEARCH_ON'].iloc[0]
        normalized_key = singularize(search_key.lower())

        st.subheader(f"{fruit} Nutrition Information")

        # Fruityvice API call
        fruityvice_url = f"https://fruityvice.com/api/fruit/{normalized_key}"
        fruityvice_response = requests.get(fruityvice_url)
        if fruityvice_response.ok:
            st.dataframe(fruityvice_response.json(), use_container_width=True)
        else:
            st.write(f"Nutrition info not found for {fruit} from Fruityvice API")

        # SmoothieFroot API call
        smoothiefroot_url = f"https://my.smoothiefroot.com/api/fruit/{normalized_key}"
        smoothiefroot_response = requests.get(smoothiefroot_url)
        if smoothiefroot_response.ok:
            st.dataframe(smoothiefroot_response.json(), use_container_width=True)
        else:
            st.write(f"Nutrition info not found for {fruit} from SmoothieFroot API")

    # Prepare SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders("INGREDIENTS", "NAME_ON_ORDER") 
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    st.write(my_insert_stmt)

    # Submit button
    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
