#!/usr/bin/env python3
"""
Convert all MIDI files in xMidiDataset to MP3 format.

This script:
1. Scans xMidiDataset/ for all .mid files
2. Converts MIDI to WAV using FluidSynth
3. Converts WAV to MP3 using FFmpeg
4. Stores MP3 files in mp3_dataset/
5. Cleans up intermediate WAV files

Dependencies:
    - FluidSynth (installed locally)
    - FFmpeg (must be in PATH or specify full path)
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path


# Configuration
FLUIDSYNTH_EXE = r"C:\Users\{LAPTOPUSERNAME}\fluidsynth-v2.5.1-win10-x64-glib\fluidsynth-v2.5.1-win10-x64-glib\bin\fluidsynth.exe"
SOUNDFONT_PATH = "FluidR3_GM/FluidR3_GM.sf2"
INPUT_DIR = "xMidiDataset"
OUTPUT_DIR = "mp3_dataset"

# FFmpeg settings
FFMPEG_EXE = "ffmpeg"  # Assumes ffmpeg is in PATH
MP3_QUALITY = "2"  # VBR quality (0=best, 9=worst), 2 is ~190kbps


def convert_midi_to_wav(midi_file, wav_file, soundfont, fluidsynth_exe):
    """
    Convert a MIDI file to WAV format using FluidSynth.
    
    Args:
        midi_file (str): Path to the MIDI file
        wav_file (str): Path to output WAV file
        soundfont (str): Path to SoundFont file (.sf2)
        fluidsynth_exe (str): Path to FluidSynth executable
        
    Returns:
        bool: True if conversion succeeded, False otherwise
    """
    try:
        cmd = [
            fluidsynth_exe,
            '-F', wav_file,
            soundfont,
            midi_file
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if os.path.exists(wav_file) and os.path.getsize(wav_file) > 0:
            return True
        else:
            if result.stderr:
                print(f"    FluidSynth error: {result.stderr[:200]}")
            return False
            
    except Exception as e:
        print(f"    FluidSynth exception: {e}")
        return False


def convert_wav_to_mp3(wav_file, mp3_file, ffmpeg_exe=FFMPEG_EXE, quality=MP3_QUALITY):
    """
    Convert a WAV file to MP3 format using FFmpeg.
    
    Args:
        wav_file (str): Path to the WAV file
        mp3_file (str): Path to output MP3 file
        ffmpeg_exe (str): Path to FFmpeg executable
        quality (str): VBR quality setting (0-9, lower is better)
        
    Returns:
        bool: True if conversion succeeded, False otherwise
    """
    try:
        cmd = [
            ffmpeg_exe,
            '-y',  # Overwrite output file if exists
            '-i', wav_file,
            '-codec:a', 'libmp3lame',
            '-qscale:a', quality,
            mp3_file
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if os.path.exists(mp3_file) and os.path.getsize(mp3_file) > 0:
            return True
        else:
            if result.stderr:
                # FFmpeg outputs to stderr even on success, check for actual errors
                if "Error" in result.stderr or "error" in result.stderr:
                    print(f"    FFmpeg error: {result.stderr[:200]}")
            return False
            
    except FileNotFoundError:
        print("    FFmpeg not found. Please install FFmpeg and add it to PATH.")
        return False
    except Exception as e:
        print(f"    FFmpeg exception: {e}")
        return False


def convert_midi_to_mp3(midi_file, output_dir, soundfont, fluidsynth_exe, skip_existing=True):
    """
    Convert a MIDI file to MP3 format.
    
    Args:
        midi_file (str): Path to the MIDI file
        output_dir (str): Directory to save the MP3 file
        soundfont (str): Path to SoundFont file (.sf2)
        fluidsynth_exe (str): Path to FluidSynth executable
        skip_existing (bool): Skip if MP3 already exists
        
    Returns:
        tuple: (success: bool, skipped: bool)
    """
    midi_path = Path(midi_file)
    mp3_filename = midi_path.stem + '.mp3'
    mp3_path = os.path.join(output_dir, mp3_filename)
    
    # Skip if already exists
    if skip_existing and os.path.exists(mp3_path):
        return (True, True)  # Success, but skipped
    
    # Create temporary WAV file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_wav:
        wav_path = tmp_wav.name
    
    try:
        # Step 1: MIDI -> WAV
        if not convert_midi_to_wav(midi_file, wav_path, soundfont, fluidsynth_exe):
            return (False, False)
        
        # Step 2: WAV -> MP3
        if not convert_wav_to_mp3(wav_path, mp3_path):
            return (False, False)
        
        return (True, False)
        
    finally:
        # Clean up temporary WAV file
        if os.path.exists(wav_path):
            try:
                os.unlink(wav_path)
            except Exception:
                pass


def main():
    """Main entry point."""
    # Validate paths
    if not os.path.exists(FLUIDSYNTH_EXE):
        print(f"Error: FluidSynth not found at: {FLUIDSYNTH_EXE}")
        sys.exit(1)
    
    if not os.path.exists(SOUNDFONT_PATH):
        print(f"Error: SoundFont not found at: {SOUNDFONT_PATH}")
        sys.exit(1)
    
    if not os.path.exists(INPUT_DIR):
        print(f"Error: Input directory not found: {INPUT_DIR}")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Find all MIDI files
    midi_files = []
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(('.mid', '.midi')):
            midi_files.append(os.path.join(INPUT_DIR, filename))
    
    midi_files.sort()
    
    if not midi_files:
        print("No MIDI files found in xMidiDataset/")
        sys.exit(0)
    
    # Print header
    print("=" * 70)
    print("MIDI to MP3 Batch Converter")
    print("=" * 70)
    print(f"Input directory:  {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Files to convert: {len(midi_files)}")
    print(f"FluidSynth:       {FLUIDSYNTH_EXE}")
    print(f"SoundFont:        {SOUNDFONT_PATH}")
    print("=" * 70)
    print()
    
    # Convert each file
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    for i, midi_file in enumerate(midi_files, 1):
        filename = os.path.basename(midi_file)
        
        print(f"[{i:3d}/{len(midi_files)}] {filename}")
        
        success, skipped = convert_midi_to_mp3(
            midi_file,
            OUTPUT_DIR,
            SOUNDFONT_PATH,
            FLUIDSYNTH_EXE,
            skip_existing=True
        )
        
        if success:
            if skipped:
                print(f"           -> Skipped (already exists)")
                skip_count += 1
            else:
                print(f"           -> OK")
                success_count += 1
        else:
            print(f"           -> FAILED")
            fail_count += 1
    
    # Print summary
    print()
    print("=" * 70)
    print("Conversion Summary")
    print("=" * 70)
    print(f"  Converted: {success_count}")
    print(f"  Skipped:   {skip_count}")
    print(f"  Failed:    {fail_count}")
    print(f"  Total:     {len(midi_files)}")
    print("=" * 70)
    print(f"\nMP3 files saved to: {os.path.abspath(OUTPUT_DIR)}")


if __name__ == "__main__":
    main()


