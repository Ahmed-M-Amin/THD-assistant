import streamlit as st
import streamlit.components.v1 as components
components.html("<script>console.log(window.parent.document.querySelector('div'));</script>")
