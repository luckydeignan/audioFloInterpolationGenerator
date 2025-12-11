# Sentence to MIDI

This directory contains scripts and output data for mapping MIDI interpolation files to story sentence partitions.

## Overview

After generating MIDI interpolations and partitioning sentences, this module creates the final mapping that aligns specific MIDI files with portions of the narrative text.

## Directory Structure

```
sentence_to_midi/
├── map_midi_to_sentences.py      # Mapping script
├── carnival/
│   ├── carnival_summary.csv      # Partition summary
│   ├── carnival_midi_mapping.json # Final MIDI-to-sentence mapping
│   ├── cluster_1to2/
│   │   └── carnival_cluster_1_partitions.csv
│   └── cluster_3to4/
│       └── carnival_cluster_3_partitions.csv
├── lantern/
│   ├── lantern_summary.csv
│   ├── lantern_midi_mapping.json
│   ├── cluster_1to2/
│   ├── cluster_2to3/
│   └── cluster_3to4/
├── starling_five/
│   └── ...
└── window_blue_curtain/
    └── ...
```

## Script

### `map_midi_to_sentences.py`

Creates JSON mapping files that associate MIDI files with sentence partitions.

**Features:**
- Reads partition summaries from `{story}_summary.csv`
- Assigns 2 MIDI files per partition (3 for largest partition if odd total)
- Distributes extra MIDI files to partitions with highest word count
- Outputs structured JSON for downstream use

## Usage

```bash
python sentence_to_midi/map_midi_to_sentences.py
```

## Output Files

### Summary CSV (`{story}_summary.csv`)

Contains partition information for all cluster transitions:

| Column | Description |
|--------|-------------|
| `Cluster` | Cluster ID |
| `Transition` | Transition identifier (e.g., "1to2") |
| `Partition` | Partition number within cluster |
| `Num_Sentences` | Number of sentences in partition |
| `Word_Count` | Total words in partition |
| `Sentence_IDs` | Comma-separated sentence IDs |

### MIDI Mapping JSON (`{story}_midi_mapping.json`)

Maps MIDI files to sentence partitions:

```json
{
  "1to2": [
    {
      "partition": 1,
      "sentence_ids": "0,1,2,3",
      "num_sentences": 4,
      "word_count": 45,
      "midi_files": [
        "interpolate_001.mid",
        "interpolate_002.mid"
      ]
    },
    {
      "partition": 2,
      "sentence_ids": "4,5,6,7,8",
      "num_sentences": 5,
      "word_count": 48,
      "midi_files": [
        "interpolate_003.mid",
        "interpolate_004.mid"
      ]
    }
  ],
  "3to4": [
    ...
  ]
}
```

### Partition CSVs (`cluster_{transition}/{story}_cluster_{id}_partitions.csv`)

Detailed partition data with full sentence text:

```csv
Partition,ID,Text,V_pred,A_pred,Word_Count
1,0,"Once upon a time...",0.75,0.5,4
1,1,"The carnival was bright...",0.82,0.6,5
2,2,"Colors everywhere...",0.78,0.55,3
```

## MIDI Assignment Logic

The script assigns MIDI files to partitions based on these rules:

1. **Base assignment**: 2 MIDI files per partition
2. **Odd total handling**: If total MIDI count is odd, the partition with the highest word count gets 3 files
3. **Sequential assignment**: MIDI files are assigned in sorted order

### Example

Given 7 MIDI files and 3 partitions with word counts [45, 48, 52]:

- Partition 1 (45 words): 2 MIDIs
- Partition 2 (48 words): 2 MIDIs  
- Partition 3 (52 words): 3 MIDIs (largest, gets extra)

## API Usage

```python
from sentence_to_midi.map_midi_to_sentences import create_midi_mapping

# Create mapping for a specific story
create_midi_mapping("carnival")
```

Or use individual functions:

```python
from sentence_to_midi.map_midi_to_sentences import (
    read_summary_csv,
    get_midi_files,
    map_midis_to_partitions
)

# Read partition summary
partitions = read_summary_csv("sentence_to_midi/carnival/carnival_summary.csv")

# Get MIDI files for a transition
midi_files = get_midi_files("carnival", "1to2")

# Map MIDIs to partitions
mapping = map_midis_to_partitions(partitions["1to2"], midi_files)
```

## Notes

- The mapping preserves sentence order for narrative coherence
- MIDI file names are stored as filenames only (not full paths)
- The JSON structure is designed for easy integration with playback systems
- Sentence IDs reference the original clustered CSV from the emotion analysis pipeline

