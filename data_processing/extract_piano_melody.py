# Extract piano melodies from MIDI files
import note_seq
import csv
import os
from magenta.pipelines import melody_pipelines


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


def get_predominant_time_signature(sequence):
    """
    Determine which time signature is active for the longest duration.
    
    Args:
        sequence: A NoteSequence
        
    Returns:
        tuple: (numerator, denominator) of the predominant time signature
    """
    if not sequence.time_signatures:
        print("No time signatures found, using default: 4/4")
        return (4, 4)  # Default to 4/4
    
    if len(sequence.time_signatures) == 1:
        print("Only one time signature found, using it")
        ts = sequence.time_signatures[0]
        return (ts.numerator, ts.denominator)
    
    # Calculate duration for each time signature
    time_sig_durations = []
    total_time = sequence.total_time
    
    for i, ts in enumerate(sequence.time_signatures):
        start_time = ts.time
        # End time is either the next time signature or the end of the sequence
        if i + 1 < len(sequence.time_signatures):
            end_time = sequence.time_signatures[i + 1].time
        else:
            end_time = total_time
        
        duration = end_time - start_time
        time_sig_durations.append({
            'numerator': ts.numerator,
            'denominator': ts.denominator,
            'duration': duration,
            'start_time': start_time
        })
    
    # Find the time signature with the longest duration
    predominant = max(time_sig_durations, key=lambda x: x['duration'])
    
    print(f"  Time signatures found:")
    for ts in time_sig_durations:
        marker = " <- PREDOMINANT" if ts == predominant else ""
        print(f"    {ts['numerator']}/{ts['denominator']} " +
              f"from {ts['start_time']:.2f}s, duration: {ts['duration']:.2f}s{marker}")
    
    return (predominant['numerator'], predominant['denominator'])


def get_predominant_tempo(sequence):
    """
    Determine which tempo is active for the longest duration.
    
    Args:
        sequence: A NoteSequence
        
    Returns:
        float: QPM (quarters per minute) of the predominant tempo
    """
    if not sequence.tempos:
        print("No tempos found, using default")
        return note_seq.DEFAULT_QUARTERS_PER_MINUTE
    
    if len(sequence.tempos) == 1:
        print("Only one tempo found, using it")
        return sequence.tempos[0].qpm
    
    # Calculate duration for each tempo
    tempo_durations = []
    total_time = sequence.total_time
    
    for i, tempo in enumerate(sequence.tempos):
        start_time = tempo.time
        # End time is either the next tempo or the end of the sequence
        if i + 1 < len(sequence.tempos):
            end_time = sequence.tempos[i + 1].time
        else:
            end_time = total_time
        
        duration = end_time - start_time
        tempo_durations.append({
            'qpm': tempo.qpm,
            'duration': duration,
            'start_time': start_time
        })
    
    # Find the tempo with the longest duration
    predominant = max(tempo_durations, key=lambda x: x['duration'])
    
    print(f"  Tempos found:")
    for tempo in tempo_durations:
        marker = " <- PREDOMINANT" if tempo == predominant else ""
        print(f"    {tempo['qpm']:.2f} BPM " +
              f"from {tempo['start_time']:.2f}s, duration: {tempo['duration']:.2f}s{marker}")
    
    return predominant['qpm']


