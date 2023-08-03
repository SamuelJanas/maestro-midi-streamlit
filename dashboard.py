import streamlit as st
from fortepyan import MidiPiece
from datasets import load_dataset

import utils as U

# Define the number of records to display per page
n_records_per_page = 4

# Global variables to store filter options
selected_composer = None
search_by_title = None
filter_option = None


def load_data(selected_split):
    # Load the dataset for the selected split
    dataset = load_dataset("roszcz/maestro-v1-sustain", split=selected_split)

    # Apply the filtering based on the current filter option
    if filter_option == "composer" and selected_composer:
        dataset = dataset.filter(lambda example: example["composer"] == selected_composer)
    elif filter_option == "title" and search_by_title:
        dataset = dataset.filter(lambda example: str(search_by_title) in example["title"])

    return dataset


def get_composers(dataset):
    # Get unique composer names from the dataset
    composers = [x for x in dataset.unique("composer")]
    return composers


def show_midi_pieces(filtered_dataset, pieces_per_page, current_page, subheader=""):
    # Calculate the start and end index for the current page
    start_idx = (current_page - 1) * pieces_per_page
    end_idx = min(start_idx + pieces_per_page, len(filtered_dataset))

    # Display the records for the selected composer for the current page
    st.subheader(subheader)
    cols = st.columns(2)

    for it in range(start_idx, end_idx):
        record = filtered_dataset[it]
        piece = MidiPiece.from_huggingface(record)
        paths = U.piece_av_files(piece)

        # Display the information and media for the MIDI piece in the columns
        with cols[it % 2]:
            st.audio(paths["mp3_path"], format="audio/mp3")
            st.image(paths["pianoroll_path"])
            st.table(piece.source)


def update_page(dataset, option, value, title=""):
    if option == "composer":
        filtered_dataset = dataset.filter(lambda example: example["composer"] == value)

    elif option == "title":
        # search for titles that contain the search string
        filtered_dataset = dataset.filter(lambda example: value in example["title"])

    return filtered_dataset


def main():
    # Set the layout of the Streamlit page
    st.set_page_config(layout="wide")

    # select the number of pieces per page

    with st.sidebar:
        # Create a combo box to select a split (train, test, or validation)
        pieces_per_page = st.selectbox("Select the number of pieces per page:", [4, 6, 8, 10])
        selected_split = st.selectbox("Select a split:", ["train", "test", "validation"])

    # Load the dataset for the selected split
    dataset = load_data(selected_split)

    # Get unique composer names from the dataset
    composers = get_composers(dataset)

    if not composers:
        st.warning("No composers found for the selected split.")
        return

    # Create a combo box to select a composer
    selected_composer = st.sidebar.selectbox("Select a composer:", composers)

    # Create a text input to search by title
    search_by_title = st.sidebar.text_input("Search by title:")

    # Create a radio button to select the filter option (composer or title)
    filter_option = st.sidebar.radio("Filter by:", ["composer", "title"])

    if filter_option == "composer" and selected_composer:
        filtered_dataset = dataset.filter(lambda example: example["composer"] == selected_composer)
    elif filter_option == "title" and search_by_title:
        filtered_dataset = dataset.filter(lambda example: str(search_by_title) in example["title"])
    else:
        filtered_dataset = dataset

    # Create a slider for page navigation
    pages = len(filtered_dataset) // pieces_per_page
    if pages > 1:
        current_page = st.slider("Page:", min_value=1, max_value=len(filtered_dataset) // pieces_per_page, step=1)
    else:
        current_page = 1

    # Show the MIDI pieces for the selected composer on the current page
    show_midi_pieces(filtered_dataset, pieces_per_page, current_page)


if __name__ == "__main__":
    main()
