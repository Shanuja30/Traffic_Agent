"""
Intersection Optimization Script
================================
This script demonstrates how to use the traffic simulation to optimize
a busy intersection by testing different traffic light timing strategies.
"""

from model import TrafficModel
import pandas as pd
import matplotlib.pyplot as plt

def run_simulation(green_duration, red_duration, spawn_rate, pedestrian_spawn_rate, steps=500):
    """Run a single simulation and return final metrics"""
    model = TrafficModel(
        width=30,
        height=3,
        spawn_rate=spawn_rate,
        green_duration=green_duration,
        red_duration=red_duration,
        pedestrian_spawn_rate=pedestrian_spawn_rate
    )
    
    for i in range(steps):
        model.step()
    
    # Get final metrics
    df = model.datacollector.get_model_vars_dataframe()
    final_row = df.iloc[-1]
    
    return {
        'cars_passed': final_row['CarsPassed'],
        'avg_travel_time': final_row['AvgTravelTime'],
        'avg_waiting_time': final_row['AvgWaitingTime'],
        'queue_length': final_row['QueueLength'],
        'pedestrians_crossed': final_row['PedestriansCrossed'],
        'avg_pedestrian_time': final_row['AvgPedestrianTime'],
        'pedestrian_wait_time': final_row['PedestrianWaitTime'],
        'green_duration': green_duration,
        'red_duration': red_duration
    }

def calculate_score(metrics, baseline, weights=None):
    """
    Calculate a composite score for a strategy.
    Higher score = better performance
    """
    if weights is None:
        # Default weights - adjust based on priorities
        weights = {
            'cars_passed': 0.3,        # Throughput important
            'avg_waiting_time': -0.2,  # Lower is better (negative weight)
            'pedestrians_crossed': 0.25,
            'pedestrian_wait_time': -0.15,
            'avg_travel_time': -0.1
        }
    
    # Normalize metrics (using baseline as reference)
    normalized_metrics = {
        'cars_passed': metrics['cars_passed'] / max(baseline['cars_passed'], 1),
        'avg_waiting_time': metrics['avg_waiting_time'] / max(baseline['avg_waiting_time'], 1),
        'pedestrians_crossed': metrics['pedestrians_crossed'] / max(baseline['pedestrians_crossed'], 1),
        'pedestrian_wait_time': metrics['pedestrian_wait_time'] / max(baseline['pedestrian_wait_time'], 1),
        'avg_travel_time': metrics['avg_travel_time'] / max(baseline['avg_travel_time'], 1)
    }
    
    # Calculate weighted score
    score = sum(
        normalized_metrics[key] * weights[key]
        for key in weights.keys()
    )
    
    return score