def extract_piano_melody(test_file, output_file, start_bar=0, num_bars=2):
    """Extract melody from a MIDI file, handling various edge cases.
    
    Args:
        test_file: Path to input MIDI file
        output_file: Path to output MIDI file
        start_bar: Which bar to start extraction from (0-indexed)
        num_bars: Number of bars to extract
    """
    try:
        sequence = note_seq.midi_file_to_note_sequence(test_file)
    except Exception as e:
        print(f"Error loading MIDI file: {e}")
        return False
    
    # Extract the original tempo (QPM = Quarters Per Minute)
    if sequence.tempos:
        original_qpm = sequence.tempos[0].qpm
        print(f"Original tempo: {original_qpm} BPM")
    else:
        original_qpm = note_seq.DEFAULT_QUARTERS_PER_MINUTE
        print(f"No tempo found, using default: {original_qpm} BPM")

    # Try to quantize the sequence
    try:
        quantized = note_seq.quantize_note_sequence(sequence, steps_per_quarter=4)
    except note_seq.MultipleTimeSignatureError as e:
        print(f"Warning: Multiple time signatures detected. Finding predominant one...")
        
        # Get the predominant time signature
        numerator, denominator = get_predominant_time_signature(sequence)
        
        # Replace all time signatures with just the predominant one
        del sequence.time_signatures[:]
        sequence.time_signatures.add(
            numerator=numerator,
            denominator=denominator,
            time=0
        )
        
        print(f"  Using {numerator}/{denominator} time signature")
        
        try:
            quantized = note_seq.quantize_note_sequence(sequence, steps_per_quarter=4)
            print("Successfully quantized after fixing time signatures")
        except note_seq.MultipleTempoError as e2:
            print(f"Warning: Multiple tempos detected after fixing time signatures. Finding predominant one...")
            
            # Get the predominant tempo
            predominant_qpm = get_predominant_tempo(sequence)
            
            # Replace all tempos with just the predominant one
            del sequence.tempos[:]
            sequence.tempos.add(qpm=predominant_qpm, time=0)
            
            # Update the original_qpm to use the predominant tempo
            original_qpm = predominant_qpm
            print(f"  Using {predominant_qpm:.2f} BPM")
            
            try:
                quantized = note_seq.quantize_note_sequence(sequence, steps_per_quarter=4)
                print("Successfully quantized after fixing tempos")
            except Exception as e3:
                print(f"Error: Could not quantize sequence even after fixing: {e3}")
                return False
        except Exception as e2:
            print(f"Error: Could not quantize sequence even after fixing: {e2}")
            return False
    except note_seq.MultipleTempoError as e:
        print(f"Warning: Multiple tempos detected. Finding predominant one...")
        
        # Get the predominant tempo
        predominant_qpm = get_predominant_tempo(sequence)
        
        # Replace all tempos with just the predominant one
        del sequence.tempos[:]
        sequence.tempos.add(qpm=predominant_qpm, time=0)
        
        # Update the original_qpm to use the predominant tempo
        original_qpm = predominant_qpm
        print(f"  Using {predominant_qpm:.2f} BPM")
        
        try:
            quantized = note_seq.quantize_note_sequence(sequence, steps_per_quarter=4)
            print("Successfully quantized after fixing tempos")
        except note_seq.MultipleTimeSignatureError as e2:
            print(f"Warning: Multiple time signatures detected after fixing tempos. Finding predominant one...")
            
            # Get the predominant time signature
            numerator, denominator = get_predominant_time_signature(sequence)
            
            # Replace all time signatures with just the predominant one
            del sequence.time_signatures[:]
            sequence.time_signatures.add(
                numerator=numerator,
                denominator=denominator,
                time=0
            )
            
            print(f"  Using {numerator}/{denominator} time signature")
            
            try:
                quantized = note_seq.quantize_note_sequence(sequence, steps_per_quarter=4)
                print("Successfully quantized after fixing both tempos and time signatures")
            except Exception as e3:
                print(f"Error: Could not quantize sequence even after fixing: {e3}")
                return False
        except Exception as e2:
            print(f"Error: Could not quantize sequence even after fixing: {e2}")
            return False
    except Exception as e:
        print(f"Error quantizing sequence: {e}")
        return False

    # Get time signature
    if quantized.time_signatures:
        numerator = quantized.time_signatures[0].numerator
        denominator = quantized.time_signatures[0].denominator
    else:
        numerator = 4
        denominator = 4
    
    # Calculate time window for the specific bars
    steps_per_quarter = 4
    steps_per_bar = int(steps_per_quarter * numerator * (4.0 / denominator))
    seconds_per_step = 60.0 / original_qpm / steps_per_quarter
    
    # Calculate start and end times
    start_step = start_bar * steps_per_bar
    end_step = (start_bar + num_bars) * steps_per_bar
    start_time = start_step * seconds_per_step
    end_time = end_step * seconds_per_step
    
    print(f"Extracting bars {start_bar} to {start_bar + num_bars - 1} ({num_bars} bars total)")
    print(f"  Time signature: {numerator}/{denominator}")
    print(f"  Steps per bar: {steps_per_bar}")
    print(f"  Time window: {format_duration(start_time)} to {format_duration(end_time)}")
    
    # First, extract just the notes in our time window into a temporary sequence
    temp_sequence = note_seq.NoteSequence()
    temp_sequence.tempos.add().qpm = original_qpm
    temp_sequence.ticks_per_quarter = note_seq.STANDARD_PPQ
    temp_sequence.time_signatures.add(
        numerator=numerator,
        denominator=denominator,
        time=0
    )
    
    notes_in_window = 0
    for note in quantized.notes:
        # Check if note overlaps with our window
        if note.start_time < end_time and note.end_time > start_time:
            new_note = temp_sequence.notes.add()
            # Shift times so the extracted section starts at 0
            new_note.start_time = max(0, note.start_time - start_time)
            new_note.end_time = min(note.end_time - start_time, end_time - start_time)
            new_note.pitch = note.pitch
            new_note.velocity = note.velocity
            new_note.instrument = note.instrument
            new_note.program = note.program
            notes_in_window += 1
    
    if notes_in_window == 0:
        print(f"Warning: No notes found in bars {start_bar}-{start_bar + num_bars - 1}")
        return False
    
    print(f"Found {notes_in_window} notes in window")
    
    # Set the total time for the temporary sequence
    temp_sequence.total_time = end_time - start_time
    
    # Quantize the temp sequence
    temp_quantized = note_seq.quantize_note_sequence(temp_sequence, steps_per_quarter=4)
    
    # Extract monophonic melody using Magenta's melody extraction
    # This ensures MusicVAE will accept it as a single segment
    print(f"Extracting monophonic melody...")
    melodies, stats = melody_pipelines.extract_melodies(
        temp_quantized,
        min_bars=num_bars,
        gap_bars=num_bars,
        max_steps_truncate=None,
        min_unique_pitches=1,
        ignore_polyphonic_notes=True,  # Force monophonic (highest note wins)
        pad_end=True
    )
    
    if not melodies:
        print(f"Warning: Could not extract monophonic melody from bars {start_bar}-{start_bar + num_bars - 1}")
        print(f"  The section may be too sparse or polyphonic.")
        return False
    
    # Take the first/longest melody
    melody = max(melodies, key=lambda m: len(m))
    print(f"Extracted melody with {len(melody)} steps")
    
    # Convert melody back to sequence with original tempo
    output_sequence = melody.to_sequence(qpm=original_qpm)
    
    # Ensure the output has the correct duration
    # Calculate the exact duration for num_bars
    exact_duration = end_time - start_time

    # Truncate notes that extend beyond the exact bar boundary
    for note in output_sequence.notes:
        if note.end_time > exact_duration:
            note.end_time = exact_duration
        # Remove notes that start at or after the boundary
        if note.start_time >= exact_duration:
            output_sequence.notes.remove(note)

    # Ensure the output has the correct duration
    output_sequence.total_time = exact_duration
    print(f"Output duration: {format_duration(output_sequence.total_time)}")
    print(f"Output tempo: {output_sequence.tempos[0].qpm} BPM")
    print(f"Output notes: {len(output_sequence.notes)}")
    
    note_seq.sequence_proto_to_midi_file(output_sequence, output_file)
    print(f"Saved to {output_file}")
    return True

