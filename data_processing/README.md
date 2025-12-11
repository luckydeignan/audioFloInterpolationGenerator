# Data Processing

This directory contains utility scripts for processing MIDI and audio files in the emotion-to-music pipeline.

## Scripts

### `extract_piano_melody.py`

Extracts monophonic piano melodies from MIDI files, handling complex cases like multiple time signatures and tempo changes.

**Features:**
- Extracts specific bar ranges from MIDI files
- Handles multiple time signatures by selecting the predominant one
- Handles multiple tempos by selecting the predominant one
- Converts polyphonic input to monophonic melody (highest note wins)
- Preserves original tempo in output

**Usage:**
```bash
python data_processing/extract_piano_melody.py
```

**Configuration:**
Edit the `main()` function to set:
- `measure` - Number of bars to extract (2 or 16)
- `story` - Story name to process
- CSV path to cluster-to-MIDI mapping

---

### `convert_midi_to_wav.py`

Converts MIDI files to WAV format using FluidSynth command-line.

**Prerequisites:**
- [FluidSynth](https://www.fluidsynth.org/) installed
- SoundFont file (included: `FluidR3_GM/FluidR3_GM.sf2`)

**Usage:**
```bash
python data_processing/convert_midi_to_wav.py
```

**Configuration:**
Edit `main()` to set:
- `output_directory` - Where to save WAV files
- `fluidsynth_executable` - Path to FluidSynth
- `soundfont_path` - Path to .sf2 file
- `midi_files` - List of MIDI files to convert

---

### `convert_vgmidi_to_mp3.py`

Batch converts MIDI files to MP3 format (MIDI → WAV → MP3).

**Prerequisites:**
- FluidSynth installed
- FFmpeg installed and in PATH

**Usage:**
```bash
python data_processing/convert_vgmidi_to_mp3.py
```

**Configuration:**
Constants at the top of the file:
```python
FLUIDSYNTH_EXE = "path/to/fluidsynth.exe"
SOUNDFONT_PATH = "FluidR3_GM/FluidR3_GM.sf2"
INPUT_DIR = "vgMidiDataset"
OUTPUT_DIR = "mp3_dataset"
MP3_QUALITY = "2"  # VBR quality (0=best, 9=worst)
```

---

### `merge_midis.py`

Concatenates multiple MIDI files into a single file with optional overlap for smooth transitions.

**Usage:**
```bash
python data_processing/merge_midis.py
```

**API:**
```python
from data_processing.merge_midis import merge_midi_files

merge_midi_files(
    midi_paths=["file1.mid", "file2.mid", "file3.mid"],
    output_path="merged.mid",
    overlap_seconds=0.5  # Crossfade duration
)
```

---

### `play_midi_audio.py`

Plays audio files (MIDI, WAV, MP3, MP4) with optional measure-based start position.

**Features:**
- Displays duration, tempo, and time signature before playback
- Start MIDI playback from a specific measure
- Optional duration limit for testing

**Prerequisites:**
- `pygame` - Required for playback
- `mido` - Optional, for MIDI duration and measure-based start
- `mutagen` - Optional, for audio file duration info

**Usage:**
```bash
python data_processing/play_midi_audio.py
```

**Configuration:**
Edit `main()` to set:
- `audio_files` - List of (file_path, start_measure) tuples
- `PLAY_DURATION` - Seconds to play (None for full playback)

## Dependencies

Install required packages:

```bash
pip install note_seq pretty_midi pygame mido mutagen
```

External tools:
- [FluidSynth](https://www.fluidsynth.org/) - MIDI synthesis
- [FFmpeg](https://ffmpeg.org/) - Audio conversion

## SoundFont

The repository includes `FluidR3_GM/FluidR3_GM.sf2`, a General MIDI SoundFont for realistic instrument sounds.