def main():
    print("=" * 70)
    print("  INTERSECTION OPTIMIZATION ANALYSIS")
    print("=" * 70)
    
    # Configuration
    spawn_rate = 0.30  # High traffic
    pedestrian_spawn_rate = 0.10  # Many pedestrians
    simulation_steps = 500
    
    # Step 1: Baseline (Current Situation)
    print("\n[Step 1] Establishing baseline performance...")
    baseline = run_simulation(
        green_duration=15,
        red_duration=15,
        spawn_rate=spawn_rate,
        pedestrian_spawn_rate=pedestrian_spawn_rate,
        steps=simulation_steps
    )
    
    print("\n=== BASELINE RESULTS (Current Timing: 15s GREEN / 15s RED) ===")
    print(f"Cars Passed: {baseline['cars_passed']}")
    print(f"Average Car Wait Time: {baseline['avg_waiting_time']:.2f} steps")
    print(f"Average Travel Time: {baseline['avg_travel_time']:.2f} steps")
    print(f"Pedestrians Crossed: {baseline['pedestrians_crossed']}")
    print(f"Average Pedestrian Wait: {baseline['pedestrian_wait_time']:.2f} steps")
    
    # Step 2: Test Different Strategies
    print("\n[Step 2] Testing different timing strategies...")
    strategies = [
        {
            'name': 'Longer Green for Cars',
            'green_duration': 20,
            'red_duration': 10,
            'description': 'Prioritizes car throughput'
        },
        {
            'name': 'Shorter Cycles',
            'green_duration': 10,
            'red_duration': 10,
            'description': 'More frequent signal changes'
        },
        {
            'name': 'Balanced (Longer Red)',
            'green_duration': 12,
            'red_duration': 18,
            'description': 'More time for pedestrians'
        },
        {
            'name': 'Current Baseline',
            'green_duration': 15,
            'red_duration': 15,
            'description': 'Equal priority'
        }
    ]
    
    results = []
    for strategy in strategies:
        print(f"\nTesting: {strategy['name']}...")
        metrics = run_simulation(
            green_duration=strategy['green_duration'],
            red_duration=strategy['red_duration'],
            spawn_rate=spawn_rate,
            pedestrian_spawn_rate=pedestrian_spawn_rate,
            steps=simulation_steps
        )
        
        metrics['strategy'] = strategy['name']
        metrics['description'] = strategy['description']
        results.append(metrics)
    
    # Convert to DataFrame
    results_df = pd.DataFrame(results)
    
    # Step 3: Calculate Scores
    print("\n[Step 3] Calculating optimization scores...")
    results_df['score'] = results_df.apply(
        lambda row: calculate_score(row.to_dict(), baseline), 
        axis=1
    )
    
    # Step 4: Display Results
    print("\n" + "=" * 70)
    print("  COMPARISON OF STRATEGIES")
    print("=" * 70)
    
    display_cols = ['strategy', 'green_duration', 'red_duration', 
                    'cars_passed', 'avg_waiting_time', 
                    'pedestrians_crossed', 'pedestrian_wait_time', 'score']
    
    print(results_df[display_cols].to_string(index=False))
    
    # Calculate improvements
    print("\n" + "=" * 70)
    print("  IMPROVEMENT ANALYSIS")
    print("=" * 70)
    
    for idx, row in results_df.iterrows():
        car_change = ((row['cars_passed'] - baseline['cars_passed']) / max(baseline['cars_passed'], 1)) * 100
        wait_improvement = ((baseline['avg_waiting_time'] - row['avg_waiting_time']) / max(baseline['avg_waiting_time'], 1)) * 100
        ped_change = ((row['pedestrians_crossed'] - baseline['pedestrians_crossed']) / max(baseline['pedestrians_crossed'], 1)) * 100
        
        print(f"\n{row['strategy']}:")
        print(f"  Cars Passed: {car_change:+.1f}% change from baseline")
        print(f"  Car Wait Time: {wait_improvement:+.1f}% improvement")
        print(f"  Pedestrians Crossed: {ped_change:+.1f}% change from baseline")
        print(f"  Overall Score: {row['score']:.3f}")
    
    # Step 5: Find Best Strategy
    best_strategy = results_df.loc[results_df['score'].idxmax()]
    
    print("\n" + "=" * 70)
    print("  RECOMMENDED SOLUTION")
    print("=" * 70)
    print(f"\nBest Strategy: {best_strategy['strategy']}")
    print(f"Configuration: {best_strategy['green_duration']}s GREEN / {best_strategy['red_duration']}s RED")
    print(f"Overall Score: {best_strategy['score']:.3f}")
    
    car_change = ((best_strategy['cars_passed'] - baseline['cars_passed']) / max(baseline['cars_passed'], 1)) * 100
    wait_improvement = ((baseline['avg_waiting_time'] - best_strategy['avg_waiting_time']) / max(baseline['avg_waiting_time'], 1)) * 100
    ped_change = ((best_strategy['pedestrians_crossed'] - baseline['pedestrians_crossed']) / max(baseline['pedestrians_crossed'], 1)) * 100
    
    print(f"\nExpected Improvements vs Baseline:")
    print(f"  Cars Passed: {best_strategy['cars_passed']} ({car_change:+.1f}%)")
    print(f"  Car Wait Time: {best_strategy['avg_waiting_time']:.2f} steps ({wait_improvement:+.1f}% reduction)")
    print(f"  Pedestrians Crossed: {best_strategy['pedestrians_crossed']} ({ped_change:+.1f}%)")
    print(f"  Pedestrian Wait: {best_strategy['pedestrian_wait_time']:.2f} steps")
    
    # Step 6: Visualize Results
    print("\n[Step 4] Generating visualization...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Chart 1: Cars Passed
    axes[0, 0].bar(range(len(results_df)), results_df['cars_passed'], color='blue', alpha=0.7)
    axes[0, 0].axhline(y=baseline['cars_passed'], color='r', linestyle='--', linewidth=2, label='Baseline')
    axes[0, 0].set_title('Cars Passed')
    axes[0, 0].set_ylabel('Count')
    axes[0, 0].set_xticks(range(len(results_df)))
    axes[0, 0].set_xticklabels(results_df['strategy'], rotation=45, ha='right')
    axes[0, 0].legend()
    axes[0, 0].grid(axis='y', alpha=0.3)
    
    # Chart 2: Average Wait Time
    axes[0, 1].bar(range(len(results_df)), results_df['avg_waiting_time'], color='orange', alpha=0.7)
    axes[0, 1].axhline(y=baseline['avg_waiting_time'], color='r', linestyle='--', linewidth=2, label='Baseline')
    axes[0, 1].set_title('Average Car Wait Time')
    axes[0, 1].set_ylabel('Steps')
    axes[0, 1].set_xticks(range(len(results_df)))
    axes[0, 1].set_xticklabels(results_df['strategy'], rotation=45, ha='right')
    axes[0, 1].legend()
    axes[0, 1].grid(axis='y', alpha=0.3)
    
    # Chart 3: Pedestrians Crossed
    axes[1, 0].bar(range(len(results_df)), results_df['pedestrians_crossed'], color='green', alpha=0.7)
    axes[1, 0].axhline(y=baseline['pedestrians_crossed'], color='r', linestyle='--', linewidth=2, label='Baseline')
    axes[1, 0].set_title('Pedestrians Crossed')
    axes[1, 0].set_ylabel('Count')
    axes[1, 0].set_xticks(range(len(results_df)))
    axes[1, 0].set_xticklabels(results_df['strategy'], rotation=45, ha='right')
    axes[1, 0].legend()
    axes[1, 0].grid(axis='y', alpha=0.3)
    
    # Chart 4: Pedestrian Wait Time
    axes[1, 1].bar(range(len(results_df)), results_df['pedestrian_wait_time'], color='yellow', alpha=0.7)
    axes[1, 1].axhline(y=baseline['pedestrian_wait_time'], color='r', linestyle='--', linewidth=2, label='Baseline')
    axes[1, 1].set_title('Average Pedestrian Wait Time')
    axes[1, 1].set_ylabel('Steps')
    axes[1, 1].set_xticks(range(len(results_df)))
    axes[1, 1].set_xticklabels(results_df['strategy'], rotation=45, ha='right')
    axes[1, 1].legend()
    axes[1, 1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('intersection_optimization_results.png', dpi=150, bbox_inches='tight')
    print("  Saved visualization to: intersection_optimization_results.png")
    plt.show()
    
    print("\n" + "=" * 70)
    print("  OPTIMIZATION COMPLETE!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Review the recommended solution above")
    print("2. Check the visualization graph")
    print("3. Adjust weights in calculate_score() function if priorities differ")
    print("4. Run multiple trials for more robust results")
    print("5. Implement recommended timing changes in real-world intersection")

if __name__ == "__main__":
    main()

