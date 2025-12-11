# Partitioning Sentences

This directory contains scripts for segmenting story sentences into equal-length partitions that align with MIDI interpolation outputs.

## Overview

When MusicVAE generates N interpolation steps between two emotional clusters, we need to divide the cluster's sentences into N partitions so each MIDI file can be mapped to a specific portion of the narrative.

## Script

### `segment_story_sentences.py`

Segments cluster sentences into partitions using a dynamic programming algorithm that minimizes the maximum word count across partitions (linear partitioning).

**Algorithm:**
- Uses linear partition algorithm to divide sentences sequentially
- Optimizes for equal word distribution, not sentence count
- Maintains narrative order (no sentence reordering)

**Features:**
- Reads cluster statistics from external CSV files
- Automatically determines partition count from interpolation files
- Outputs partition files for each cluster transition
- Generates summary CSV with partition metadata

## Usage

```bash
python partitioning_sentences/segment_story_sentences.py
```

## Input Files

The script expects:

1. **Statistics CSV** (external):
   ```
   Cluster,Start_ID,End_ID,Length,Valence_Mean,...
   1,0,20,18,0.746,...
   2,18,20,3,0.935,...
   ```

2. **Clustered CSV** (external):
   ```
   ID,text,V_pred,A_pred
   0,"Once upon a time...",0.75,0.5
   1,"The carnival was bright...",0.82,0.6
   ```

3. **Interpolation files** (determines partition count):
   ```
   outputs/piano_melodies/{story}/2bar/interpolations/{transition}/*.mid
   ```

## Output Files

Outputs are saved to `sentence_to_midi/{story}/`:

### Summary CSV (`{story}_summary.csv`)

```csv
Cluster,Transition,Partition,Num_Sentences,Word_Count,Sentence_IDs
1,1to2,1,4,45,"0,1,2,3"
1,1to2,2,5,48,"4,5,6,7,8"
```

### Partition CSVs (`cluster_{transition}/{story}_cluster_{id}_partitions.csv`)

```csv
Partition,ID,Text,V_pred,A_pred,Word_Count
1,0,"Once upon a time...",0.75,0.5,4
1,1,"The carnival was bright...",0.82,0.6,5
2,2,"Colors everywhere...",0.78,0.55,3
```

## Algorithm Details

### Linear Partition Problem

Given N sentences with word counts and K partitions, find sequential partition boundaries that minimize the maximum partition word count.

**Dynamic Programming Solution:**
- `dp[i][j]` = minimum maximum partition sum for first i sentences using j partitions
- Time complexity: O(N² × K)
- Space complexity: O(N × K)

### Example

Sentences: [10, 20, 30, 15, 25] words
Partitions: 3

Optimal split: [10, 20] | [30] | [15, 25]
- Partition 1: 30 words
- Partition 2: 30 words  
- Partition 3: 40 words
- Max = 40 words (minimized)

## Configuration

Edit `main()` to process specific stories:

```python
for story_name in ["carnival", "lantern", "starling_five", "window_blue_curtain"]:
    stats_csv = f"path/to/{story_name}_predictions_output/statistics.csv"
    clustered_csv = f"path/to/{story_name}_predictions_output/clustered.csv"
    # ...
```

## Notes

- Number of partitions is automatically derived from the number of interpolation MIDI files
- If fewer sentences than partitions, creates one sentence per partition
- Maintains sentence order (partitions are sequential segments of the story)

