import matplotlib.pyplot as plt


def total_variation_distance(counts: dict, baseline_counts: dict, num_shots: int) -> float:
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
    all_keys = set(counts.keys()) | set(baseline_counts.keys())

    # Calculate TVD
    tvd = 0.0
    for key in all_keys:
        p = counts.get(key, 0) / num_shots
        q = baseline_counts.get(key, 0) / num_shots
        tvd += abs(p - q)

    return 0.5 * tvd


def dominant_state_percentile(counts: dict, num_shots: int, top_n: int = 2) -> float:
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
    experiments = ['Baseline', 'Static', 'Dynamic']

    # Calculate metrics
    tvd_values = [
        total_variation_distance(baseline, expected, num_shots),
        total_variation_distance(static_obf, expected, num_shots),
        total_variation_distance(dynamic_obf, expected, num_shots)
    ]

    dominant_values = [
        dominant_state_percentile(baseline, num_shots),
        dominant_state_percentile(static_obf, num_shots),
        dominant_state_percentile(dynamic_obf, num_shots)
    ]

    # Create figure with 2 subplots
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    # Plot 1: TVD bar chart
    tvd_labels = [f'{exp}: {val:.3f}' for exp, val in zip(experiments, tvd_values)]
    axes[0].bar(tvd_labels, tvd_values, color=['green', 'orange', 'red'])
    axes[0].set_ylabel('Total Variation Distance')
    axes[0].set_title(f'TVD from Expected Distribution for {name}')
    axes[0].set_ylim(0, 1)

    # Plot 2: Dominant state percentile bar chart
    dom_labels = [f'{exp}: {val:.1f}%' for exp, val in zip(experiments, dominant_values)]
    axes[1].bar(dom_labels, dominant_values, color=['green', 'orange', 'red'])
    axes[1].set_ylabel('Percentage (%)')
    axes[1].set_title(f'Dominant State Percentile for {name}')
    axes[1].set_ylim(0, 100)

    plt.tight_layout()
    plt.savefig('obfuscation_analysis.png', dpi=150)
    plt.show()

    # Print metrics
    print("\n=== Analysis Results ===")
    for i, exp in enumerate(experiments):
        print(f"{exp}:")
        print(f"  TVD from baseline: {tvd_values[i]:.4f}")
        print(f"  Dominant State: {dominant_values[i]:.2f}%")