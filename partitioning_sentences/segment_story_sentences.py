#!/usr/bin/env python3
"""
Segment story sentences from clusters into equal-length partitions.

This script reads cluster statistics and clustered sentence data, then
segments each cluster's sentences into partitions of approximately equal
word count.
"""

import csv
import os
from typing import List, Dict, Tuple


def count_words(text: str) -> int:
    """Count words in a text string."""
    return len(text.split())


def partition_sentences(sentences: List[Dict], num_partitions: int) -> List[List[Dict]]:
    """
    Partition sentences into sequential groups using the linear partition algorithm.
    This minimizes the maximum word count across all partitions using dynamic programming.
    
    Args:
        sentences: List of sentence dictionaries with 'text' field
        num_partitions: Number of partitions to create
        
    Returns:
        List of partitions, where each partition is a list of sentence dicts in sequential order
    """
    if not sentences:
        return []
    
    if num_partitions <= 0:
        raise ValueError("num_partitions must be positive")
    
    # If fewer sentences than partitions, use fewer partitions
    n = len(sentences)
    k = min(num_partitions, n)
    
    if k == 1:
        return [sentences]
    if k == n:
        return [[sent] for sent in sentences]
    
    # Calculate word count for each sentence
    word_counts = [count_words(sent['text']) for sent in sentences]
    
    # Compute prefix sums for quick range sum queries
    prefix_sums = [0]
    for wc in word_counts:
        prefix_sums.append(prefix_sums[-1] + wc)
    
    def range_sum(i, j):
        """Sum of word counts from index i to j (inclusive)"""
        return prefix_sums[j + 1] - prefix_sums[i]
    
    # DP table: dp[i][j] = minimum maximum partition sum for first i sentences using j partitions
    dp = [[float('inf')] * (k + 1) for _ in range(n + 1)]
    dp[0][0] = 0
    
    # Track partition points
    splits = [[0] * (k + 1) for _ in range(n + 1)]
    
    # Fill DP table
    for i in range(1, n + 1):
        for j in range(1, min(i, k) + 1):
            # Try all possible last partition starting points
            for p in range(j - 1, i):
                # Last partition is from p to i-1
                last_partition_sum = range_sum(p, i - 1)
                max_sum = max(dp[p][j - 1], last_partition_sum)
                
                if max_sum < dp[i][j]:
                    dp[i][j] = max_sum
                    splits[i][j] = p
    
    # Backtrack to find partition points
    partition_points = []
    curr = n
    for j in range(k, 0, -1):
        partition_points.append(curr)
        curr = splits[curr][j]
    partition_points.reverse()
    
    # Build partitions
    partitions = []
    start = 0
    for end in partition_points:
        partitions.append(sentences[start:end])
        start = end
    
    return partitions


