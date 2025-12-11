#!/usr/bin/env python3
"""
Play audio files (MIDI, WAV, MP3, MP4) with optional measure-based start.

Supports: .mid, .midi, .wav, .mp3, .mp4
Features:
    - Display duration before playback
    - Start MIDI playback from a specific measure (0-indexed)
    
Usage:
    python play_midi_audio.py
    
Configuration:
    - Edit the audio_files list in main() to add files
    - Set START_MEASURE in main() to start from a specific measure (MIDI only)
    
Dependencies:
    - pygame (required)
    - mido (optional, for MIDI duration and measure-based start)
    - mutagen (optional, for audio file duration info)
"""

import sys
import os
import csv
import time
import tempfile
import pygame
try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False
    
try:
    from mutagen import File as MutagenFile
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False


def get_midi_tempo(midi_file):
    """
    Get the tempo (BPM) from a MIDI file.
    
    Args:
        midi_file (str): Path to MIDI file
        
    Returns:
        float: Tempo in BPM, or None if unable to determine
    """
    if not MIDO_AVAILABLE:
        return None
    
    try:
        mid = mido.MidiFile(midi_file)
        
        # Search for tempo in all tracks
        for track in mid.tracks:
            for msg in track:
                if msg.type == 'set_tempo':
                    # Convert microseconds per beat to BPM
                    bpm = mido.tempo2bpm(msg.tempo)
                    return bpm
        
        # If no tempo found, return default (120 BPM)
        return 120.0
        
    except Exception as e:
        return None


def get_midi_time_signature(midi_file):
    """
    Get the time signature from a MIDI file.
    
    Args:
        midi_file (str): Path to MIDI file
        
    Returns:
        tuple: (numerator, denominator) or None if unable to determine
    """
    if not MIDO_AVAILABLE:
        return None
    
    try:
        mid = mido.MidiFile(midi_file)
        
        # Search for time signature in all tracks
        for track in mid.tracks:
            for msg in track:
                if msg.type == 'time_signature':
                    return (msg.numerator, msg.denominator)
        
        # If no time signature found, return default (4/4)
        return (4, 4)
        
    except Exception as e:
        return None


def get_audio_duration(audio_file):
    """
    Get the duration of an audio file in seconds.
    
    Args:
        audio_file (str): Path to the audio file
        
    Returns:
        float: Duration in seconds, or None if unable to determine
    """
    file_ext = os.path.splitext(audio_file)[1].lower()
    
    # For MIDI files, use mido if available
    if file_ext in ('.mid', '.midi'):
        if MIDO_AVAILABLE:
            try:
                mid = mido.MidiFile(audio_file)
                return mid.length
            except Exception as e:
                print(f"Warning: Could not get MIDI duration with mido: {e}")
        else:
            print("Info: Install 'mido' for accurate MIDI duration (pip install mido)")
    
    # For other audio formats, try mutagen
    if MUTAGEN_AVAILABLE:
        try:
            audio = MutagenFile(audio_file)
            if audio is not None and hasattr(audio.info, 'length'):
                return audio.info.length
        except Exception as e:
            print(f"Warning: Could not get duration with mutagen: {e}")
    else:
        if file_ext in ('.wav', '.mp3', '.mp4'):
            print("Info: Install 'mutagen' for duration info (pip install mutagen)")
    
    return None


def format_duration(seconds):
    """
    Format duration in seconds to MM:SS format.
    
    Args:
        seconds (float): Duration in seconds
        
    Returns:
        str: Formatted duration string
    """
    if seconds is None:
        return "Unknown"
    
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"


def get_midi_measures(midi_file):
    """
    Get measure boundaries (in seconds) from a MIDI file.
    
    Args:
        midi_file (str): Path to MIDI file
        
    Returns:
        list: List of measure start times in seconds, or None if unable to parse
    """
    if not MIDO_AVAILABLE:
        return None
    
    try:
        mid = mido.MidiFile(midi_file)
        
        # Find time signature (default to 4/4)
        numerator = 4
        denominator = 4
        
        # Get time signature from first track
        for track in mid.tracks:
            for msg in track:
                if msg.type == 'time_signature':
                    numerator = msg.numerator
                    denominator = msg.denominator
                    break
            if numerator != 4 or denominator != 4:
                break
        
        # Calculate ticks per measure
        ticks_per_beat = mid.ticks_per_beat
        ticks_per_measure = ticks_per_beat * numerator * (4 / denominator)
        
        # Track tempo changes and calculate measure boundaries
        tempo = 500000  # Default tempo (120 BPM)
        current_tick = 0
        current_time = 0.0
        measures = [0.0]  # First measure starts at 0
        
        # Merge all tracks to get tempo changes
        events = []
        for track in mid.tracks:
            tick = 0
            for msg in track:
                tick += msg.time
                if msg.type == 'set_tempo':
                    events.append((tick, msg.tempo))
        
        events.sort()
        
        # Calculate measure times
        tempo_idx = 0
        current_measure_tick = 0
        
        while current_tick < mid.length * mid.ticks_per_beat * 2:  # Some buffer
            next_measure_tick = current_measure_tick + ticks_per_measure
            
            # Check for tempo changes before next measure
            while tempo_idx < len(events) and events[tempo_idx][0] <= next_measure_tick:
                tempo_tick, new_tempo = events[tempo_idx]
                # Add time elapsed at current tempo
                tick_diff = tempo_tick - current_tick
                current_time += mido.tick2second(tick_diff, mid.ticks_per_beat, tempo)
                current_tick = tempo_tick
                tempo = new_tempo
                tempo_idx += 1
            
            # Add time to next measure
            tick_diff = next_measure_tick - current_tick
            current_time += mido.tick2second(tick_diff, mid.ticks_per_beat, tempo)
            current_tick = next_measure_tick
            current_measure_tick = next_measure_tick
            
            measures.append(current_time)
            
            # Stop if we've exceeded the file length
            if current_time > mid.length + 10:  # Add some buffer
                break
        
        return measures
        
    except Exception as e:
        print(f"Warning: Could not parse MIDI measures: {e}")
        return None


