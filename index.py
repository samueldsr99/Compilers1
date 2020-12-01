import streamlit as st

from views.first_follows import first_follows
from views.grammar_details import grammar_details
from views.insert_grammar import insert_grammar
from views.parsing import parsing


def index():
    st.title('Compilación: Proyecto 1')

    choices = [
        'Insertar Gramatica',
        'Detalles de la gramatica',
        'Calcular Firsts & Follows',
        'Parsing'
    ]

    choice = st.sidebar.radio('Seleccione una opcion:', choices)

    if choice == choices[0]:
        insert_grammar()
    elif choice == choices[1]:
        grammar_details()
    elif choice == choices[2]:
        first_follows()
    elif choice == choices[3]:
        parsing()


if __name__ == '__main__':
    index()
