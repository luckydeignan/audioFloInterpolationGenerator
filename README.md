# Emotion-to-Music Pipeline

<img src="magenta-logo-bg.png" height="75">

This repository extends Google's [Magenta](https://github.com/magenta/magenta) project with a custom pipeline for generating music that maps to emotional trajectories in narrative text. The pipeline extracts emotional clusters from stories and uses MusicVAE to generate interpolated musical transitions between emotional states.

## Project Overview

The core pipeline works as follows:

1. **Extract emotional clusters** from story text (external process)
2. **Find nearest MIDI matches** for each emotional cluster centroid
3. **Extract piano melodies** from matched MIDI files
4. **Generate interpolations** between cluster endpoints using MusicVAE
5. **Segment story sentences** into partitions matching interpolation outputs
6. **Map MIDI files** to sentence partitions for synchronized playback

## Custom Directories

This repository includes several custom additions for the emotion-to-music pipeline:

| Directory | Description |
|-----------|-------------|
| [`cluster_nearest_neighbors/`](cluster_nearest_neighbors/) | MusicVAE configuration files and cluster statistics for each story |
| [`data_processing/`](data_processing/) | Utility scripts for MIDI/audio conversion and playback |
| [`partitioning_sentences/`](partitioning_sentences/) | Scripts for segmenting story sentences into equal-length partitions |
| [`sentence_to_midi/`](sentence_to_midi/) | MIDI-to-sentence mapping outputs and scripts |

## Stories

The pipeline has been configured for four stories:

- **carnival** - A carnival-themed narrative
- **lantern** - A lantern-themed narrative  
- **starling_five** - A narrative involving starlings
- **window_blue_curtain** - A narrative with window/curtain imagery

Each story has its own subdirectory in `cluster_nearest_neighbors/` and `sentence_to_midi/` containing configuration and output files.

## Quick Start

### Prerequisites

- Python 3.x with Magenta installed (`pip install magenta`)
- [FluidSynth](https://www.fluidsynth.org/) for MIDI-to-audio conversion
- [FFmpeg](https://ffmpeg.org/) for audio format conversion (optional)

### Running Interpolations

Use the batch script to generate all MusicVAE interpolations:

```bash
run_interps.bat
```

Or run individual interpolations using the JSON config files:

```bash
music_vae_generate --json_config=cluster_nearest_neighbors/carnival/config_1to2.json
```

### Processing Pipeline

1. **Extract piano melodies** from source MIDI files:
   ```bash
   python data_processing/extract_piano_melody.py
   ```

2. **Run MusicVAE interpolations**:
   ```bash
   run_interps.bat
   ```

3. **Segment story sentences** into partitions:
   ```bash
   python partitioning_sentences/segment_story_sentences.py
   ```

4. **Map MIDI files** to sentence partitions:
   ```bash
   python sentence_to_midi/map_midi_to_sentences.py
   ```

## Output Structure

Generated outputs are saved in the `outputs/` directory:

```
outputs/
├── piano_melodies/
│   └── {story}/
│       └── {measure}bar/
│           ├── cluster_{id}.mid        # Extracted melodies
│           └── interpolations/
│               └── {transition}/       # e.g., 1to2, 2to3
│                   └── *.mid           # Interpolated sequences
├── monophonic_piano_2bar/              # 2-bar extractions
└── output_16bar_v1/                    # 16-bar outputs
```

## Configuration Files

Each story has JSON configuration files for MusicVAE interpolation:

```json
{
    "config": "hierdec-mel_16bar",
    "checkpoint_file": "hierdec-mel_16bar/hierdec-mel_16bar.ckpt",
    "mode": "interpolate",
    "input_midi_1": "outputs/piano_melodies/story/16bar/cluster_1.mid",
    "input_midi_2": "outputs/piano_melodies/story/16bar/cluster_2.mid",
    "output_dir": "outputs/piano_melodies/story/16bar/interpolations/1to2",
    "num_outputs": 5,
    "temperature": 0.5
}
```

## Dependencies

Key dependencies added to this project:

- `note_seq` - Note sequence manipulation
- `pretty_midi` - MIDI file operations
- `pygame` - Audio playback
- `mido` - MIDI file parsing
- `mutagen` - Audio metadata (optional)

## Original Magenta

This repository is built on top of Google's Magenta. For the original Magenta documentation, models, and examples, see:

- [Magenta Website](https://magenta.tensorflow.org)
- [Magenta GitHub](https://github.com/magenta/magenta)
- [Magenta.js](https://github.com/tensorflow/magenta-js)

## License

See [LICENSE](LICENSE) for details.