def create_midi_from_measure(midi_file, start_measure):
    """
    Create a temporary MIDI file starting from a specific measure.
    
    Args:
        midi_file (str): Path to original MIDI file
        start_measure (int): 0-indexed measure to start from
        
    Returns:
        str: Path to temporary MIDI file, or None if unable to create
    """
    if not MIDO_AVAILABLE:
        print("Warning: mido is required to start from a specific measure")
        return None
    
    try:
        measures = get_midi_measures(midi_file)
        if measures is None or start_measure >= len(measures):
            print(f"Warning: Cannot start from measure {start_measure}")
            return None
        
        start_time = measures[start_measure]
        mid = mido.MidiFile(midi_file)
        
        # First pass: find the active tempo, time signature, and key at start_time
        active_tempo = 500000  # Default
        active_time_sig = None
        active_key_sig = None
        
        for track in mid.tracks:
            current_time = 0.0
            tempo = 500000
            
            for msg in track:
                current_time += mido.tick2second(msg.time, mid.ticks_per_beat, tempo)
                
                if msg.type == 'set_tempo':
                    tempo = msg.tempo
                    if current_time <= start_time:
                        active_tempo = msg.tempo
                
                if msg.type == 'time_signature' and current_time <= start_time:
                    active_time_sig = msg.copy(time=0)
                
                if msg.type == 'key_signature' and current_time <= start_time:
                    active_key_sig = msg.copy(time=0)
                
                if current_time > start_time:
                    break
        
        # Create new MIDI file
        new_mid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat, type=mid.type)
        
        for track_idx, track in enumerate(mid.tracks):
            new_track = mido.MidiTrack()
            current_time = 0.0
            tempo = 500000  # For time calculations
            first_message = True
            
            # Add initial meta messages (tempo, time sig, key sig) to first track
            if track_idx == 0 or mid.type == 1:  # Type 1 = simultaneous tracks
                if active_time_sig:
                    new_track.append(active_time_sig)
                if active_key_sig:
                    new_track.append(active_key_sig)
                if active_tempo != 500000:  # Only add if not default
                    new_track.append(mido.MetaMessage('set_tempo', tempo=active_tempo, time=0))
            
            for msg in track:
                current_time += mido.tick2second(msg.time, mid.ticks_per_beat, tempo)
                
                if msg.type == 'set_tempo':
                    tempo = msg.tempo
                
                # Include messages at or after start time
                if current_time >= start_time:
                    if first_message:
                        # Calculate time from start for first message
                        delta_seconds = current_time - start_time
                        delta_ticks = mido.second2tick(
                            delta_seconds,
                            mid.ticks_per_beat,
                            active_tempo  # Use active tempo at start!
                        )
                        new_msg = msg.copy(time=int(delta_ticks))
                        first_message = False
                    else:
                        new_msg = msg.copy()
                    
                    new_track.append(new_msg)
            
            new_mid.tracks.append(new_track)
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False)
        new_mid.save(temp_file.name)
        temp_file.close()
        
        return temp_file.name
        
    except Exception as e:
        print(f"Warning: Could not create MIDI from measure {start_measure}: {e}")
        import traceback
        traceback.print_exc()
        return None


