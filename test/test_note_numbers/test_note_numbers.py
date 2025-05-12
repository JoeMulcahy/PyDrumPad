from utility.music_notes import NoteNumbers
import pytest


@pytest.fixture
def note_numbers_instance():
    return NoteNumbers()


def test_midi_notes_list_type(note_numbers_instance):
    assert isinstance(note_numbers_instance.midi_notes_list, list)


def test_octaves_list_type(note_numbers_instance):
    assert isinstance(note_numbers_instance.octaves_list, list)


def test_notes_in_scale_type(note_numbers_instance):
    assert isinstance(note_numbers_instance.notes_in_scale, list)


def test_midi_to_notes_dict_type(note_numbers_instance):
    # The dictionary is initially empty until __generate_midi_to_notes is called
    assert isinstance(note_numbers_instance.midi_to_notes_dict, dict)


def test_midi_notes_list_content(note_numbers_instance):
    expected_midi_notes = list(range(12, 109))
    assert note_numbers_instance.midi_notes_list == expected_midi_notes


def test_octaves_list_content(note_numbers_instance):
    expected_octaves = list(range(0, 9))
    assert note_numbers_instance.octaves_list == expected_octaves


def test_notes_in_scale_content(note_numbers_instance):
    expected_notes = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"]
    assert note_numbers_instance.notes_in_scale == expected_notes


def test_midi_to_notes_dict_content(note_numbers_instance):
    assert len(note_numbers_instance.midi_to_notes_dict) == 97
    assert note_numbers_instance.midi_to_notes_dict[21] == "a0"
    assert note_numbers_instance.midi_to_notes_dict[60] == "c4"
    assert note_numbers_instance.midi_to_notes_dict[108] == "c8"


def test_get_midi_note_number_from_notes_valid(note_numbers_instance):
    assert note_numbers_instance.get_midi_note_number_from_notes("c4") == 60
    assert note_numbers_instance.get_midi_note_number_from_notes("a0") == 21
    assert note_numbers_instance.get_midi_note_number_from_notes("c8") == 108


def test_get_midi_note_number_from_notes_invalid(note_numbers_instance):
    assert note_numbers_instance.get_midi_note_number_from_notes(
        "invalid_note") is None  # Or you might expect a specific error/behavior


def test_get_midi_note_number_from_notes_none(note_numbers_instance, capsys):
    note_numbers_instance.get_midi_note_number_from_notes(None)
    captured = capsys.readouterr()
    assert "note: None not found" in captured.out


def test_get_note_from_midi_number_valid(note_numbers_instance):
    assert note_numbers_instance.music_note_from_midi_number(60) == "c4"
    assert note_numbers_instance.music_note_from_midi_number(21) == "a0"
    assert note_numbers_instance.music_note_from_midi_number(108) == "c8"


def test_get_note_from_midi_number_invalid(note_numbers_instance, capsys):
    note_numbers_instance.music_note_from_midi_number(0)
    captured = capsys.readouterr()
    assert "midi note: 0 not found" in captured.out
    note_numbers_instance.music_note_from_midi_number(128)
    captured = capsys.readouterr()
    assert "midi note: 128 not found" in captured.out
