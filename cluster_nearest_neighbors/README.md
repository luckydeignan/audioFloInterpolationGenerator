# Cluster Nearest Neighbors

This directory contains configuration files and statistics for MusicVAE interpolation between emotional cluster endpoints.

## Directory Structure

```
cluster_nearest_neighbors/
├── carnival/
│   ├── config_1to2.json         # MusicVAE config for cluster 1→2 transition
│   ├── config_3to4.json         # MusicVAE config for cluster 3→4 transition
│   ├── carnival_stats.csv       # Cluster statistics (valence/arousal)
│   ├── clustered.csv            # Sentence assignments to clusters
│   ├── cluster_2bar_neighbors.csv   # Nearest MIDI matches (2-bar)
│   └── cluster_16bar_neighbors.csv  # Nearest MIDI matches (16-bar)
├── lantern/
│   ├── config_1to2.json
│   ├── config_2to3.json
│   ├── config_3to4.json
│   ├── lantern_stats.csv
│   ├── cluster_2bar_neighbors.csv
│   └── cluster_16bar_neighbors.csv
├── starling_five/
│   ├── config_1to2.json
│   ├── config_2to3.json
│   └── config_3to4.json
└── window_blue_curtain/
    ├── config_1to2.json
    ├── config_2to3.json
    └── config_3to4.json
```

## Configuration Files

### MusicVAE Config (`config_*.json`)

Each JSON file configures a MusicVAE interpolation run between two cluster endpoints:

```json
{
    "config": "hierdec-mel_16bar",
    "checkpoint_file": "hierdec-mel_16bar/hierdec-mel_16bar.ckpt",
    "mode": "interpolate",
    "input_midi_1": "outputs/piano_melodies/story/16bar/cluster_1.mid",
    "input_midi_2": "outputs/piano_melodies/story/16bar/cluster_2.mid",
    "output_dir": "outputs/piano_melodies/story/16bar/interpolations/1to2",
    "num_outputs": 5,
    "temperature": 0.5,
    "max_batch_size": 8,
    "log": "INFO"
}
```

| Parameter | Description |
|-----------|-------------|
| `config` | MusicVAE model configuration (`hierdec-mel_16bar` or `cat-mel_2bar_big`) |
| `checkpoint_file` | Path to model checkpoint |
| `mode` | Generation mode (`interpolate` for smooth transitions) |
| `input_midi_1` | Starting MIDI file (cluster start) |
| `input_midi_2` | Ending MIDI file (cluster end) |
| `output_dir` | Directory for generated interpolation files |
| `num_outputs` | Number of interpolation steps to generate |
| `temperature` | Sampling temperature (lower = more deterministic) |

### Cluster Statistics (`*_stats.csv`)

Contains emotional cluster information:

| Column | Description |
|--------|-------------|
| `Cluster` | Cluster ID (1-indexed) |
| `Start_ID` | First sentence ID in cluster |
| `End_ID` | Last sentence ID in cluster |
| `Length` | Number of sentences |
| `Valence_Mean` | Mean valence score (0-1, negative→positive) |
| `Valence_Std` | Valence standard deviation |
| `Arousal_Mean` | Mean arousal score (0-1, calm→excited) |
| `Arousal_Std` | Arousal standard deviation |

### Nearest MIDI Neighbors (`cluster_*bar_neighbors.csv`)

Maps each cluster to its nearest MIDI match from the VGMidi dataset:

| Column | Description |
|--------|-------------|
| `Cluster` | Cluster ID |
| `Nearest_MIDI` | Filename of closest MIDI match |
| `Nearest_Piece_Name` | Human-readable piece name |
| `Window_Start` | Starting bar for extraction |
| `Distance` | Euclidean distance in valence-arousal space |

## Usage

### Run All Interpolations

Execute the batch script from the repository root:

```bash
run_interps.bat
```

### Run Single Interpolation

```bash
music_vae_generate --json_config=cluster_nearest_neighbors/carnival/config_1to2.json
```

## Transition Naming Convention

Transitions are named by their cluster endpoints:
- `1to2` = Cluster 1 → Cluster 2
- `2to3` = Cluster 2 → Cluster 3
- `3to4` = Cluster 3 → Cluster 4

Not all stories have all transitions (depends on number of detected clusters).

## Notes

- The `num_outputs` value determines how many interpolation steps are generated
- More outputs = smoother transitions but longer processing time
- Temperature of 0.5 provides good balance between variety and coherence

