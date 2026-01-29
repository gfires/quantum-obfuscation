import matplotlib.pyplot as plt


def total_variation_distance(counts: dict, reference_counts: dict, num_shots: int) -> float:
    """
    Calculate total variation distance between observed distribution and baseline.
    TVD = 0.5 * sum(|p(x) - q(x)|) for all possible outcomes.
    Args:
        counts (dict): Measurement counts from the observed distribution.
        baseline_counts (dict): Measurement counts from the baseline distribution.
        num_shots (int): Total number of shots.
    Returns:
        float: Total variation distance.
    """
    # Get all possible keys from both distributions
    all_keys = set(counts.keys()) | set(reference_counts.keys())

    # Calculate TVD
    tvd = 0.0
    for key in all_keys:
        p = counts.get(key, 0) / num_shots
        q = reference_counts.get(key, 0) / num_shots
        tvd += abs(p - q)

    return 0.5 * tvd


def dominant_state_percentile(counts: dict, num_shots: int, top_n: int = 1) -> float:
    """
    Calculate the percentage of shots in the top N most frequent states.
    Args:
        counts (dict): Measurement counts.
        num_shots (int): Total number of shots.
        top_n (int): Number of top states to consider.
    Returns:
        float: Percentage of shots in the top N states.
    """
    sorted_counts = sorted(counts.values(), reverse=True)
    top_counts = sum(sorted_counts[:top_n])
    return (top_counts / num_shots) * 100


def analyze_results(name: str, expected: dict, baseline: dict, static_obf: dict, static_recovered: dict, dynamic_obf: dict, dynamic_recovered: dict, num_shots: int):
    """
    Analyze and plot results from the three experiments.
    Generates bar charts for TVD and dominant state percentile, plus overlaid PDF.
    Args:
        name (str): Name of the gate being analyzed.
        expected (dict): Expected measurement counts.
        baseline (dict): Counts from baseline simulation.
        static_obf (dict): Counts from static obfuscation simulation.
        static_recovered (dict): Recovered counts from static recovery simulation.
        dynamic_obf (dict): Counts from dynamic obfuscation simulation.
        dynamic_recovered (dict): Recovered counts from dynamic recovery simulation.
        num_shots (int): Number of shots used in each simulation.
    """
    # Define experiment labels
    experiments_4 = ['Expected', 'Baseline', 'Static', 'Dynamic']
    experiments_3 = ['Baseline', 'Static', 'Dynamic']

    # Calculate metrics
    # Plot 1: Recovered distributions TVD (4 bars including Expected)
    recovered_tvd_values = [
        total_variation_distance(baseline, expected, num_shots),
        total_variation_distance(static_recovered, expected, num_shots),
        total_variation_distance(dynamic_recovered, expected, num_shots)
    ]

    # Plot 2: Actual (non-recovered) distributions TVD (3 bars only)
    actual_tvd_values = [
        total_variation_distance(baseline, expected, num_shots),
        total_variation_distance(static_obf, expected, num_shots),
        total_variation_distance(dynamic_obf, expected, num_shots)
    ]

    # Plot 3: Dominant state percentile (4 bars including Expected)
    dominant_values = [
        dominant_state_percentile(expected, num_shots),
        dominant_state_percentile(baseline, num_shots),
        dominant_state_percentile(static_obf, num_shots),
        dominant_state_percentile(dynamic_obf, num_shots)
    ]

    # Create figure with 3 subplots
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Plot 1: Recovered TVD bar chart (3 bars)
    recovered_labels = [f'{exp}: {val:.3f}' for exp, val in zip(experiments_3, recovered_tvd_values)]
    axes[0].bar(recovered_labels, recovered_tvd_values, color=['green', 'orange', 'red'])
    axes[0].set_ylabel('Total Variation Distance')
    axes[0].set_title(f'Recovered Distributions TVD (from Expected) for {name}')
    axes[0].set_ylim(0, 1)
    axes[0].tick_params(axis='x', rotation=15)

    # Plot 2: Actual TVD bar chart (3 bars)
    actual_labels = [f'{exp}: {val:.3f}' for exp, val in zip(experiments_3, actual_tvd_values)]
    axes[1].bar(actual_labels, actual_tvd_values, color=['green', 'orange', 'red'])
    axes[1].set_ylabel('Total Variation Distance')
    axes[1].set_title(f'Actual Distributions TVD (from Expected) for {name}')
    axes[1].set_ylim(0, 1)

    # Plot 3: Dominant state percentile bar chart (4 bars)
    dom_labels = [f'{exp}: {val:.1f}%' for exp, val in zip(experiments_4, dominant_values)]
    axes[2].bar(dom_labels, dominant_values, color=['blue', 'green', 'orange', 'red'])
    axes[2].set_ylabel('Percentage (%)')
    axes[2].set_title(f'Dominant State Percentile (Top-1) for {name}')
    axes[2].set_ylim(0, 100)
    axes[2].tick_params(axis='x', rotation=15)

    plt.tight_layout()
    plt.savefig('obfuscation_analysis.png', dpi=150)
    plt.show()

    # Print metrics
    print("\n=== Analysis Results ===")
    print("\nRecovered Distributions TVD:")
    for i, exp in enumerate(experiments_3):
        print(f"  {exp}: {recovered_tvd_values[i]:.4f}")

    print("\nActual Distributions TVD:")
    for i, exp in enumerate(experiments_3):
        print(f"  {exp}: {actual_tvd_values[i]:.4f}")

    print("\nDominant State Percentile (Top-1):")
    for i, exp in enumerate(experiments_4):
        print(f"  {exp}: {dominant_values[i]:.2f}%")