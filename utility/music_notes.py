# music_notes.py

OCTAVE_NUMBER_LIST = list(range(1, 10))
NOTES_IN_SCALE_LIST = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"]

MIDI_NOTE_NUMBERS_LIST = list(range(12, 109))
MUSIC_NOTES_LIST = []  # musical notes i.e. c4
NOTE_FREQUENCIES_LIST = []  # frequency of a note in Hz

MIDI_NOTE_NUMBER_TO_MUSIC_NOTE_DICT = {}  # dict[midi_note_number] = music_note
MIDI_NOTE_NUMBER_TO_FREQUENCY_DICT = {}  # dict[midi_note_number] = frequency in Hz

FREQUENCY_TO_MIDI_NUMBER_DICT = {}  # dict[freq] = midi_note_number i.e. 72
FREQUENCY_TO_MUSIC_NOTE_DICT = {}  # dict[freq] = music_note i.e. c4

MUSIC_NOTE_TO_FREQUENCY_DICT = {}  # dict[music_note] = freq
MUSIC_NOTE_TO_MIDI_NOTE_NUMBER_DICT = {}  # dict[music_note] = midi_note

A4_FREQUENCY = 440

# Populate NOTE_NUMBERS
counter = 0
for oct_number in OCTAVE_NUMBER_LIST:
    for note in NOTES_IN_SCALE_LIST:
        MUSIC_NOTES_LIST.append(note + str(oct_number))
        counter += 1
        if counter >= len(MIDI_NOTE_NUMBERS_LIST):
            break


# Populate NOTE_FREQUENCIES_LIST
for i in range(len(MIDI_NOTE_NUMBERS_LIST)):
    # Calculate the MIDI note number.
    midi_note_number = int(MIDI_NOTE_NUMBERS_LIST[i])

    # Calculate the frequency using the formula.
    if midi_note_number is not None:
        frequency = A4_FREQUENCY * (2 ** ((midi_note_number - 69) / 12))
        NOTE_FREQUENCIES_LIST.append(frequency)
    else:
        NOTE_FREQUENCIES_LIST.append(0)


# Build MIDI_NOTE_NUMBER_TO_MUSIC_NOTE_DICT dictionary
for i, midi_note in enumerate(MIDI_NOTE_NUMBERS_LIST):
    MIDI_NOTE_NUMBER_TO_MUSIC_NOTE_DICT[midi_note] = MUSIC_NOTES_LIST[i]

# MIDI_NOTE_NUMBER_TO_FREQUENCY_DICT
for i, midi_note in enumerate(MIDI_NOTE_NUMBERS_LIST):
    MIDI_NOTE_NUMBER_TO_FREQUENCY_DICT[midi_note] = NOTE_FREQUENCIES_LIST[i]

# FREQUENCY_TO_MIDI_NUMBER_DICT
for i, freq in enumerate(NOTE_FREQUENCIES_LIST):
    FREQUENCY_TO_MIDI_NUMBER_DICT[freq] = MIDI_NOTE_NUMBERS_LIST[i]

# FREQUENCY_TO_MUSIC_NOTE_DICT
for i, freq in enumerate(NOTE_FREQUENCIES_LIST):
    FREQUENCY_TO_MUSIC_NOTE_DICT[freq] = MUSIC_NOTES_LIST[i]

# MUSIC_NOTE_TO_FREQUENCY_DICT
for i, note in enumerate(MUSIC_NOTES_LIST):
    MUSIC_NOTE_TO_FREQUENCY_DICT[note] = NOTE_FREQUENCIES_LIST[i]

# MUSIC_NOTE_TO_MIDI_NOTE_NUMBER_DICT
for i, note in enumerate(MUSIC_NOTES_LIST):
    MUSIC_NOTE_TO_MIDI_NOTE_NUMBER_DICT[note] = MIDI_NOTE_NUMBERS_LIST[i]


def music_note_from_midi_number(midi_note: int):
    if midi_note in MIDI_NOTE_NUMBER_TO_MUSIC_NOTE_DICT:
        return MIDI_NOTE_NUMBER_TO_MUSIC_NOTE_DICT[midi_note]
    print(f'midi note: {midi_note} not found')


def convert_midi_to_note(m):
    if m in MIDI_NOTE_NUMBER_TO_MUSIC_NOTE_DICT:
        return MIDI_NOTE_NUMBER_TO_MUSIC_NOTE_DICT[m]
    print(f'{m} not found')


def convert_midi_to_frequency(m):
    if m in MIDI_NOTE_NUMBER_TO_FREQUENCY_DICT:
        return MIDI_NOTE_NUMBER_TO_FREQUENCY_DICT[m]
    print(f'{m} not found')


def convert_frequency_to_midi(f):
    if f in FREQUENCY_TO_MIDI_NUMBER_DICT:
        return FREQUENCY_TO_MIDI_NUMBER_DICT[f]
    print(f'{freq} not found')


def convert_frequency_to_note(f):
    if f in FREQUENCY_TO_MUSIC_NOTE_DICT:
        return FREQUENCY_TO_MUSIC_NOTE_DICT[f]
    print(f'{f} not found')


def convert_note_to_frequency(n):
    if n in MUSIC_NOTE_TO_FREQUENCY_DICT:
        return MUSIC_NOTE_TO_FREQUENCY_DICT[n]
    print(f'{n} not found')


def convert_note_to_midi(n):
    if n in MUSIC_NOTE_TO_MIDI_NOTE_NUMBER_DICT:
        return MUSIC_NOTE_TO_MIDI_NOTE_NUMBER_DICT[n]
    print(f'{n} not found')