def segment_single_cluster(clustered_csv: str, cluster_id: str, start_id: int, 
                           end_id: int, num_partitions: int) -> List[List[Dict]]:
    """
    Segment a single cluster into equal-length partitions.
    
    Args:
        clustered_csv: Path to clustered sentences CSV
        cluster_id: ID of the cluster to segment
        start_id: Starting sentence ID for this cluster
        end_id: Ending sentence ID for this cluster
        num_partitions: Number of partitions to create
        
    Returns:
        List of partitions, where each partition is a list of sentence dicts
    """
    # Read all sentences
    all_sentences = []
    with open(clustered_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_sentences = list(reader)
    
    # Extract sentences for this cluster
    cluster_sentences = [
        sent for sent in all_sentences 
        if start_id <= int(sent['ID']) <= end_id
    ]
    
    if not cluster_sentences:
        print(f"Warning: No sentences found for cluster {cluster_id}")
        return []
    
    # Partition the sentences
    partitions = partition_sentences(cluster_sentences, num_partitions)
    
    # Print summary
    print(f"\nCluster {cluster_id} ({len(cluster_sentences)} sentences):")
    total_words = sum(count_words(s['text']) for s in cluster_sentences)
    print(f"  Total words: {total_words}")
    print(f"  Partitions: {len(partitions)}")
    
    for i, partition in enumerate(partitions):
        partition_words = sum(count_words(s['text']) for s in partition)
        print(f"    Partition {i+1}: {len(partition)} sentences, {partition_words} words")
    
    return partitions


def segment_clusters(stats_csv: str, clustered_csv: str, num_partitions: int = 5) -> Dict:
    """
    Segment clusters into equal-length partitions.
    
    Args:
        stats_csv: Path to cluster statistics CSV
        clustered_csv: Path to clustered sentences CSV
        num_partitions: Number of partitions per cluster
        
    Returns:
        Dictionary mapping cluster ID to list of partitions
    """
    # Read cluster statistics
    cluster_stats = []
    with open(stats_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        cluster_stats = list(reader)
    
    # Process each cluster
    results = {}
    
    for cluster_info in cluster_stats:
        cluster_id = cluster_info['Cluster']
        start_id = int(cluster_info['Start_ID'])
        end_id = int(cluster_info['End_ID'])
        
        partitions = segment_single_cluster(
            clustered_csv, cluster_id, start_id, end_id, num_partitions
        )
        
        if partitions:
            results[cluster_id] = partitions
    
    return results


def save_cluster_partitions(partitions: List[List[Dict]], output_dir: str, 
                           story_name: str, cluster_id: str):
    """
    Save a single cluster's partitions to CSV file.
    
    Args:
        partitions: List of partitions for a single cluster
        output_dir: Directory to save output file
        story_name: Name of the story
        cluster_id: ID of the cluster
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Save partition file
    output_file = os.path.join(output_dir, f"{story_name}_cluster_{cluster_id}_partitions.csv")
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Partition', 'ID', 'Text', 'V_pred', 'A_pred', 'Word_Count'])
        
        for part_idx, partition in enumerate(partitions):
            for sent in partition:
                writer.writerow([
                    part_idx + 1,
                    sent['ID'],
                    sent['text'],
                    sent.get('V_pred', ''),
                    sent.get('A_pred', ''),
                    count_words(sent['text'])
                ])
    
    print(f"Saved cluster {cluster_id} partitions to: {output_file}")


def save_partitioned_results(results: Dict, output_dir: str, story_name: str):
    """
    Save partitioned results to CSV files.
    
    Args:
        results: Dictionary from segment_clusters
        output_dir: Directory to save output files
        story_name: Name of the story for output filename
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Save summary file
    summary_path = os.path.join(output_dir, f"{story_name}_partitions_summary.csv")
    with open(summary_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Cluster', 'Partition', 'Num_Sentences', 'Word_Count', 'Sentence_IDs'])
        
        for cluster_id, partitions in sorted(results.items()):
            for part_idx, partition in enumerate(partitions):
                num_sentences = len(partition)
                word_count = sum(count_words(s['text']) for s in partition)
                sentence_ids = ','.join(s['ID'] for s in partition)
                writer.writerow([cluster_id, part_idx + 1, num_sentences, word_count, sentence_ids])
    
    print(f"\nSaved summary to: {summary_path}")
    
    # Save detailed partition files
    for cluster_id, partitions in sorted(results.items()):
        save_cluster_partitions(partitions, output_dir, story_name, cluster_id)


def main():
    """Main entry point."""
    for story_name in ["carnival", "lantern", "starling_five", "window_blue_curtain"]:
        stats_csv = rf"C:\Users\{LAPTOPUSERNAME}\emotional_trajectories_stories\emo_clusters\cluster_outputs\{story_name}_predictions_output\statistics.csv"

        clustered_csv = rf"C:\Users\{LAPTOPUSERNAME}\emotional_trajectories_stories\emo_clusters\cluster_outputs\{story_name}_predictions_output\clustered.csv"
        

        # Check if files exist
        if not os.path.exists(stats_csv) or not os.path.exists(clustered_csv):
            print(f"\nSkipping {story_name}: Required CSV files not found")
            continue
        
        # Read cluster statistics to get cluster IDs
        cluster_stats = []
        with open(stats_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            cluster_stats = list(reader)
        
        # Determine number of partitions for each cluster transition
        # Based on the number of interpolation files
        cluster_transitions = ["1to2", "2to3", "3to4"]
        num_partitions = {}
        
        for transition in cluster_transitions:
            interp_dir = f"outputs/piano_melodies/{story_name}/2bar/interpolations/{transition}"
            if os.path.exists(interp_dir):
                # Count MIDI files and divide by 2 (assuming input/output pairs)
                num_partitions[transition] = len(os.listdir(interp_dir)) // 2
            else:
                print(f"Warning: Directory not found: {interp_dir}")
                raise ValueError(f"Directory not found: {interp_dir}") # Default fallback
        
        print("="*60)
        print(f"Segmenting story: {story_name}")
        print("="*60)
        print(f"Stats CSV: {stats_csv}")
        print(f"Clustered CSV: {clustered_csv}")
        print(f"Number of partitions per transition: {num_partitions}")
        print("="*60)
        
        # Track summary data for this story
        summary_data = []
        
        # Process each cluster transition
        for transition_idx, transition in enumerate(cluster_transitions):
            if transition_idx >= len(cluster_stats):
                break
            
            cluster_info = cluster_stats[transition_idx]
            cluster_id = cluster_info['Cluster']
            start_id = int(cluster_info['Start_ID'])
            end_id = int(cluster_info['End_ID'])
            n_partitions = num_partitions[transition]
            
            # Skip if no partitions (directory was empty or didn't exist)
            if n_partitions <= 0:
                print(f"\nSkipping cluster {cluster_id} (transition {transition}): no interpolation files found")
                continue
            
            # Segment this cluster
            partitions = segment_single_cluster(
                clustered_csv, cluster_id, start_id, end_id, n_partitions
            )
            
            if partitions:
                # Save to sentence_to_midi directory structure
                output_dir = f"sentence_to_midi/{story_name}/cluster_{transition}"
                save_cluster_partitions(partitions, output_dir, story_name, cluster_id)
                
                # Add to summary
                for part_idx, partition in enumerate(partitions):
                    word_count = sum(count_words(s['text']) for s in partition)
                    num_sentences = len(partition)
                    sentence_ids = ','.join(s['ID'] for s in partition)
                    summary_data.append({
                        'Cluster': cluster_id,
                        'Transition': transition,
                        'Partition': part_idx + 1,
                        'Num_Sentences': num_sentences,
                        'Word_Count': word_count,
                        'Sentence_IDs': sentence_ids
                    })
        
        # Save summary file for this story
        if summary_data:
            summary_dir = f"sentence_to_midi/{story_name}"
            os.makedirs(summary_dir, exist_ok=True)
            summary_path = os.path.join(summary_dir, f"{story_name}_summary.csv")
            
            with open(summary_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['Cluster', 'Transition', 'Partition', 
                                                       'Num_Sentences', 'Word_Count', 'Sentence_IDs'])
                writer.writeheader()
                writer.writerows(summary_data)
            
            print(f"\nSaved summary to: {summary_path}")
        
        print("\n" + "="*60)
        print(f"Segmentation complete for {story_name}!")
        print("="*60)


if __name__ == "__main__":
    main()

