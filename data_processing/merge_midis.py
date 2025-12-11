#!/usr/bin/env python
"""Script to concatenate multiple MIDI files into a single MIDI file."""

import argparse
import os
import pretty_midi


def merge_midi_files(midi_paths, output_path, overlap_seconds=0.5):
    """
    Concatenate multiple MIDI files into a single MIDI file with overlap.
    
    Args:
        midi_paths: List of paths to MIDI files to concatenate
        output_path: Path where the merged MIDI file will be saved
        overlap_seconds: Duration (in seconds) to overlap between segments (default: 0.5)
    """
    if not midi_paths:
        raise ValueError("No MIDI files provided")
    
    # Load the first MIDI file as the base
    merged_midi = pretty_midi.PrettyMIDI(midi_paths[0])
    current_end_time = merged_midi.get_end_time()
    
    print(f"Loaded {midi_paths[0]} (duration: {current_end_time:.2f}s)")
    print(f"Overlap between segments: {overlap_seconds:.2f}s")
    
    # Concatenate each subsequent MIDI file
    for midi_path in midi_paths[1:]:
        midi = pretty_midi.PrettyMIDI(midi_path)
        midi_duration = midi.get_end_time()
        print(f"Loading {midi_path} (duration: {midi_duration:.2f}s)")
        
        # Calculate start time with overlap (start earlier than end of previous segment)
        segment_start_time = max(0, current_end_time - overlap_seconds)
        
        # Shift all notes in this MIDI by the segment start time
        for instrument in midi.instruments:
            # Shift all notes
            for note in instrument.notes:
                note.start += segment_start_time
                note.end += segment_start_time
            
            # Shift all control changes
            for control_change in instrument.control_changes:
                control_change.time += segment_start_time
            
            # Shift all pitch bends
            for pitch_bend in instrument.pitch_bends:
                pitch_bend.time += segment_start_time
            
            # Find matching instrument in merged MIDI or create new one
            matching_instrument = None
            for merged_instrument in merged_midi.instruments:
                if (merged_instrument.program == instrument.program and
                    merged_instrument.is_drum == instrument.is_drum):
                    matching_instrument = merged_instrument
                    break
            
            if matching_instrument:
                # Add notes to existing instrument
                matching_instrument.notes.extend(instrument.notes)
                matching_instrument.control_changes.extend(instrument.control_changes)
                matching_instrument.pitch_bends.extend(instrument.pitch_bends)
            else:
                # Add as new instrument
                merged_midi.instruments.append(instrument)
        
        # Update current end time (accounts for overlap)
        current_end_time = segment_start_time + midi_duration
    
    # Save the merged MIDI file
    merged_midi.write(output_path)
    print(f"\nMerged MIDI saved to: {output_path}")
    print(f"Total duration: {merged_midi.get_end_time():.2f}s")
    print(f"Number of instruments: {len(merged_midi.instruments)}")


def main():
    midi_files_one = []

    midi_files_two = []
    interpolation_files = sorted(os.listdir("outputs/piano_melodies/starling_five/2bar/interpolations/1to2/"))
    for idx, file in enumerate(interpolation_files):
        if idx <2:
            midi_files_one.append(os.path.join("outputs/piano_melodies/starling_five/2bar/interpolations/1to2/", file))
        else:
            midi_files_two.append(os.path.join("outputs/piano_melodies/starling_five/2bar/interpolations/1to2/", file))
    print(midi_files_one)
    print(midi_files_two)
    merge_midi_files(midi_files_one, "outputs/piano_melodies/starling_five/2bar/interpolations/1to2/full_sequence_with_interpolation_one.mid", overlap_seconds=0)
    merge_midi_files(midi_files_two, "outputs/piano_melodies/starling_five/2bar/interpolations/1to2/full_sequence_with_interpolation_two.mid", overlap_seconds=0)


if __name__ == '__main__':
    main()

