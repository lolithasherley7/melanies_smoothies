# Import python packages
import streamlit as st
# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw: ")
st.write(
  """Choose the fruits you want in your custom Smoothie
  """)


name_on_order = st.text_input("Name on Smoothie: ")
st.write("The name on the Smoothie will be : ", name_on_order)


# option = st.selectbox(
#     "What is your favourite Fruit?",
#     ("Banana", "Strawberries", "Peaches"),
# )

# st.write("Your favourite Fruit is:", option)


cnx=st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
st.dataframe(data=my_dataframe, use_container_width=True)
st.stop()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:", 
    [row["FRUIT_NAME"] for row in my_dataframe.collect()],
    max_selections = 5
)

if ingredients_list and name_on_order:
    st.write(ingredients_list)
    st.text(ingredients_list)

    ingredients_string = ' '
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + 'Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon" + fruit_chosen)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width= True)
 

    my_insert_stmt = f"INSERT INTO smoothies.public.orders(\"INGREDIENTS\", \"NAME_ON_ORDER\") VALUES ('{ingredients_string}', '{name_on_order}')"


    st.write(my_insert_stmt)
    # st.stop()
    if ingredients_list and name_on_order:
        time_to_insert = st.button('Submit Order')
        
        if time_to_insert:
            session.sql(my_insert_stmt).collect()
            st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")

#new section to display smoothiefrroot nutrition information 



            