def play_midi(audio_file, start_measure=0, play_for=None):
    """
    Play an audio file using pygame.
    
    Supports: MIDI (.mid, .midi), WAV (.wav), MP3 (.mp3), MP4 (.mp4)
    
    Args:
        audio_file (str): Path to the audio file to play
        start_measure (int): 0-indexed measure to start playback from (MIDI only)
        play_for (float): Optional duration in seconds to play. If None, plays entire file.
    """
    # Check if file exists
    if not os.path.exists(audio_file):
        print(f"Error: File '{audio_file}' not found. Skipping...")
        return
    
    # Check if file has a supported extension
    supported_formats = ('.mid', '.midi', '.wav', '.mp3', '.mp4')
    file_ext = os.path.splitext(audio_file)[1].lower()
    is_midi = file_ext in ('.mid', '.midi')
    
    if not audio_file.lower().endswith(supported_formats):
        print(f"Warning: '{audio_file}' may not be a supported audio format.")
        print(f"Supported formats: {', '.join(supported_formats)}")
    
    # Get and display duration and measure info
    duration = get_audio_duration(audio_file)
    duration_str = format_duration(duration)
    print(f"Duration: {duration_str}")
    
    # Get and display tempo and time signature for MIDI files
    if is_midi:
        tempo = get_midi_tempo(audio_file)
        if tempo:
            print(f"Tempo: {tempo:.1f} BPM")
        
        time_sig = get_midi_time_signature(audio_file)
        if time_sig:
            print(f"Time Signature: {time_sig[0]}/{time_sig[1]}")
    
    # Handle measure-based start for MIDI files
    temp_file = None
    file_to_play = audio_file
    
    if start_measure > 0:
        if is_midi:
            measures = get_midi_measures(audio_file)
            if measures:
                print(f"Total measures: {len(measures) - 1}")
                print(f"Starting from measure: {start_measure}")
                temp_file = create_midi_from_measure(audio_file, start_measure)
                if temp_file:
                    file_to_play = temp_file
                else:
                    print("Warning: Could not create modified MIDI, playing from beginning")
            else:
                print("Warning: Could not determine measures, playing from beginning")
        else:
            print("Warning: Measure-based start only supported for MIDI files")
    
    # Initialize pygame mixer
    freq = 44100  # Audio CD quality
    bitsize = -16  # Unsigned 16 bit
    channels = 2  # 1 is mono, 2 is stereo
    buffer = 1024  # Number of samples
    pygame.mixer.init(freq, bitsize, channels, buffer)
    
    # Optional: Set volume (0.0 to 1.0)
    pygame.mixer.music.set_volume(0.8)
    
    try:
        # Load the audio file
        print(f"Loading audio file: {os.path.basename(audio_file)}")
        pygame.mixer.music.load(file_to_play)
        
        # Play the audio file
        if play_for:
            print(f"Playing for {play_for}s... (Press Ctrl+C to stop)")
        else:
            print("Playing... (Press Ctrl+C to stop)")
        pygame.mixer.music.play()
        
        # Wait while the music plays
        start_time = time.time()
        while pygame.mixer.music.get_busy():
            elapsed = time.time() - start_time
            
            # Stop if we've played for the specified duration
            if play_for and elapsed >= play_for:
                pygame.mixer.music.stop()
                print(f"\nPlayback stopped after {play_for}s")
                break
            
            time.sleep(0.1)  # Check more frequently for better timing
        else:
            print("\nPlayback completed!")
        
    except KeyboardInterrupt:
        print("\n\nPlayback stopped by user.")
        pygame.mixer.music.stop()
        raise  # Re-raise to allow stopping the entire playlist
    except Exception as e:
        print(f"Error playing audio file: {e}")
        print("Skipping to next file...")
    finally:
        pygame.mixer.quit()
        
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except Exception:
                pass


def main():
    """Main entry point."""
    # Configuration
    # Define list of audio files to play
    # Supports: .mid, .midi, .wav, .mp3, .mp4
    audio_files = []  # List of tuples (audio_file, start_measure)

    # # Read CSV file
    # cluster_data = []
    # with open("cluster_nearest_neighbors/lantern/average_16bar_neighbors.csv", 'r') as f:
    #     csv_reader = csv.DictReader(f)
    #     cluster_data = list(csv_reader)
    
    base_path = "xMidiDataset"
    # for item in cluster_data:
    #     if item["Cluster"].replace('.0', '') == "4":
    #         #audio_files.append((os.path.join(base_path, item["Nearest_MIDI"]), item["Window_Start"]))
    #         audio_files.append((os.path.join("outputs/piano_melodies/carnival/2bar", f"cluster_{item['Cluster'][0]}.mid"), 0))

    # Add the interpolation MIDI file    
    # Sort interpolation files to ensure correct order (000, 001, 002, etc.)
    interpolation_files = sorted(os.listdir("outputs/piano_melodies/window_blue_curtain/2bar"))
    for file in interpolation_files:
        audio_files.append((os.path.join("outputs/piano_melodies/window_blue_curtain/2bar", file), 0))

    # Optional: Set duration limit for faster testing (in seconds)
    # Set to None to play full files
    PLAY_DURATION = 5  # e.g., 10 for 10 seconds, None for full playback
    
    print(f"Playlist: {len(audio_files)} audio file(s) to play\n")
    if PLAY_DURATION:
        print(f"Playing {PLAY_DURATION}s of each track for testing\n")
    print(audio_files)

    try:
        for i, (audio_file, start_measure) in enumerate(audio_files, 1):
            print(f"\n{'='*60}")
            print(f"Track {i}/{len(audio_files)}")
            print(f"{'='*60}")
            play_midi(audio_file, start_measure=int(start_measure), play_for=PLAY_DURATION)
        
        print(f"\n{'='*60}")
        print("All tracks completed!")
        print(f"{'='*60}")
    except KeyboardInterrupt:
        print(f"\n\n{'='*60}")
        print("Playlist stopped by user.")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()

