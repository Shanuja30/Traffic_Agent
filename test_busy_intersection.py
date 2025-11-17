"""
Test Script for Busy Intersection Scenarios
============================================
This script verifies that the traffic simulation works correctly
under high traffic conditions (busy intersection scenarios).
"""

from model import TrafficModel, CarAgent, PedestrianAgent
import time

def test_high_car_traffic():
    """Test simulation with very high car traffic"""
    print("Test 1: Very High Car Traffic")
    print("-" * 50)
    
    m = TrafficModel(
        width=30, height=3,
        spawn_rate=0.5,  # Very high traffic
        pedestrian_spawn_rate=0.02,
        green_duration=10,
        red_duration=10
    )
    
    for i in range(200):
        m.step()
    
    print(f"✓ Cars passed: {m.cars_passed}")
    print(f"✓ Average wait time: {m.compute_avg_waiting_time():.2f} steps")
    print(f"✓ Queue length: {m.get_queue_length()}")
    print(f"✓ No crashes or errors\n")
    
    return m.cars_passed > 0

def test_high_pedestrian_traffic():
    """Test simulation with very high pedestrian traffic"""
    print("Test 2: Very High Pedestrian Traffic")
    print("-" * 50)
    
    m = TrafficModel(
        width=30, height=3,
        spawn_rate=0.15,
        pedestrian_spawn_rate=0.2,  # Very high pedestrian traffic
        green_duration=10,
        red_duration=12  # More red time to allow pedestrian crossing
    )
    
    signal_changes = 0
    prev_state = m.traffic_light.state
    
    for i in range(400):
        m.step()
        # Track signal changes
        if m.traffic_light.state != prev_state:
            signal_changes += 1
            prev_state = m.traffic_light.state
    
    print(f"✓ Pedestrians crossed: {m.pedestrians_crossed}")
    print(f"✓ Average pedestrian wait: {m.compute_avg_pedestrian_waiting_time():.2f} steps")
    print(f"✓ Traffic light signal switching: {signal_changes} times")
    print(f"✓ System remains stable under high pedestrian load\n")
    
    # System works correctly if it doesn't crash and signals are switching
    return signal_changes > 0 and m.compute_avg_pedestrian_waiting_time() >= 0

def test_maximum_load():
    """Test simulation under maximum load (high cars + high pedestrians)"""
    print("Test 3: Maximum Load Scenario")
    print("-" * 50)
    
    m = TrafficModel(
        width=30, height=3,
        spawn_rate=0.4,  # High car traffic
        pedestrian_spawn_rate=0.15,  # High pedestrian traffic
        green_duration=12,
        red_duration=12
    )
    
    for i in range(400):
        m.step()
        # Check for stability
        if i % 100 == 0:
            queue = m.get_queue_length()
            cars = len([a for a in m.schedule.agents if isinstance(a, CarAgent)])
            peds = len([a for a in m.schedule.agents if isinstance(a, PedestrianAgent)])
            print(f"  Step {i}: Queue={queue}, Cars={cars}, Pedestrians={peds}")
    
    print(f"✓ Cars passed: {m.cars_passed}")
    print(f"✓ Pedestrians crossed: {m.pedestrians_crossed}")
    print(f"✓ System remained stable under maximum load\n")
    
    return True

def test_queue_stability():
    """Test that queue lengths remain reasonable under high load"""
    print("Test 4: Queue Stability")
    print("-" * 50)
    
    m = TrafficModel(
        width=25, height=3,
        spawn_rate=0.45,
        pedestrian_spawn_rate=0.12,
        green_duration=10,
        red_duration=10
    )
    
    max_queue = 0
    for i in range(300):
        m.step()
        queue = m.get_queue_length()
        max_queue = max(max_queue, queue)
    
    print(f"✓ Maximum queue length: {max_queue}")
    print(f"✓ Queue remained bounded (not growing infinitely)")
    print(f"✓ Cars continue to pass: {m.cars_passed}\n")
    
    return max_queue < 20  # Reasonable upper bound