if __name__ == "__main__":
    for measure in [16]:
        for story in ['carnival', 'lantern', 'starling_five', 'window_blue_curtain']:
            if "window_blue_curtain" not in story:
                continue
            csv_path = f"C:/Users/{LAPTOPUSERNAME}/emotional_trajectories_stories/emo_clusters/cluster_outputs/{story}_predictions_output/{measure}_bar_nearest_midi_matches.csv"
            output_dir = f"outputs/piano_melodies/{story}/{measure}bar"
            os.makedirs(output_dir, exist_ok=True)

            # Read CSV file
            cluster_data = []
            with open(csv_path, 'r') as f:
                    csv_reader = csv.DictReader(f)
                    cluster_data = list(csv_reader)

            base_path = "xMidiDataset"
            success_count = 0
            total_count = len(cluster_data)

            for idx, item in enumerate(cluster_data):
                if "2" not in item['Cluster']:
                    continue
                cluster_id = item['Cluster'].replace('.0', '')  # Remove .0 from cluster number
                output_file = os.path.join(output_dir, f"cluster_{cluster_id}.mid")
                midi_path = os.path.join(base_path, item["Nearest_MIDI"])
                
                # Get the starting bar from CSV (convert to 0-indexed integer)
                start_bar = int(item['Window_Start'])
                
                print(f"\n{'='*60}")
                print(f"Processing Cluster {cluster_id}: {item['Nearest_Piece_Name']}")
                print(f"{'='*60}")
                
                if extract_piano_melody(midi_path, output_file, start_bar=start_bar, num_bars=measure):
                    success_count += 1

            print(f"\n{'='*60}")
            print(f"Completed: {success_count} successful extractions")
            print(f"{'='*60}")