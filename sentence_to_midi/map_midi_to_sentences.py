#!/usr/bin/env python3
"""
Map MIDI files to sentence partitions.

This script reads partition summaries and maps interpolation MIDI files
to each partition, creating a JSON mapping file.
"""

import csv
import json
import os
from typing import Dict, List
from collections import defaultdict


def read_summary_csv(summary_path: str) -> Dict[str, List[Dict]]:
    """
    Read the summary CSV and organize by transition.
    
    Args:
        summary_path: Path to the summary CSV file
        
    Returns:
        Dictionary mapping transition to list of partition info
    """
    partitions_by_transition = defaultdict(list)
    
    with open(summary_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            transition = row['Transition']
            partitions_by_transition[transition].append({
                'cluster': row['Cluster'],
                'partition': int(row['Partition']),
                'num_sentences': int(row['Num_Sentences']),
                'word_count': int(row['Word_Count']),
                'sentence_ids': row['Sentence_IDs']
            })
    
    return dict(partitions_by_transition)


def get_midi_files(story_name: str, transition: str) -> List[str]:
    """
    Get sorted list of MIDI files for a transition.
    
    Args:
        story_name: Name of the story
        transition: Transition identifier (e.g., "1to2")
        
    Returns:
        Sorted list of MIDI filenames
    """
    midi_dir = f"outputs/piano_melodies/{story_name}/2bar/interpolations/{transition}"
    
    if not os.path.exists(midi_dir):
        return []
    
    # Get all .mid files and sort them
    midi_files = [f for f in os.listdir(midi_dir) if f.endswith('.mid')]
    midi_files.sort()
    
    return midi_files


def map_midis_to_partitions(partitions: List[Dict], midi_files: List[str]) -> List[Dict]:
    """
    Map MIDI files to partitions (2 per partition, 3 for largest if odd).
    
    Args:
        partitions: List of partition info dictionaries
        midi_files: List of MIDI filenames
        
    Returns:
        List of partition dictionaries with assigned MIDI files
    """
    num_midis = len(midi_files)
    num_partitions = len(partitions)
    
    if num_midis == 0:
        print(f"  Warning: No MIDI files found")
        return []
    
    # Expected: 2 MIDIs per partition (or 3 for one if odd)
    expected_midis = num_partitions * 2
    
    if num_midis != expected_midis and num_midis != expected_midis + 1:
        print(f"  Warning: Expected {expected_midis} or {expected_midis + 1} MIDI files, found {num_midis}")
    
    # Determine if we have an odd number of MIDIs
    has_extra = (num_midis % 2 == 1)
    
    # Find partition with highest word count for extra MIDI
    largest_partition_idx = 0
    if has_extra:
        largest_partition_idx = max(range(len(partitions)), 
                                   key=lambda i: partitions[i]['word_count'])
    
    # Assign MIDIs to partitions
    midi_idx = 0
    result = []
    
    for i, partition in enumerate(partitions):
        # Determine how many MIDIs this partition gets
        num_files = 3 if (has_extra and i == largest_partition_idx) else 2
        
        # Assign MIDI files
        assigned_midis = []
        for _ in range(num_files):
            if midi_idx < len(midi_files):
                assigned_midis.append(midi_files[midi_idx])
                midi_idx += 1
        
        # Create result entry
        result.append({
            'partition': partition['partition'],
            'sentence_ids': partition['sentence_ids'],
            'num_sentences': partition['num_sentences'],
            'word_count': partition['word_count'],
            'midi_files': assigned_midis
        })
    
    return result


def create_midi_mapping(story_name: str):
    """
    Create MIDI to sentence mapping for a story.
    
    Args:
        story_name: Name of the story to process
    """
    summary_path = f"sentence_to_midi/{story_name}/{story_name}_summary.csv"
    
    if not os.path.exists(summary_path):
        print(f"Summary CSV not found: {summary_path}")
        return
    
    print("="*60)
    print(f"Creating MIDI mapping for: {story_name}")
    print("="*60)
    
    # Read partition summary
    partitions_by_transition = read_summary_csv(summary_path)
    
    # Create mapping for each transition
    mapping = {}
    
    for transition, partitions in sorted(partitions_by_transition.items()):
        print(f"\nTransition {transition}:")
        print(f"  Partitions: {len(partitions)}")
        
        # Get MIDI files for this transition
        midi_files = get_midi_files(story_name, transition)
        print(f"  MIDI files: {len(midi_files)}")
        
        if not midi_files:
            print(f"  Skipping (no MIDI files found)")
            continue
        
        # Map MIDIs to partitions
        mapped_partitions = map_midis_to_partitions(partitions, midi_files)
        
        # Add to mapping
        mapping[transition] = mapped_partitions
        
        # Print summary
        for part in mapped_partitions:
            print(f"    Partition {part['partition']}: {len(part['midi_files'])} MIDIs, "
                  f"{part['word_count']} words, sentences {part['sentence_ids']}")
    
    # Save to JSON
    output_path = f"sentence_to_midi/{story_name}/{story_name}_midi_mapping.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Saved mapping to: {output_path}")
    print(f"{'='*60}")


def main():
    """Main entry point."""
    # Process all available stories
    stories = ["carnival", "lantern", "starling_five", "window_blue_curtain"]
    
    for story_name in stories:
        summary_path = f"sentence_to_midi/{story_name}/{story_name}_summary.csv"
        if os.path.exists(summary_path):
            create_midi_mapping(story_name)
            print()
        else:
            print(f"Skipping {story_name}: Summary CSV not found\n")


if __name__ == "__main__":
    main()