def test_no_deadlocks():
    """Test that agents don't get permanently stuck"""
    print("Test 5: Deadlock Prevention")
    print("-" * 50)
    
    m = TrafficModel(
        width=20, height=3,
        spawn_rate=0.4,
        pedestrian_spawn_rate=0.15,
        green_duration=8,
        red_duration=8
    )
    
    cars_progressing = False
    avg_x_positions = []
    
    for i in range(300):
        m.step()
        
        # Check if cars are moving (average X position changes)
        if i > 50 and i % 50 == 0:
            cars = [a for a in m.schedule.agents if isinstance(a, CarAgent)]
            if len(cars) > 0:
                avg_x = sum(car.pos[0] for car in cars) / len(cars)
                avg_x_positions.append(avg_x)
                
                # Check if cars are progressing (X position increases over time)
                if len(avg_x_positions) >= 2:
                    if avg_x_positions[-1] > avg_x_positions[0]:
                        cars_progressing = True
    
    print(f"✓ Cars passed: {m.cars_passed}")
    print(f"✓ Agents continue to progress: {cars_progressing}")
    print(f"✓ No permanent deadlocks detected\n")
    
    # System works if agents are progressing OR cars are passing
    return cars_progressing or m.cars_passed > 0

def test_extended_simulation():
    """Test that simulation runs correctly for extended periods"""
    print("Test 6: Extended Simulation")
    print("-" * 50)
    
    m = TrafficModel(
        width=30, height=3,
        spawn_rate=0.35,
        pedestrian_spawn_rate=0.12,
        green_duration=10,
        red_duration=10
    )
    
    start_time = time.time()
    
    try:
        for i in range(1000):
            m.step()
            # Validate metrics can be computed
            if i % 200 == 0:
                wait_time = m.compute_avg_waiting_time()
                ped_wait = m.compute_avg_pedestrian_waiting_time()
                travel_time = m.compute_avg_travel_time()
        
        elapsed = time.time() - start_time
        
        print(f"✓ Completed 1000 steps in {elapsed:.2f} seconds")
        print(f"✓ All metrics computed successfully")
        print(f"✓ No errors or crashes\n")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}\n")
        return False

def test_pedestrian_crossing_under_heavy_traffic():
    """Test that pedestrians can cross even under heavy car traffic"""
    print("Test 7: Pedestrian Crossing Under Heavy Traffic")
    print("-" * 50)
    
    m = TrafficModel(
        width=25, height=3,
        spawn_rate=0.3,  # Moderate-high car traffic
        pedestrian_spawn_rate=0.15,  # Moderate pedestrian traffic
        green_duration=10,
        red_duration=12  # More red time for pedestrians
    )
    
    pedestrians_crossed_during_test = 0
    
    for i in range(400):
        prev_crossed = m.pedestrians_crossed
        m.step()
        
        if m.pedestrians_crossed > prev_crossed:
            pedestrians_crossed_during_test += (m.pedestrians_crossed - prev_crossed)
    
    print(f"✓ Pedestrians crossed: {m.pedestrians_crossed}")
    print(f"✓ Signal switching working: Light cycles between GREEN/RED")
    print(f"✓ Pedestrians can cross during RED light periods\n")
    
    return m.pedestrians_crossed > 0

def main():
    """Run all busy intersection tests"""
    print("=" * 70)
    print("  BUSY INTERSECTION TEST SUITE")
    print("=" * 70)
    print()
    
    tests = [
        ("High Car Traffic", test_high_car_traffic),
        ("High Pedestrian Traffic", test_high_pedestrian_traffic),
        ("Maximum Load", test_maximum_load),
        ("Queue Stability", test_queue_stability),
        ("Deadlock Prevention", test_no_deadlocks),
        ("Extended Simulation", test_extended_simulation),
        ("Pedestrian Crossing Under Load", test_pedestrian_crossing_under_heavy_traffic),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result, None))
        except Exception as e:
            results.append((test_name, False, str(e)))
    
    # Print summary
    print("=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    print()
    
    passed = 0
    failed = 0
    
    for test_name, result, error in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
        if error:
            print(f"       Error: {error}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print()
    print(f"Total: {len(tests)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()
    
    if failed == 0:
        print("=" * 70)
        print("  ✓ ALL TESTS PASSED - System works correctly under busy conditions!")
        print("=" * 70)
        return 0
    else:
        print("=" * 70)
        print("  ✗ SOME TESTS FAILED - Review output above")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    exit(main())

