#!/usr/bin/env python3
"""
Convert MIDI files to WAV audio files.

This script converts a list of MIDI files to WAV format and saves them
to a specified output directory.
"""

import sys
import os
import subprocess
from pathlib import Path


def convert_midi_to_wav(midi_file, output_dir, soundfont, fluidsynth_exe):
    """
    Convert a MIDI file to WAV format using FluidSynth command-line.
    
    Args:
        midi_file (str): Path to the MIDI file to convert
        output_dir (str): Directory to save the WAV file
        soundfont (str): Path to a SoundFont file (.sf2)
        fluidsynth_exe (str): Path to FluidSynth executable
    """
    # Check if file exists
    if not os.path.exists(midi_file):
        print(f"Error: File '{midi_file}' not found. Skipping...")
        return False
    
    # Check if file has .mid or .midi extension
    if not midi_file.lower().endswith(('.mid', '.midi')):
        print(f"Warning: '{midi_file}' may not be a MIDI file. Skipping...")
        return False
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename
    midi_path = Path(midi_file)
    output_filename = midi_path.stem + '.wav'
    output_path = os.path.join(output_dir, output_filename)
    
    try:
        print(f"Converting: {midi_file}")
        print(f"  -> {output_path}")
        
        # Build FluidSynth command
        # Correct order for FluidSynth 2.5.1: fluidsynth -F output.wav soundfont.sf2 input.mid
        cmd = [
            fluidsynth_exe,
            '-F', output_path,        # Output WAV file (must come before soundfont)
            soundfont,                # SoundFont file
            midi_file                 # Input MIDI file
        ]
        
        # Run FluidSynth
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        # Check if output file was created
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"  ✓ Success!\n")
            return True
        else:
            print(f"  ✗ Failed to create output file")
            if result.stderr:
                print(f"  Error: {result.stderr}\n")
            return False
        
    except Exception as e:
        print(f"  ✗ Error converting MIDI file: {e}\n")
        return False


def main():
    """Main entry point."""
    # Define output directory for WAV files
    output_directory = "outputs/mono_piano_2bar_wav_files"
    
    # FluidSynth executable path
    fluidsynth_executable = r"C:\Users\{LAPTOPUSERNAME}\fluidsynth-v2.5.1-win10-x64-glib\fluidsynth-v2.5.1-win10-x64-glib\bin\fluidsynth.exe"
    
    # SoundFont file path
    soundfont_path = "FluidR3_GM/FluidR3_GM.sf2"
    
    # Define list of MIDI files to convert
    midi_files = [
        "outputs/monophonic_piano_2bar/cat-mel_2bar_big_input2-extractions_2025-11-27_135740-000-of-005.mid",
        "outputs/monophonic_piano_2bar/cat-mel_2bar_big_interpolate_2025-11-27_140300-000-of-005.mid",
        "outputs/monophonic_piano_2bar/cat-mel_2bar_big_interpolate_2025-11-27_140300-001-of-005.mid",
        "outputs/monophonic_piano_2bar/cat-mel_2bar_big_interpolate_2025-11-27_140300-002-of-005.mid",
        "outputs/monophonic_piano_2bar/cat-mel_2bar_big_interpolate_2025-11-27_140300-003-of-005.mid",
        "outputs/monophonic_piano_2bar/cat-mel_2bar_big_interpolate_2025-11-27_140300-004-of-005.mid",
        # Add more MIDI files here as needed
    ]
    
    print("="*60)
    print("MIDI to WAV Converter (FluidSynth CLI)")
    print("="*60)
    print(f"Output directory: {output_directory}")
    print(f"Files to convert: {len(midi_files)}")
    print(f"FluidSynth: {fluidsynth_executable}")
    print(f"SoundFont: {soundfont_path}")
    print("="*60)
    print()
    
    # Convert each file
    success_count = 0
    fail_count = 0
    
    for i, midi_file in enumerate(midi_files, 1):
        print(f"[{i}/{len(midi_files)}]")
        if convert_midi_to_wav(midi_file, output_directory, soundfont_path, fluidsynth_executable):
            success_count += 1
        else:
            fail_count += 1
    
    # Print summary
    print("="*60)
    print("Conversion Summary:")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {fail_count}")
    print(f"  Total: {len(midi_files)}")
    print("="*60)


if __name__ == "__main__":
    main()
